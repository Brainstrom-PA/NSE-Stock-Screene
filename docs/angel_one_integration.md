# Angel One SmartAPI — planned integration (Phase 2)

Phase 1 does **not** connect to Angel One. This document describes the
integration boundary that already exists in the codebase and the steps
Phase 2 will follow.

## Boundary in the code

- `backend/app/data/base_provider.py` defines the interface every provider
  must implement.
- `backend/app/data/angel_one_provider.py` is a stub that raises
  `NotImplementedError` if invoked in Phase 1 and returns `is_ready() == False`.
- `backend/app/data/normalizer.py::normalize_angel_one_tick` is the only
  place that will translate Angel One frames into our `MarketTick`.

Because the rest of the system consumes `MarketTick`, no other file
changes when we go live.

## Environment variables (Phase 2)

Placeholders already documented in `.env.example`:

```
ANGEL_API_KEY=
ANGEL_CLIENT_ID=
ANGEL_PASSWORD=
ANGEL_TOTP=          # rotating 2-factor code
```

None of these are read in Phase 1.

## Planned Phase-2 sequence

1. Login via SmartAPI (`generateSession`) using API key, client id,
   password and current TOTP.
2. Persist `feed_token`, `access_token` in memory only (never on disk).
3. Fetch the instrument master and map Angel One tokens to our
   `DemoInstrument` universe (or replace it with the live NSE list).
4. Open the SmartWebSocket v2 market-feed subscription for LTP + depth.
5. On every frame call `normalize_angel_one_tick(raw)` → `MarketTick`.
6. Store the tick in `market_observations` (SQLite) and forward it to
   the pipeline.
7. Switch mode: `DATA_MODE=live` in `.env`.

## What Phase 2 must NOT do

- Do not place, modify or cancel orders. This is an analysis system.
- Do not log or expose any Angel One credential.
- Do not couple screening / quant / UI code to Angel One field names.

## Reference

- SmartAPI docs: https://smartapi.angelbroking.com/docs
- SmartWebSocket v2 market feed
