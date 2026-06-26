# ICT Analysis Bot — Conservative Confluence + Entry/SL/TP

Bot d'**analyse complète** (machi ghir signal generator). Kay-détecta, kay-analyzي b confluence, w kayعطي signal m-filtré b Entry + Stop Loss + Take Profit.

> 🎯 **L-philosophie:** a9al signals, walakin kol wahed m-confirmé b 4 facteurs. Conservative = hard filters (koll condition obligatoire, machi score).

```
Twelve Data (H4 bias + M15 entry)
      │
      ▼
┌─────────────────────────────────┐
│  ANALYSIS ENGINE (hard filters) │
│  1. HTF bias (H4) agrees    ✅  │
│  2. Structure break (BOS)   ✅  │
│  3. Liquidity sweep         ✅  │
│  4. Fresh OB/FVG reaction   ✅  │
│  5. Inside killzone         ✅  │
└─────────────────────────────────┘
      │  koll-hom passed?
      ▼
Signal + Entry/SL/TP (R:R 1:2) → Telegram
```

**Ila wahda mن l-conditions ناقصة → WALU signal.** Hadchi kay-elimini l-noise li كان كايجي bezzaf.

---

## 🆕 Ach tbeddel mن l-version 9dima

| 9bel | Daba |
|------|------|
| Signal 3la ay OB/FVG tap | Signal ghir ila **koll** confluence passed |
| Bezzaf signals (noise) | A9al bezzaf, walakin a9wa |
| Walو entry/SL/TP | Entry + SL + TP automatiques (R:R 1:2) |
| Timeframe wahed | H4 bias + M15 entry (multi-TF) |
| Walو sweep/MSS | Liquidity sweep + structure break obligatoires |

---

## 📁 Structure

```
ict-python/
├── main.py                 ← loop (fetch HTF+LTF → analyze → Telegram)
├── config/settings.py      ← réglages + hard filter toggles
├── core/
│   ├── feed.py             ← Twelve Data
│   ├── ict_engine.py       ← OB + FVG detection
│   ├── structure.py        ← swings, BOS/MSS, liquidity sweep, ATR  [NEW]
│   ├── analysis.py         ← confluence engine + Entry/SL/TP        [NEW]
│   ├── killzone.py         ← session filter
│   └── notifier.py         ← Telegram (Entry/SL/TP format)
├── requirements.txt
├── .env.example
└── Procfile
```

---

## 📲 Mثal d'signal jdid

```
🟢 ICT BUY SETUP 📈
━━━━━━━━━━━━━━━
📊 Pair: XAU/USD  |  ⏱ M15
💠 Zone: FVG  |  📐 R:R 1:2

🎯 Entry: 4046.28
🛑 Stop Loss: 4038.50
✅ Take Profit: 4061.84

Confluence (all confirmed):
   ✅ HTF bias bullish
   ✅ BOS bull
   ✅ liquidity sweep
   ✅ FVG reaction

💰 Current: 4047.10
━━━━━━━━━━━━━━━
⚠️ Not financial advice. Manage your risk.
```

---

## ⚙️ Réglages mohimmين (`config/settings.py`)

| Réglage | Default | Wach kaydir |
|---------|---------|-------------|
| `TIMEFRAME` | M15 | Entry timeframe |
| `HTF_TIMEFRAME` | H4 | Bias timeframe |
| `RISK_REWARD` | 2.0 | R:R fixe (7ot 3.0 l 1:3) |
| `SL_ATR_MULT` | 0.5 | Buffer d'SL (ATR × hadchi) |
| `REQUIRE_HTF_BIAS` | True | H4 bias obligatoire |
| `REQUIRE_MSS` | True | Structure break obligatoire |
| `REQUIRE_SWEEP` | True | Liquidity sweep obligatoire |
| `USE_KILLZONE` | True | London/NY ghir |

### 🎛️ Kif t-controlي 3dad d'signals

- **Bezzaf strict (a9al signals)**: koll filters True + R:R 3.0
- **Chwiya flexible**: 7ot `REQUIRE_SWEEP=False` (kayزيد signals)
- ⚠️ Conservative recommandé: khlli koll-hom True. L-but machi ktar signals, howa win-rate 3ali.

---

## 🚀 Setup (نفس l-version 9dima)

1. **Twelve Data key**: twelvedata.com/apikey (free, email ghir)
2. **Telegram bot**: @BotFather → token + chat id
3. Local: `export TWELVEDATA_KEY=... TELEGRAM_TOKEN=... TELEGRAM_CHAT_ID=...` → `python main.py`
4. **Railway**: upload + Variables → kayخدم 24/7

---

## ⚠️ Notes mohimma

- **Conservative = patient**. Wa9ila ghadي t-dوز ساعات bla signal — hadchi normal w mطلوب. Setup wahed نقي خير mن 10 d9af.
- L-Entry/SL/TP = **suggestions** basés 3la l-zone + ATR. Verify 3la chart 9bel.
- Backtest 9bel ma t-trader b flous réels. Had l-bot ma kay-garantiش profit.
- ICT real fih experience + context. L-bot = aide, machi remplacement d'analyse dyalek.

---

## 🔜 Étapes jaya possibles

1. **Backtesting module**: 7sab win-rate 3la données historiques
2. **Multiple TP** (TP1/TP2/TP3 b partial close)
3. **News filter**: skip signals 9bel high-impact news
4. **Dashboard web**: track signals + performance
5. **Trailing SL** logic
