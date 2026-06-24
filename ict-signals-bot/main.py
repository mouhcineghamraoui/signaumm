"""
ICT Signals Bot — main loop.
Polls OANDA -> runs ICT engine -> filters by killzone -> sends to Telegram.

Run:  python main.py
"""

import time
import logging
from datetime import datetime, timezone

from config import settings as cfg
from core.feed import TwelveDataFeed
from core.ict_engine import analyze
from core.notifier import TelegramNotifier
from core.killzone import in_killzone, active_killzone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("main")

# de-dup: remember last signal per pair to avoid spamming the same bar
_last_signal_time = {}


def scan_pair(feed, notifier, pair):
    candles = feed.get_candles(pair, cfg.TIMEFRAME, cfg.CANDLE_COUNT)
    if len(candles) < 30:
        log.warning("%s: not enough candles (%d)", pair, len(candles))
        return

    # use only completed candles for stable signals
    candles = [c for c in candles if c.get("complete", True)]

    signals = analyze(
        candles,
        ob_strength=cfg.OB_STRENGTH,
        fvg_min=cfg.FVG_MIN_SIZE,
        fresh_bars=cfg.FRESH_BARS,
    )

    if not signals:
        return

    last_bar_time = candles[-1].get("time", "")

    for sig in signals:
        # killzone filter
        if cfg.USE_KILLZONE and not in_killzone(zones=cfg.KILLZONES):
            log.info("%s %s signal skipped (outside killzone)", pair, sig["side"])
            continue

        # de-dup per pair per bar
        key = f"{pair}:{sig['type']}:{sig['side']}"
        if _last_signal_time.get(key) == last_bar_time:
            continue
        _last_signal_time[key] = last_bar_time

        ok = notifier.send_signal(sig, pair, cfg.TIMEFRAME)
        kz = active_killzone() or "—"
        log.info("%s %s %s signal sent=%s (killzone=%s)",
                 pair, sig["side"], sig["type"], ok, kz)


def main():
    log.info("=== ICT Signals Bot starting ===")

    feed = TwelveDataFeed(cfg.TWELVEDATA_KEY)
    notifier = TelegramNotifier(cfg.TELEGRAM_TOKEN, cfg.TELEGRAM_CHAT_ID)

    # validate credentials
    if not feed.ping():
        log.error("Twelve Data credentials invalid or no connection. Check TWELVEDATA_KEY.")
        return
    log.info("Twelve Data connection OK")

    notifier.send("✅ <b>ICT Bot online</b>\nMonitoring: " +
                  ", ".join(cfg.PAIRS) +
                  f"\nTimeframe: {cfg.TIMEFRAME}")

    while True:
        try:
            kz = active_killzone()
            if cfg.USE_KILLZONE and not kz:
                log.info("Outside killzone — idling")
            else:
                for pair in cfg.PAIRS:
                    scan_pair(feed, notifier, pair)
        except Exception as e:
            log.error("Scan loop error: %s", e)

        time.sleep(cfg.SCAN_INTERVAL)


if __name__ == "__main__":
    main()
