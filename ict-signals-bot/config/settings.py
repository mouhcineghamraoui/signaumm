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

# ---- Timeframes ----
TIMEFRAME      = "M15"    # entry timeframe
CANDLE_COUNT   = 200
HTF_TIMEFRAME  = "H4"     # higher timeframe for bias
HTF_COUNT      = 100

# ---- Strategy / detection ----
OB_STRENGTH    = 5        # swing strength for Order Blocks
FVG_MIN_SIZE   = 0.0      # min FVG size (0 = any)
FRESH_BARS     = 30       # only signal on zones newer than this
SWING_STRENGTH = 3        # swing detection for structure/liquidity

# ---- Entry / SL / TP ----
RISK_REWARD    = 2.0      # fixed R:R (1:2). Set 3.0 for 1:3
SL_ATR_MULT    = 0.5      # SL buffer = ATR * this

# ---- HARD FILTERS (conservative: all True) ----
# Every True condition is MANDATORY. A setup failing any one = no signal.
REQUIRE_HTF_BIAS = True   # HTF trend must agree with signal direction
REQUIRE_MSS      = True   # structure break must confirm direction
REQUIRE_SWEEP    = True   # liquidity sweep must precede the setup

# ---- Killzone filter ----
USE_KILLZONE = True
KILLZONES    = ("london", "newyork")

# ---- Loop ----
# Now 2 requests per pair (LTF + HTF). 4 pairs = 8 req/scan.
# Free tier 8/min + throttle -> one scan ~70s. 300s interval is safe.
SCAN_INTERVAL = 300
