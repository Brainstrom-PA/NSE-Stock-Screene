# Software Requirements Specification — AI Market Screening

## 1. Purpose

A market-screening and quantitative-analysis system for NSE-listed stocks
that (a) screens the universe by price and liquidity, (b) computes SMMA
crossovers, (c) predicts profitability of each crossover with a supervised
ML model, and (d) displays a professional live dashboard.

The system is analysis-only. **No order execution is in scope, ever.**

## 2. Scope by phase

Each requirement below is tagged with the phase in which it becomes
functional.

### 2.1 Phase 1 — IMPLEMENTED

- [x] Modular Python package (`backend/app/…`)
- [x] Normalized market-data model (`MarketTick`, `ScreenedStock`)
- [x] Provider abstraction (`BaseMarketDataProvider`)
- [x] `DemoMarketDataProvider` (fully working, deterministic-random walk)
- [x] `AngelOneMarketDataProvider` integration boundary (no credentials needed)
- [x] NSE screening (LTP ₹30–₹500 inclusive, Bid Qty > 10L, Ask Qty > 10L strict)
- [x] Centralised thresholds (`app/config/thresholds.py`)
- [x] SQLite storage foundation (schema for observations / crossovers /
      trade outcomes / ML examples / models)
- [x] FastAPI service exposing `/api/health`, `/api/source`, `/api/snapshot`,
      `/api/summary`, `/api/stock/{symbol}`
- [x] React dashboard (professional dark fintech UI) with:
      header + DEMO/RUNNING badges, KPI cards, live-updating stock table,
      detail panel, 2-second REST polling
- [x] pytest suite covering models, providers, screening & boundary cases
- [x] `.env.example`, `.gitignore`, README, architecture docs, data dictionary
- [x] Local runner (`python run.py`)

### 2.2 Phase 2 — PLANNED

- [x] SMMA(20) and SMMA(120) streaming computation _(Phase 2a done)_
- [x] Crossover event detection (BUY / SELL rules) _(Phase 2a done)_
- [ ] ETQ 5m / 20m / 60m windows
- [ ] LTQ moving averages & acceleration
- [ ] Average LTP 20m / 60m
- [ ] Bid/ask ratio and spread features
- [ ] Trade-outcome bookkeeping (paper P/L on crossovers)
- [ ] Angel One SmartAPI live provider (auth, WebSocket, normalization)

### 2.3 Phase 3 — PLANNED

- [ ] Feature engineering pipeline
- [ ] Supervised training (Logistic Regression baseline,
      HistGradientBoostingClassifier primary, Random Forest comparison)
- [ ] Time-aware validation (no random shuffling of time-series)
- [ ] Model registry & versioning
- [ ] Inference (`predict_profitability`) with calibrated probability
- [ ] SHAP / feature-attribution explanation
- [ ] ACCEPT / AVOID decision on the dashboard

### 2.4 Phase 4 — PLANNED

- [ ] Windows executable via PyInstaller
- [ ] Optional WebSocket push to the frontend (replaces 2s polling)

## 3. Functional requirements — Phase 1

### 3.1 Screening

Given a normalized `MarketTick`, the screener MUST classify it as:

- **Price qualified** iff `30 ≤ LTP ≤ 500`
- **Liquidity qualified** iff `bid_quantity > 1,000,000 AND ask_quantity > 1,000,000`
- **Qualified** iff both above are true

The thresholds are the assignment constants and MUST NOT be changed
in code paths — only via `app/config/thresholds.py`.

### 3.2 Data provider

- The demo provider MUST return a normalized snapshot on every call.
- The demo provider MUST label every tick with `source="demo"`.
- The Angel One provider MUST NOT require credentials in Phase 1
  and MUST raise `NotImplementedError` if invoked.

### 3.3 Dashboard

- Header displays: `AI MARKET SCREENING`, sub-title, `DATA SOURCE: DEMO`,
  `SYSTEM STATUS: RUNNING`.
- Four KPI cards: NSE Universe / Price Qualified / Liquidity Qualified /
  Active Signals (0 in Phase 1).
- Table with columns Symbol, LTP, SMMA20, SMMA120, LTQ, ETQ 5m/20m/60m,
  Avg LTP 20m/60m, Bid Price, Bid Qty, Ask Price, Ask Qty, Signal,
  AI Probability, Decision. Phase-1-unimplemented cells show `—` or `Pending`.
- Auto-refresh every 2 seconds via REST polling.
- Row detail panel with market depth + Phase-2/3 empty-state placeholders.

## 4. Non-functional requirements

- Local execution with `python run.py`.
- No external service required in Phase 1.
- Modular architecture, type hints, docstrings.
- Runs on Windows / macOS / Linux.
- Configuration externalised through `.env`.

## 5. Out of scope (permanent)

- Placing, modifying or cancelling orders.
- Automated trading.
- Investment advice.
