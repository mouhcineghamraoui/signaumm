"""
Analysis Engine — the brain of the bot.

Takes raw zones (OB/FVG) + market structure and applies HARD FILTERS.
Only setups that pass EVERY required condition produce a signal.
Each valid signal comes with Entry, Stop Loss, and Take Profit (fixed R:R).

Conservative confluence stack (ALL must be true):
  1. HTF bias agrees with signal direction        (multi-timeframe)
  2. Entry-TF structure break in signal direction (BOS/MSS)
  3. Liquidity sweep happened before the setup    (stop hunt)
  4. Price is reacting at a fresh OB or FVG zone   (the entry zone)
  5. Signal is inside an active killzone           (handled in main)

This version also returns DIAGNOSTICS so you can see exactly which
filter blocked a setup (helps tune the bot when it gives 0 signals).
"""

from dataclasses import dataclass
from typing import List, Optional

from core.ict_engine import find_order_blocks, find_fvgs
from core.structure import (
    find_swings, trend_bias, last_structure_break,
    detect_liquidity_sweep, atr,
)


@dataclass
class Signal:
    side: str          # BUY / SELL
    setup: str         # which zone type (OB / FVG)
    entry: float
    sl: float
    tp: float
    rr: float
    price: float
    zone_top: float
    zone_bot: float
    bias: str
    reasons: list
    time: str = ""


@dataclass
class Diagnostic:
    """What the engine saw this scan — for logging / tuning."""
    htf_bias: str = "neutral"
    zones_found: int = 0
    candidate_side: str = "none"
    candidate_setup: str = "none"
    structure_break: str = "none"
    sweep: str = "none"
    blocked_by: str = ""        # which filter rejected it
    passed: bool = False

    def summary(self) -> str:
        if self.passed:
            return f"PASS {self.candidate_side} {self.candidate_setup}"
        if self.candidate_side == "none":
            return f"no fresh zone tapped (HTF={self.htf_bias}, {self.zones_found} zones)"
        return (f"blocked={self.blocked_by} "
                f"(cand={self.candidate_side} {self.candidate_setup}, "
                f"HTF={self.htf_bias}, brk={self.structure_break}, sweep={self.sweep})")


def _round(v, digits):
    return round(v, digits)


def analyze_setup(
    ltf_candles: List[dict],
    htf_candles: List[dict],
    rr: float = 2.0,
    ob_strength: int = 5,
    fvg_min: float = 0.0,
    fresh_bars: int = 30,
    sl_atr_mult: float = 0.5,
    swing_strength: int = 3,
    require_sweep: bool = True,
    require_mss: bool = True,
    require_htf_bias: bool = True,
    digits: int = 5,
    return_diagnostic: bool = False,
):
    """
    Run the full confluence check on the LATEST candle.
    Returns Signal or None  (or (Signal|None, Diagnostic) if return_diagnostic).
    """
    diag = Diagnostic()

    def _ret(sig):
        return (sig, diag) if return_diagnostic else sig

    if len(ltf_candles) < 40 or len(htf_candles) < 10:
        diag.blocked_by = "not enough candles"
        return _ret(None)

    last = ltf_candles[-1]
    last_idx = len(ltf_candles) - 1
    price = last["close"]

    # ---------- 1. HTF bias ----------
    htf_swings = find_swings(htf_candles, swing_strength)
    htf_bias = trend_bias(htf_swings)
    diag.htf_bias = htf_bias

    # ---------- 2. LTF structure ----------
    ltf_swings = find_swings(ltf_candles, swing_strength)
    sb = last_structure_break(ltf_candles, ltf_swings)
    diag.structure_break = f"{sb['side']}" if sb else "none"

    # ---------- 3. liquidity sweep ----------
    sweep = detect_liquidity_sweep(ltf_candles, ltf_swings, lookback=12)
    diag.sweep = f"{sweep['side']}" if sweep else "none"

    # ---------- 4. find the reacting zone ----------
    obs = find_order_blocks(ltf_candles, ob_strength)
    fvgs = find_fvgs(ltf_candles, fvg_min)
    zones = obs + fvgs
    diag.zones_found = len(zones)

    candidate = None
    for z in zones:
        if last_idx - z.index > fresh_bars or z.index >= last_idx:
            continue
        if last["low"] <= z.top and last["high"] >= z.bot:
            candidate = z
            break
    if candidate is None:
        diag.blocked_by = "no fresh zone tapped"
        return _ret(None)

    side = "BUY" if candidate.side == "bull" else "SELL"
    diag.candidate_side = side
    diag.candidate_setup = candidate.kind

    # ================= HARD FILTERS =================
    reasons = []

    if require_htf_bias:
        if side == "BUY" and htf_bias != "bullish":
            diag.blocked_by = "HTF bias"
            return _ret(None)
        if side == "SELL" and htf_bias != "bearish":
            diag.blocked_by = "HTF bias"
            return _ret(None)
        reasons.append(f"HTF bias {htf_bias}")

    if require_mss:
        if not sb:
            diag.blocked_by = "no structure break"
            return _ret(None)
        if side == "BUY" and sb["side"] != "bull":
            diag.blocked_by = "structure break direction"
            return _ret(None)
        if side == "SELL" and sb["side"] != "bear":
            diag.blocked_by = "structure break direction"
            return _ret(None)
        reasons.append(f"{sb['type']} {sb['side']}")

    if require_sweep:
        if not sweep:
            diag.blocked_by = "no liquidity sweep"
            return _ret(None)
        if side == "BUY" and sweep["side"] != "bull":
            diag.blocked_by = "sweep direction"
            return _ret(None)
        if side == "SELL" and sweep["side"] != "bear":
            diag.blocked_by = "sweep direction"
            return _ret(None)
        reasons.append("liquidity sweep")

    reasons.append(f"{candidate.kind} reaction")

    # ================= ENTRY / SL / TP =================
    a = atr(ltf_candles, 14)
    buffer = a * sl_atr_mult

    if side == "BUY":
        entry = candidate.top
        sl = candidate.bot - buffer
        risk = entry - sl
        if risk <= 0:
            diag.blocked_by = "invalid risk"
            return _ret(None)
        tp = entry + risk * rr
    else:
        entry = candidate.bot
        sl = candidate.top + buffer
        risk = sl - entry
        if risk <= 0:
            diag.blocked_by = "invalid risk"
            return _ret(None)
        tp = entry - risk * rr

    diag.passed = True
    sig = Signal(
        side=side, setup=candidate.kind,
        entry=_round(entry, digits), sl=_round(sl, digits), tp=_round(tp, digits),
        rr=rr, price=_round(price, digits),
        zone_top=_round(candidate.top, digits), zone_bot=_round(candidate.bot, digits),
        bias=htf_bias, reasons=reasons, time=last.get("time", ""),
    )
    return _ret(sig)
