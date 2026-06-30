"""
ICT Analysis Bot — main loop (with diagnostics + HTF caching + mode control).

Polls Twelve Data (HTF cached + LTF fresh) -> runs confluence analysis
-> killzone filter -> sends high-quality signals with Entry/SL/TP to Telegram.

When DIAGNOSTIC_LOG is on, logs WHY each pair gave no signal — so you can
see exactly which filter is blocking and tune MODE accordingly.

Run:  python main.py
"""

import time
import logging

from config import settings as cfg
from core.feed import TwelveDataFeed
from core.cache import CandleCache, fetch_cached
from core.analysis import analyze_setup
from core.notifier import TelegramNotifier
from core.killzone import in_killzone, active_killzone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("main")

_last_signal_time = {}
_cache = CandleCache()


def _digits(symbol: str) -> int:
    if "JPY" in symbol:
        return 3
    if "XAU" in symbol or "XAG" in symbol:
        return 2
    return 5


def scan_pair(feed, notifier, pair):
    # LTF fresh every scan; HTF served from cache when still valid
    ltf = feed.get_candles(pair, cfg.TIMEFRAME, cfg.CANDLE_COUNT)
    htf, from_cache = fetch_cached(feed, _cache, pair, cfg.HTF_TIMEFRAME, cfg.HTF_COUNT)

    if len(ltf) < 40 or len(htf) < 10:
        log.warning("%s: not enough candles (ltf=%d htf=%d)", pair, len(ltf), len(htf))
        return

    sig, diag = analyze_setup(
        ltf_candles=ltf,
        htf_candles=htf,
        rr=cfg.RISK_REWARD,
        ob_strength=cfg.OB_STRENGTH,
        fvg_min=cfg.FVG_MIN_SIZE,
        fresh_bars=cfg.FRESH_BARS,
        sl_atr_mult=cfg.SL_ATR_MULT,
        swing_strength=cfg.SWING_STRENGTH,
        require_sweep=cfg.REQUIRE_SWEEP,
        require_mss=cfg.REQUIRE_MSS,
        require_htf_bias=cfg.REQUIRE_HTF_BIAS,
        digits=_digits(pair),
        return_diagnostic=True,
    )

    htf_tag = "cached" if from_cache else "fresh"

    if not sig:
        if cfg.DIAGNOSTIC_LOG:
            log.info("%s [%s HTF] no signal — %s", pair, htf_tag, diag.summary())
        return

    # killzone filter
    if cfg.USE_KILLZONE and not in_killzone(zones=cfg.KILLZONES):
        log.info("%s %s setup ready but outside killzone — skipped", pair, sig.side)
        return

    # de-dup per pair per bar
    key = f"{pair}:{sig.side}:{sig.setup}"
    if _last_signal_time.get(key) == sig.time:
        return
    _last_signal_time[key] = sig.time

    ok = notifier.send_signal(sig, pair, cfg.TIMEFRAME)
    kz = active_killzone() or "—"
    log.info("%s ✅ %s %s SIGNAL sent=%s (entry=%s sl=%s tp=%s, kz=%s)",
             pair, sig.side, sig.setup, ok, sig.entry, sig.sl, sig.tp, kz)


def main():
    log.info("=== ICT Analysis Bot starting (mode=%s) ===", cfg.MODE)

    feed = TwelveDataFeed(cfg.TWELVEDATA_KEY)
    notifier = TelegramNotifier(cfg.TELEGRAM_TOKEN, cfg.TELEGRAM_CHAT_ID)

    if not feed.ping():
        log.error("Twelve Data credentials invalid or no connection. Check TWELVEDATA_KEY.")
        return
    log.info("Twelve Data connection OK")

    notifier.send(
        "✅ <b>ICT Analysis Bot online</b>\n"
        f"Pairs: {', '.join(cfg.PAIRS)}\n"
        f"Entry TF: {cfg.TIMEFRAME}  |  Bias TF: {cfg.HTF_TIMEFRAME}\n"
        f"Mode: <b>{cfg.MODE}</b> (bias={cfg.REQUIRE_HTF_BIAS}, "
        f"mss={cfg.REQUIRE_MSS}, sweep={cfg.REQUIRE_SWEEP})\n"
        f"R:R 1:{cfg.RISK_REWARD:.0f}"
    )

    scan_count = 0
    while True:
        try:
            kz = active_killzone()
            if cfg.USE_KILLZONE and not kz:
                log.info("Outside killzone — idling (London 07-10 UTC, NY 12-15 UTC)")
            else:
                scan_count += 1
                log.info("--- Scan #%d (killzone: %s) ---", scan_count, kz or "off")
                for pair in cfg.PAIRS:
                    scan_pair(feed, notifier, pair)
        except Exception as e:
            log.error("Scan loop error: %s", e)

        time.sleep(cfg.SCAN_INTERVAL)


if __name__ == "__main__":
    main()
