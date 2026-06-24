"""
Configuration — edit pairs, timeframe, and behaviour here.
Secrets come from environment variables (see .env.example).
"""

import os

# ---- Credentials (from environment) ----
TWELVEDATA_KEY   = os.environ.get("TWELVEDATA_KEY", "7f0b765e4400433192f986762d11a589")

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "8853131432:AAENR3xXdfZAy56wqTX8D0GooApIlpll-Qw")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1544456085")

# ---- Instruments (Twelve Data naming: slash format) ----
PAIRS = [
    "EUR/USD",
    "GBP/USD",
    "XAU/USD",   # gold
    "USD/JPY",
]

# ---- Strategy settings ----
TIMEFRAME    = "M15"     # M1 M5 M15 M30 H1 H4 D
CANDLE_COUNT = 200       # how many candles to fetch each scan
OB_STRENGTH  = 5         # swing strength for Order Blocks
FVG_MIN_SIZE = 0.0       # min FVG size (instrument units; 0 = any)
FRESH_BARS   = 50        # only signal on zones newer than this many bars

# ---- Filters ----
USE_KILLZONE = True              # only signal during London/NY killzones
KILLZONES    = ("london", "newyork")

# ---- Loop ----
# Free tier = 8 req/min. With 4 pairs + throttle, one full scan ~= 35s.
# Scanning once per closed M15 candle is plenty; 300s keeps us well under quota.
SCAN_INTERVAL = 300      # seconds between full scans
