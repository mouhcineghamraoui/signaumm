# ICT Signals Bot — Python + Twelve Data + Telegram

Système automatique **bla TradingView, bla broker, bla restriction géographique**: kay9ra prix real-time mn Twelve Data (free API key b email ghir), kay-détecta ICT setups (Order Blocks + FVG) f Python, kay-filtri b killzones (London/NY), w kaysifet signals l-Telegram.

> ⚡ **3lach Twelve Data w machi OANDA?** OANDA kayrefdo l-applications mn chi blدان (Maroc inclus). Twelve Data = sign-up b email ghir, walو KYC, walو broker, kaykhdem mن ay blassa.

```
Twelve Data API (free, real-time forex)
      │  Python kay-fetchي candles
      ▼
ICT Engine (OB + FVG detection)
      │
Killzone filter (London / NY ghir)
      │  signal valide
      ▼
Telegram Bot → chat dyalek
```

---

## 📁 Structure

```
ict-python/
├── main.py                 ← l-loop principal
├── config/settings.py      ← pairs, timeframe, réglages (BEDDEL HNA)
├── core/
│   ├── feed.py             ← Twelve Data feed
│   ├── ict_engine.py       ← OB + FVG detection
│   ├── notifier.py         ← Telegram
│   └── killzone.py         ← session filter
├── requirements.txt
├── .env.example
└── Procfile                ← deployment
```

---

## 🚀 Setup — 4 étapes

### 1️⃣ Twelve Data API key (free, mن ay blassa)

1. Sir l **twelvedata.com/apikey**
2. Sign-up b email (walو broker, walو restriction)
3. Copy l-**API key** mn dashboard

> 💡 Free plan = 800 request/jour, 8/minute. Kafي l-4 pairs 3la M15.

### 2️⃣ Telegram bot

1. Telegram → **@BotFather** → `/newbot` → khod l-**TOKEN**
2. Sifet message l-bot, mn be3d zور `https://api.telegram.org/bot<TOKEN>/getUpdates` → 9elleb 3la `"chat":{"id":...}` = **CHAT_ID**

### 3️⃣ Test local

```bash
cd ict-python
pip install -r requirements.txt

# 7ot l-credentials (Linux/Mac):
export TWELVEDATA_KEY=xxx
export TELEGRAM_TOKEN=xxx
export TELEGRAM_CHAT_ID=xxx

# Windows (PowerShell):
#   $env:TWELVEDATA_KEY="xxx"

python main.py
```

Khass-k tji message "✅ ICT Bot online" f Telegram.

### 4️⃣ Déploiement Railway (24/7)

1. **railway.app** → New Project → upload l-folder (wla GitHub)
2. Settings → Variables: zid `TWELVEDATA_KEY`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`
3. Railway kay9ra l-`Procfile` (`worker: python main.py`) — kaykhdem 24/7

---

## ⚙️ Réglages (`config/settings.py`)

| Réglage | Default | Wach kaydir |
|---------|---------|-------------|
| `PAIRS` | EUR/USD, GBP/USD, XAU/USD, USD/JPY | Pairs (Twelve Data: `EUR/USD` b slash) |
| `TIMEFRAME` | M15 | M1/M5/M15/M30/H1/H4/D |
| `OB_STRENGTH` | 5 | Sensibilité Order Blocks |
| `FVG_MIN_SIZE` | 0 | Filteri FVG sghar (noise) |
| `FRESH_BARS` | 50 | Signal ghir 3la zones jdad |
| `USE_KILLZONE` | True | Signal ghir f London/NY |
| `SCAN_INTERVAL` | 300 | Sec bين scans (free tier safe) |

> ⚠️ **Rate limit**: Free tier = 8 req/min. L-code 3andu throttle automatique (8s bين calls). Ma t-zيdش pairs bezzaf (4-6 max) wla t-baisser SCAN_INTERVAL bezzaf.

---

## 🎯 Killzones (UTC)

- **London**: 07:00–10:00 UTC
- **New York**: 12:00–15:00 UTC

Casablanca = UTC+1 → London KZ ≈ 08:00–11:00 3andek.

---

## ⚠️ Notes

- Detection OB/FVG **solide mais machi parfaite** — base mezyana, ICT real fih confluences ktar.
- Bda b **M15** — noise a9al.
- **Ay signal = verify 3la chart**. Tool d'aide, machi garantie.
- Free tier 800 req/jour: 4 pairs × scan kol 5min × ~3h killzone/jour = bنin l-quota.

---

## 🔜 Étapes jaya possibles

1. **Multi-timeframe bias**: H4 direction + M15 entry
2. **Liquidity sweep**: stop-hunt detection 9bel OB
3. **Market structure shift (MSS)**: confirmation a9wa
4. **Dashboard web**: signals history + win-rate
5. **Risk levels**: auto SL/TP basé 3la zone + ATR
