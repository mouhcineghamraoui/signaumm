"""
Configuration — edit pairs, timeframe, and behaviour here.
Secrets come from environment variables (see .env.example).
"""

import os

# ---- Credentials (from environment) ----
TWELVEDATA_KEY   = os.environ.get("TWELVEDATA_KEY", "")
TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ---- Instruments (Twelve Data naming: slash format) ----
PAIRS = [
    "EUR/USD",
    "GBP/USD",
    "XAU/USD",   # gold
    "USD/JPY",
]

# ---- Timeframes ----
TIMEFRAME      = "M15"    # entry timeframe
CANDLE_COUNT   = 200
HTF_TIMEFRAME  = "H4"     # higher timeframe for bias
HTF_COUNT      = 100

# ---- Strategy / detection ----
OB_STRENGTH    = 5
FVG_MIN_SIZE   = 0.0
FRESH_BARS     = 30
SWING_STRENGTH = 3

# ---- Entry / SL / TP ----
RISK_REWARD    = 2.0
SL_ATR_MULT    = 0.5

# =====================================================================
#  MODE — controls how strict the filters are
#  "conservative" : all 3 hard filters required (fewest, strongest signals)
#  "balanced"     : HTF bias + structure required, sweep optional
#  "relaxed"      : HTF bias required only (most signals, weakest)
# =====================================================================
MODE = "balanced"

_MODE_FILTERS = {
    "conservative": dict(REQUIRE_HTF_BIAS=True,  REQUIRE_MSS=True,  REQUIRE_SWEEP=True),
    "balanced":     dict(REQUIRE_HTF_BIAS=True,  REQUIRE_MSS=True,  REQUIRE_SWEEP=False),
    "relaxed":      dict(REQUIRE_HTF_BIAS=True,  REQUIRE_MSS=False, REQUIRE_SWEEP=False),
}
_f = _MODE_FILTERS.get(MODE, _MODE_FILTERS["conservative"])
REQUIRE_HTF_BIAS = _f["REQUIRE_HTF_BIAS"]
REQUIRE_MSS      = _f["REQUIRE_MSS"]
REQUIRE_SWEEP    = _f["REQUIRE_SWEEP"]

# ---- Diagnostics ----
# When True, logs WHY each pair produced no signal (which filter blocked).
# Turn on while tuning, off once happy (keeps logs clean).
DIAGNOSTIC_LOG = True

# ---- Killzone filter ----
USE_KILLZONE = True
KILLZONES    = ("london", "newyork")

# ---- Loop ----
# With HTF caching, HTF fetched once per ~2h instead of every scan.
# M15 fetched fresh each scan. ~4-5 req/scan for 4 pairs.
SCAN_INTERVAL = 300
