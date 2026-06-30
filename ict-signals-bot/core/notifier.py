"""Telegram notifier — sends formatted ICT analysis signals with Entry/SL/TP."""

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

    def send_signal(self, sig, symbol: str, tf: str) -> bool:
        """sig is an analysis.Signal dataclass."""
        side = sig.side
        emoji = "🟢" if side == "BUY" else "🔴"
        arrow = "📈" if side == "BUY" else "📉"

        # risk / reward distances (for display)
        if side == "BUY":
            risk = sig.entry - sig.sl
            reward = sig.tp - sig.entry
        else:
            risk = sig.sl - sig.entry
            reward = sig.entry - sig.tp

        reasons = "\n".join(f"   ✅ {r}" for r in sig.reasons)

        msg = (
            f"{emoji} <b>ICT {side} SETUP</b> {arrow}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📊 Pair: <b>{symbol}</b>  |  ⏱ {tf}\n"
            f"💠 Zone: {sig.setup}  |  📐 R:R 1:{sig.rr:.0f}\n\n"
            f"🎯 <b>Entry:</b> <code>{sig.entry}</code>\n"
            f"🛑 <b>Stop Loss:</b> <code>{sig.sl}</code>\n"
            f"✅ <b>Take Profit:</b> <code>{sig.tp}</code>\n\n"
            f"<b>Confluence (all confirmed):</b>\n{reasons}\n\n"
            f"💰 Current: {sig.price}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"<i>⚠️ Not financial advice. Manage your risk.</i>"
        )
        return self.send(msg)
