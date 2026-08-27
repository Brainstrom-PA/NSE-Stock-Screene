# Architecture

## Technical view

```
┌───────────────────────────────────────────────────────────────┐
│                         React Dashboard                       │
│  Header · KPI cards · Stock table (2s polling) · Detail panel │
└─────────────────────────────▲─────────────────────────────────┘
                              │  REST /api/*
┌─────────────────────────────┴─────────────────────────────────┐
│                         FastAPI (server.py)                   │
│                       app.main : /api routes                  │
└─────────────────────────────▲─────────────────────────────────┘
                              │
                    app.services.pipeline.Pipeline
                              │
        ┌─────────────────────┴──────────────────────┐
        ▼                                            ▼
BaseMarketDataProvider                       ScreeningEngine
   │                                          (app.screening)
   ├── DemoMarketDataProvider   ✅ Phase 1        │
   └── AngelOneMarketDataProvider  ▢ Phase 2      ▼
        │                              ScreenedStock  ─►  Downstream
        ▼                                                 (quant / signals /
     MarketTick                                            ml / decision — stubs)
     (normalized)
                              │
                              ▼
                     app.storage (SQLite)
                (schema ready for Phase 2+)
```

### Layer responsibilities

| Layer | Module | Phase 1 status |
|-------|--------|----------------|
| Data source        | `app.data.demo_provider`, `.angel_one_provider` | Demo ✅ / Angel ▢ |
| Normalization      | `app.data.normalizer`, `.models`                | ✅ |
| Screening          | `app.screening.screener`                        | ✅ |
| Quantitative       | `app.quant.*`                                   | Stubs |
| Signals            | `app.signals.*`                                 | Stubs |
| ML                 | `app.ml.*`                                      | Stubs |
| Storage            | `app.storage.database`, `.schema`, `.repositories` | Foundation ✅ |
| Orchestration      | `app.services.pipeline`                         | ✅ |
| HTTP API           | `app.main`                                      | ✅ |
| UI                 | `frontend/`                                     | ✅ |

### Why an abstract provider?

The rest of the system never sees an Angel One JSON payload. It only sees
`MarketTick` — our own normalized model. When Angel One is switched on
in Phase 2, only two files change:

1. `app.data.angel_one_provider` — implement `get_snapshot()`.
2. `app.data.normalizer.normalize_angel_one_tick` — map fields to `MarketTick`.

No changes are required to the screener, dashboard, or downstream
Phase 2/3 modules.

## Non-technical view (for evaluators)

Imagine a factory line:

1. **Data source** — where the market prices come from. Today we generate
   fake but realistic prices (DEMO). Tomorrow, a real broker feed
   (Angel One) plugs in the same slot without redesigning anything.
2. **Normalizer** — everything is translated to one common vocabulary
   so the rest of the factory does not care where the data came from.
3. **Screener** — a strict quality-check station: it keeps only stocks
   whose price is between ₹30 and ₹500 **and** whose bid/ask sizes are
   both above 10 lakh.
4. **Dashboard** — a live control room showing which stocks pass, which
   fail, and why. It refreshes every 2 seconds.

Future stations (crossover detection, ML profitability scoring, accept/
avoid decisions) already have their space reserved on the factory floor —
we just haven’t built the machines yet. The dashboard shows `—` or
`Pending` in those slots so nobody mistakes an empty station for a
working one.

## Data flow — one Phase-1 tick

1. UI calls `GET /api/snapshot` every 2 seconds.
2. `Pipeline.run_once()` asks the current provider for `get_snapshot()`.
3. The demo provider walks its RNG one step and returns 20 `MarketTick`s.
4. The screener produces 20 `ScreenedStock`s with price/liquidity flags.
5. FastAPI serializes and returns the array.
6. The React table renders — cells that changed briefly flash green/red.

## Configuration boundary

- All screening thresholds live in `app/config/thresholds.py`.
- All runtime behaviour (mode, tick interval, DB path) lives in
  `app/config/settings.py`, which is the only place that reads
  `os.environ`.
