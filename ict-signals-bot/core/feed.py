"""
Twelve Data feed — free real-time forex/crypto data.
No broker account, no geographic restriction.

Get free API key:  https://twelvedata.com/apikey  (just an email)
Free plan: 800 requests/day, 8 req/min — enough for a few pairs on M15.
"""

import requests
import logging
import time

log = logging.getLogger("twelvedata")

BASE = "https://api.twelvedata.com"

# map our internal granularity -> Twelve Data interval strings
TF_MAP = {
    "M1": "1min", "M5": "5min", "M15": "15min", "M30": "30min",
    "H1": "1h", "H4": "4h", "D": "1day",
}


class TwelveDataFeed:
    def __init__(self, apikey: str):
        self.apikey = apikey
        self.session = requests.Session()
        self._last_call = 0.0
        self._min_gap = 8.0  # seconds between calls (free tier: 8/min)

    def _throttle(self):
        """Respect free-tier rate limit (8 req/min)."""
        elapsed = time.time() - self._last_call
        if elapsed < self._min_gap:
            time.sleep(self._min_gap - elapsed)
        self._last_call = time.time()

    def get_candles(self, instrument: str, granularity: str = "M15", count: int = 200):
        """
        instrument : e.g. 'EUR/USD', 'XAU/USD', 'BTC/USD'  (slash format)
        granularity: M1 M5 M15 M30 H1 H4 D
        Returns list of dicts (oldest -> newest):
          {time, open, high, low, close, volume, complete}
        """
        interval = TF_MAP.get(granularity, "15min")
        self._throttle()
        url = f"{BASE}/time_series"
        params = {
            "symbol": instrument,
            "interval": interval,
            "outputsize": count,
            "apikey": self.apikey,
            "format": "JSON",
            "timezone": "UTC",
        }
        try:
            r = self.session.get(url, params=params, timeout=15)
            data = r.json()
            if data.get("status") == "error":
                log.error("TwelveData error for %s: %s", instrument, data.get("message"))
                return []
            values = data.get("values", [])
            if not values:
                log.warning("No data for %s", instrument)
                return []
            # API returns newest-first -> reverse to oldest-first
            out = []
            for v in reversed(values):
                out.append({
                    "time":   v["datetime"],
                    "open":   float(v["open"]),
                    "high":   float(v["high"]),
                    "low":    float(v["low"]),
                    "close":  float(v["close"]),
                    "volume": int(float(v.get("volume", 0) or 0)),
                    "complete": True,  # TD returns closed candles
                })
            return out
        except Exception as e:
            log.error("TwelveData request failed: %s", e)
            return []

    def get_price(self, instrument: str):
        candles = self.get_candles(instrument, "M1", 1)
        return candles[-1]["close"] if candles else None

    def ping(self) -> bool:
        c = self.get_candles("EUR/USD", "M15", 2)
        return len(c) > 0
