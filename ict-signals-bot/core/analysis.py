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

Entry / SL / TP:
  - Entry : edge of the zone facing price
  - SL    : far side of the zone + ATR buffer
  - TP    : Entry +/- (risk * RR)   with fixed RR (e.g. 2.0)
"""

from dataclasses import dataclass, asdict
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
    price: float       # current price
    zone_top: float
    zone_bot: float
    bias: str
    reasons: list      # confluence reasons passed
    time: str = ""


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
) -> Optional[Signal]:
    """
    Run the full conservative confluence check on the LATEST candle.
    Returns a Signal only if ALL required filters pass, else None.
    """
    if len(ltf_candles) < 40 or len(htf_candles) < 10:
        return None

    last = ltf_candles[-1]
    last_idx = len(ltf_candles) - 1
    price = last["close"]

    # ---------- 1. HTF bias ----------
    htf_swings = find_swings(htf_candles, swing_strength)
    htf_bias = trend_bias(htf_swings)

    # ---------- 2. LTF structure ----------
    ltf_swings = find_swings(ltf_candles, swing_strength)
    sb = last_structure_break(ltf_candles, ltf_swings)

    # ---------- 3. liquidity sweep ----------
    sweep = detect_liquidity_sweep(ltf_candles, ltf_swings, lookback=12)

    # ---------- 4. find the reacting zone ----------
    obs = find_order_blocks(ltf_candles, ob_strength)
    fvgs = find_fvgs(ltf_candles, fvg_min)
    zones = obs + fvgs

    # determine candidate direction from a fresh zone the price is tapping
    candidate = None
    for z in zones:
        if last_idx - z.index > fresh_bars or z.index >= last_idx:
            continue
        if last["low"] <= z.top and last["high"] >= z.bot:
            candidate = z
            break
    if candidate is None:
        return None

    side = "BUY" if candidate.side == "bull" else "SELL"

    # ================= HARD FILTERS =================
    reasons = []

    # Filter 1: HTF bias must agree
    if require_htf_bias:
        if side == "BUY" and htf_bias != "bullish":
            return None
        if side == "SELL" and htf_bias != "bearish":
            return None
        reasons.append(f"HTF bias {htf_bias}")

    # Filter 2: structure break must agree
    if require_mss:
        if not sb:
            return None
        if side == "BUY" and sb["side"] != "bull":
            return None
        if side == "SELL" and sb["side"] != "bear":
            return None
        reasons.append(f"{sb['type']} {sb['side']}")

    # Filter 3: liquidity sweep must agree
    if require_sweep:
        if not sweep:
            return None
        if side == "BUY" and sweep["side"] != "bull":
            return None
        if side == "SELL" and sweep["side"] != "bear":
            return None
        reasons.append("liquidity sweep")

    reasons.append(f"{candidate.kind} reaction")

    # ================= ENTRY / SL / TP =================
    a = atr(ltf_candles, 14)
    buffer = a * sl_atr_mult

    if side == "BUY":
        entry = candidate.top          # enter at top edge of zone
        sl = candidate.bot - buffer    # stop below zone
        risk = entry - sl
        if risk <= 0:
            return None
        tp = entry + risk * rr
    else:  # SELL
        entry = candidate.bot          # enter at bottom edge of zone
        sl = candidate.top + buffer    # stop above zone
        risk = sl - entry
        if risk <= 0:
            return None
        tp = entry - risk * rr

    return Signal(
        side=side,
        setup=candidate.kind,
        entry=_round(entry, digits),
        sl=_round(sl, digits),
        tp=_round(tp, digits),
        rr=rr,
        price=_round(price, digits),
        zone_top=_round(candidate.top, digits),
        zone_bot=_round(candidate.bot, digits),
        bias=htf_bias,
        reasons=reasons,
        time=last.get("time", ""),
    )
