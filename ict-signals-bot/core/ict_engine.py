"""
ICT Engine — Order Block + Fair Value Gap detection (pure Python).

Concepts:
  - Swing high/low  : pivot points used for market-structure breaks
  - Order Block (OB): last opposite candle before a structure break
  - Fair Value Gap  : 3-candle imbalance (gap between candle1 and candle3)
  - Signal          : price returning into a fresh OB or FVG zone

Input: list of candle dicts {open, high, low, close, time} (oldest -> newest)
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Zone:
    kind: str          # "OB" or "FVG"
    side: str          # "bull" or "bear"
    top: float
    bot: float
    index: int         # bar index where created
    time: str = ""
    mitigated: bool = False


def _is_swing_high(c, i, strength):
    h = c[i]["high"]
    for j in range(1, strength + 1):
        if c[i - j]["high"] >= h or c[i + j]["high"] >= h:
            return False
    return True


def _is_swing_low(c, i, strength):
    l = c[i]["low"]
    for j in range(1, strength + 1):
        if c[i - j]["low"] <= l or c[i + j]["low"] <= l:
            return False
    return True


def find_order_blocks(candles: List[dict], strength: int = 5) -> List[Zone]:
    """Detect OB via swing break of structure."""
    zones: List[Zone] = []
    n = len(candles)
    if n < strength * 2 + 2:
        return zones

    last_swing_high = None
    last_swing_low = None

    for i in range(strength, n - strength):
        if _is_swing_high(candles, i, strength):
            last_swing_high = candles[i]["high"]
        if _is_swing_low(candles, i, strength):
            last_swing_low = candles[i]["low"]

        close = candles[i]["close"]
        prev_close = candles[i - 1]["close"]

        # Bullish BOS: close breaks above last swing high -> find last down candle
        if last_swing_high and close > last_swing_high and prev_close <= last_swing_high:
            for k in range(i - 1, max(i - 15, -1), -1):
                if candles[k]["close"] < candles[k]["open"]:
                    zones.append(Zone("OB", "bull", candles[k]["high"],
                                      candles[k]["low"], k, candles[k].get("time", "")))
                    break

        # Bearish BOS: close breaks below last swing low -> find last up candle
        if last_swing_low and close < last_swing_low and prev_close >= last_swing_low:
            for k in range(i - 1, max(i - 15, -1), -1):
                if candles[k]["close"] > candles[k]["open"]:
                    zones.append(Zone("OB", "bear", candles[k]["high"],
                                      candles[k]["low"], k, candles[k].get("time", "")))
                    break

    return zones


def find_fvgs(candles: List[dict], min_size: float = 0.0) -> List[Zone]:
    """Detect 3-candle Fair Value Gaps."""
    zones: List[Zone] = []
    for i in range(2, len(candles)):
        c0 = candles[i]       # current
        c2 = candles[i - 2]   # two back

        # Bullish FVG: current low > high of 2 bars ago
        if c0["low"] > c2["high"]:
            size = c0["low"] - c2["high"]
            if size >= min_size:
                zones.append(Zone("FVG", "bull", c0["low"], c2["high"],
                                  i, c0.get("time", "")))

        # Bearish FVG: current high < low of 2 bars ago
        if c0["high"] < c2["low"]:
            size = c2["low"] - c0["high"]
            if size >= min_size:
                zones.append(Zone("FVG", "bear", c2["low"], c0["high"],
                                  i, c0.get("time", "")))

    return zones


def check_signals(candles: List[dict], zones: List[Zone],
                  fresh_bars: int = 50) -> List[dict]:
    """
    Signal when the LATEST candle taps into a recent zone.
    Returns list of signal dicts.
    """
    if not candles:
        return []

    last = candles[-1]
    last_idx = len(candles) - 1
    signals = []

    for z in zones:
        if z.mitigated:
            continue
        # only consider reasonably fresh zones
        if last_idx - z.index > fresh_bars:
            continue
        # zone must be older than current candle
        if z.index >= last_idx:
            continue

        # price taps into the zone (overlap)
        if last["low"] <= z.top and last["high"] >= z.bot:
            side = "BUY" if z.side == "bull" else "SELL"
            signals.append({
                "side": side,
                "type": z.kind,
                "zone_top": z.top,
                "zone_bot": z.bot,
                "price": last["close"],
                "time": last.get("time", ""),
                "age_bars": last_idx - z.index,
            })
            z.mitigated = True  # avoid re-firing same zone

    return signals


def analyze(candles: List[dict], ob_strength: int = 5,
            fvg_min: float = 0.0, fresh_bars: int = 50) -> List[dict]:
    """Full pipeline: detect zones + check latest candle for signals."""
    obs  = find_order_blocks(candles, ob_strength)
    fvgs = find_fvgs(candles, fvg_min)
    return check_signals(candles, obs + fvgs, fresh_bars)
