"""
Time-based cache for HTF candles.

The higher timeframe (H4) only changes every 4 hours, so re-fetching it
every 5-minute scan wastes API quota. This cache stores HTF data and only
refreshes it after the timeframe's duration has passed.

Cuts request count roughly in half: instead of 2 fetches/pair/scan,
the HTF fetch happens only once per HTF bar.
"""

import time
import logging

log = logging.getLogger("cache")

# how long (seconds) each timeframe stays "fresh" before re-fetch
TF_SECONDS = {
    "M1": 60, "M5": 300, "M15": 900, "M30": 1800,
    "H1": 3600, "H4": 14400, "D": 86400,
}


class CandleCache:
    def __init__(self):
        self._store = {}   # key -> (timestamp, candles)

    def get(self, key: str, max_age: float):
        entry = self._store.get(key)
        if not entry:
            return None
        ts, candles = entry
        if time.time() - ts > max_age:
            return None
        return candles

    def set(self, key: str, candles):
        self._store[key] = (time.time(), candles)


def fetch_cached(feed, cache: CandleCache, symbol: str,
                 timeframe: str, count: int):
    """
    Fetch candles, using cache for slow timeframes.
    Refresh interval = half the TF duration (safety margin to catch new bars).
    """
    tf_dur = TF_SECONDS.get(timeframe, 900)
    max_age = tf_dur * 0.5
    key = f"{symbol}:{timeframe}:{count}"

    cached = cache.get(key, max_age)
    if cached is not None:
        log.debug("cache hit %s", key)
        return cached, True   # (candles, from_cache)

    candles = feed.get_candles(symbol, timeframe, count)
    if candles:
        cache.set(key, candles)
    return candles, False
