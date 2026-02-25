# 🛠️ Trading Tools

## Polymarket Tool
- **Location:** `polymarket-tool/`
- **Start:** `./start.sh`
- **URL:** http://localhost:8502
- **API Key:** `019c3d3c-80a9-725f-96bd-2e29348b07f6`
- **Features:** Market search, order book, one-click to official site
- **Status:** API endpoint fixed (/book?token_id=xxx)

## TA Telegram Bot (New)
- **Location:** `ta-telegram-bot/`
- **Features:** 
  - Multi-timeframe analysis (1d/4h/1h/15m/5m)
  - SMC/ICT style (Liquidity → FVG → OB → Execution Plan)
  - Auto position tracking from Binance
  - Price alerts for key levels
- **Source:** Binance USDT Perpetual (fapi)
- **Analysis:** LLM-based (OpenClaw Gateway)

## Binance Account
- **Type:** Futures (USDT-M)
- **API:** Configured for read-only access
- **Base URL:** https://fapi.binance.com

---
*Type: FACT-004, new trading bot*
