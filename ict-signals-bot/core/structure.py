"""
Market Structure module — the backbone of ICT confluence.

Provides:
  - swing highs / lows
  - trend bias (HH/HL = bullish, LH/LL = bearish)
  - BOS (Break of Structure) / MSS (Market Structure Shift)
  - liquidity sweep detection (stop hunt)
  - ATR (for SL buffer + volatility)
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Swing:
    kind: str      # "high" or "low"
    price: float
    index: int


def atr(candles: List[dict], period: int = 14) -> float:
    """Average True Range over last `period` candles."""
    if len(candles) < period + 1:
        return 0.0
    trs = []
    for i in range(len(candles) - period, len(candles)):
        h, l = candles[i]["high"], candles[i]["low"]
        pc = candles[i - 1]["close"]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        trs.append(tr)
    return sum(trs) / len(trs) if trs else 0.0


def find_swings(candles: List[dict], strength: int = 3) -> List[Swing]:
    """Return ordered list of swing points."""
    swings = []
    n = len(candles)
    for i in range(strength, n - strength):
        h = candles[i]["high"]
        l = candles[i]["low"]
        is_high = all(candles[i - j]["high"] < h and candles[i + j]["high"] < h
                      for j in range(1, strength + 1))
        is_low = all(candles[i - j]["low"] > l and candles[i + j]["low"] > l
                     for j in range(1, strength + 1))
        if is_high:
            swings.append(Swing("high", h, i))
        if is_low:
            swings.append(Swing("low", l, i))
    return swings


def trend_bias(swings: List[Swing]) -> str:
    """
    Determine bias from last swing highs/lows.
    bullish = higher highs + higher lows
    bearish = lower highs + lower lows
    """
    highs = [s for s in swings if s.kind == "high"]
    lows = [s for s in swings if s.kind == "low"]
    if len(highs) < 2 or len(lows) < 2:
        return "neutral"

    hh = highs[-1].price > highs[-2].price
    hl = lows[-1].price > lows[-2].price
    lh = highs[-1].price < highs[-2].price
    ll = lows[-1].price < lows[-2].price

    if hh and hl:
        return "bullish"
    if lh and ll:
        return "bearish"
    return "neutral"


def last_structure_break(candles: List[dict], swings: List[Swing]):
    """
    Detect most recent BOS/MSS.
    Returns dict {type: 'BOS'|'MSS', side: 'bull'|'bear', index} or None.
    A close beyond the last opposite swing = structure break.
    """
    if not swings:
        return None
    last = candles[-1]["close"]

    recent_highs = [s for s in swings if s.kind == "high"][-3:]
    recent_lows = [s for s in swings if s.kind == "low"][-3:]

    # bullish break: close above most recent swing high
    if recent_highs and last > recent_highs[-1].price:
        return {"type": "BOS", "side": "bull", "level": recent_highs[-1].price}
    # bearish break: close below most recent swing low
    if recent_lows and last < recent_lows[-1].price:
        return {"type": "BOS", "side": "bear", "level": recent_lows[-1].price}
    return None


def detect_liquidity_sweep(candles: List[dict], swings: List[Swing],
                           lookback: int = 10) -> Optional[dict]:
    """
    Liquidity sweep = price wicks beyond a prior swing then closes back inside.
    Bullish sweep (sell-side taken): low pierces a swing low, closes above it.
    Bearish sweep (buy-side taken): high pierces a swing high, closes below it.
    Checks the most recent candles.
    """
    if len(candles) < 3 or not swings:
        return None

    recent_high = max((s for s in swings if s.kind == "high"),
                      key=lambda s: s.index, default=None)
    recent_low = min((s for s in swings if s.kind == "low"),
                     key=lambda s: s.index, default=None)

    # scan last `lookback` candles for a sweep
    for i in range(max(len(candles) - lookback, 1), len(candles)):
        c = candles[i]
        # bullish sweep: wick below swing low, close back above
        if recent_low and c["low"] < recent_low.price and c["close"] > recent_low.price:
            return {"side": "bull", "level": recent_low.price, "index": i}
        # bearish sweep: wick above swing high, close back below
        if recent_high and c["high"] > recent_high.price and c["close"] < recent_high.price:
            return {"side": "bear", "level": recent_high.price, "index": i}
    return None
