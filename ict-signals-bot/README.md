# ICT Analysis Bot — Confluence + Entry/SL/TP + Diagnostics

Bot d'**analyse complète** ICT: kay-détecta, kay-analyzي b confluence multi-timeframe, w kayعطي signal m-filtré b Entry + Stop Loss + Take Profit.

> 🎯 **Philosophie:** a9al signals, walakin kol wahed m-confirmé. Hard filters (machi score).

---

## 🆕 Jdid f had l-version

### 1. 🔍 Diagnostic logging
L-bot daba kayقول lik **3lash 0 signals** kol scan:
```
EUR/USD [cached HTF] no signal — blocked=no liquidity sweep (cand=BUY FVG, HTF=bullish, brk=bull, sweep=none)
XAU/USD [fresh HTF] no signal — no fresh zone tapped (HTF=bearish, 3 zones)
GBP/USD ✅ BUY FVG SIGNAL sent=True (entry=1.27340 sl=1.27180 tp=1.27660)
```
Hakda t-chوf b 3aynيk ach كاي-blokي → t-tunيe l-bot صحيح.

### 2. 🎚️ MODE system (3 niveaux)
F `config/settings.py`, سطر wahed: `MODE = "balanced"`

| Mode | Filters | Signals |
|------|---------|---------|
| `conservative` | bias + MSS + **sweep** | A9al, a9wa |
| `balanced` ⭐ | bias + MSS | متوازن (default) |
| `relaxed` | bias ghir | Ktar, ad3af |

> Ila كان عندك 0 signals f `conservative` → l-sweep filter صارم. `balanced` كاي-7ll hadchi.

### 3. ⚡ HTF caching (quota fix)
H4 ما كاي-تبدلش kol 5min (kol ~4h!). Daba كاي-cachيه:
- **9bel:** 8 req/scan (4 pairs × 2 TF)
- **daba:** ~4-5 req/scan (HTF cached)
- **~40% أقل requests** → l-quota 800/jour آمن بزاف

---

## 📁 Structure

```
ict-python/
├── main.py                 ← loop + diagnostics + cache
├── config/settings.py      ← MODE + DIAGNOSTIC_LOG + réglages
├── core/
│   ├── feed.py             ← Twelve Data
│   ├── cache.py            ← HTF time-based cache              [NEW]
│   ├── ict_engine.py       ← OB + FVG detection
│   ├── structure.py        ← swings, BOS/MSS, sweep, ATR
│   ├── analysis.py         ← confluence + Entry/SL/TP + diagnostics
│   ├── killzone.py         ← session filter
│   └── notifier.py         ← Telegram
├── requirements.txt
├── .env.example
└── Procfile
```

---

## 🔧 L-diagnostic flow (mنين 0 signals)

1. شغّل b `DIAGNOSTIC_LOG = True` (déjà on)
2. خليه يدور f killzone (London 07-10 UTC / NY 12-15 UTC)
3. شوف l-logs:

| L-log كاي-9ول | L-mعنى | L-7all |
|---------------|--------|--------|
| `blocked=HTF bias` بزاف | Market sideways, bias neutral | Normal — stenna trend واضح |
| `no fresh zone tapped` | Price ما وصلش l zone | زيد `FRESH_BARS` (30→50) |
| `blocked=no liquidity sweep` | Sweep filter صارم | `MODE='balanced'` |
| `blocked=no structure break` | MSS ناقص | `MODE='relaxed'` |
| `no signal` بزاف f killzone | Filters صارمين | بدّل MODE درجة |

---

## ⚙️ Réglages mohimmين (`config/settings.py`)

| Réglage | Default | Wach kaydir |
|---------|---------|-------------|
| `MODE` | balanced | conservative / balanced / relaxed |
| `DIAGNOSTIC_LOG` | True | Logs 3lash 0 signals |
| `RISK_REWARD` | 2.0 | R:R fixe (3.0 = 1:3) |
| `FRESH_BARS` | 30 | Zone freshness |
| `SCAN_INTERVAL` | 300 | Sec بين scans |
| `USE_KILLZONE` | True | London/NY ghir |

---

## 🚀 Setup

1. **Twelve Data key**: twelvedata.com/apikey (free, email ghir)
2. **Telegram bot**: @BotFather → token + chat id
3. Local: `export TWELVEDATA_KEY=... TELEGRAM_TOKEN=... TELEGRAM_CHAT_ID=...` → `python main.py`
4. **Railway**: upload + Variables → 24/7

---

## 📊 Quota math (Twelve Data free = 800/jour)

```
4 pairs × ~1.2 req/scan (HTF cached) = ~5 req/scan
Killzone = ~6h/jour, scan kol 5min = 72 scans
72 × 5 = ~360 req/jour  ✅ (taht 800)
```

Ila bغiti pairs ktar: زيد `SCAN_INTERVAL` (300→600) bach t-bqa taht l-quota.

---

## ⚠️ Notes

- **Balanced mode** = compromis مزيان بين quality w quantité. بدا بيه.
- **Conservative** = patient بزاف. ساعات bla signal = normal.
- Backtest 9bel ma t-trader b flous réels.
- Entry/SL/TP = suggestions basés 3la zone + ATR. Verify 3la chart.

---

## 🔜 Étapes jaya

1. **Backtesting module**: win-rate 3la données historiques
2. **Multiple TP** (TP1/TP2/TP3)
3. **News filter**: skip 9bel high-impact news
4. **Dashboard web**: signals + performance tracking
