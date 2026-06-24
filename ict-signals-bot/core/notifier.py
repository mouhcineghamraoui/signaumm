"""Telegram notifier — sends formatted ICT signals."""

import requests
import logging

log = logging.getLogger("telegram")


class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.api = f"https://api.telegram.org/bot{token}/sendMessage"

    def send(self, text: str) -> bool:
        if not self.token or not self.chat_id:
            log.error("Telegram not configured")
            return False
        try:
            r = requests.post(self.api, json={
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML",
            }, timeout=10)
            if r.status_code != 200:
                log.error("Telegram %s: %s", r.status_code, r.text[:200])
                return False
            return True
        except Exception as e:
            log.error("Telegram failed: %s", e)
            return False

    def send_signal(self, sig: dict, symbol: str, tf: str) -> bool:
        side = sig["side"]
        emoji = "🟢" if side == "BUY" else "🔴"
        arrow = "📈" if side == "BUY" else "📉"
        zone = ""
        try:
            zone = f"\n🎯 Zone: {sig['zone_bot']:.5f} — {sig['zone_top']:.5f}"
        except (KeyError, TypeError, ValueError):
            pass
        msg = (
            f"{emoji} <b>ICT {side} SIGNAL</b> {arrow}\n\n"
            f"📊 Pair: <b>{symbol}</b>\n"
            f"⏱ Timeframe: {tf}\n"
            f"💠 Setup: {sig['type']}\n"
            f"💰 Price: {sig['price']:.5f}"
            f"{zone}\n"
            f"🕐 Zone age: {sig.get('age_bars','?')} bars\n\n"
            f"<i>⚠️ Not financial advice. Verify on chart.</i>"
        )
        return self.send(msg)
