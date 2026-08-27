# AI Market Screening — PRD

## Original problem statement
AI-Powered NSE stock screening & SMMA crossover analysis system.
Phase 1 only: build the foundation (screening + demo provider + dashboard).
No fake ML results, no fake live-market results, no order execution.

## Users
- Retail quant analyst / trader who wants to screen NSE stocks by
  price & liquidity rules and later apply SMMA crossover + ML analytics.

## Core requirements (static)
- Screening: 30 ≤ LTP ≤ 500 AND bid_qty > 10L AND ask_qty > 10L.
- Provider abstraction: Base / Demo / AngelOne (Angel is Phase-2 stub).
- Normalized MarketTick as the ONLY inter-layer contract.
- Dashboard: header (DEMO + RUNNING badges), 4 KPI cards, live-updating
  stock table with all future columns marked "—"/"Pending", detail panel.
- 2-second REST polling (swappable for WebSocket later).
- SQLite storage foundation (schema for all future tables).
- Tests + docs (SRS, architecture, data dictionary, angel integration,
  quant methodology, ML methodology, user guide).
- `.env.example`, `.gitignore`, `python run.py`, no credentials needed.

## Architecture
DATA SOURCE → NORMALIZER → NORMALIZED MODEL → SCREENING → (QUANT → SIGNALS
→ ML → DECISION stubs) → DASHBOARD.

## Implemented (Phase 1) — 2026-02
- Modular `backend/app` package (config, data, screening, quant/signals/ml
  stubs, storage, services, main).
- FastAPI routes: `/api/{health,source,universe,snapshot,summary,stock/{sym}}`.
- Demo provider with 20 curated symbols exercising all screening branches.
- Fintech dark React dashboard (Chivo / IBM Plex Sans / JetBrains Mono).
- Tick-flash animation on price changes.
- pytest suite: 24 tests, all passing.
- Full documentation set.

## Implemented (Phase 2a) — 2026-02
- Streaming `SMMACalculator` (SMA-seed + recurrence) for 20 and 120 periods.
- Per-symbol `SymbolState` inside `Pipeline` (150-tick warm-up so SMMA120
  is populated on the very first API response).
- Crossover event detection (BUY / SELL) with `last_signal` and
  `last_signal_at` fields on `ScreenedStock`.
- `/api/summary` now reports `active_signals` (this tick) and
  `lifetime_signals` (any past event).
- Frontend Signal column renders `SignalPill` (bright BUY/SELL with
  pulsing dot on fresh events, muted for last known event).
- Detail panel shows numeric SMMA20/SMMA120, stance, latest event, time.
- New pytest coverage: SMMA math + crossover event detector (12 tests).

## Backlog / Next
- P0 (Phase 2b): ETQ 5m/20m/60m, LTQ moving averages, avg LTP 20m/60m,
  bid/ask ratio + spread features, Angel One live provider +
  SmartWebSocket normalizer.
- P1 (Phase 3): ML dataset builder, training, calibrated inference,
  explanation, ACCEPT/AVOID decision, time-aware validation.
- P2 (Phase 4): PyInstaller Windows .exe, WebSocket push to frontend.
