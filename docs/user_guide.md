# User guide (Phase 1)

## Launch locally

```bash
python run.py                     # API on http://127.0.0.1:8001
cd frontend && yarn start         # dashboard on http://localhost:3000
```

## Reading the dashboard

- **Header** – confirms the app is running and that the data source is
  `DEMO / SIMULATED`. Nothing here is real market data.
- **KPI cards** – snapshot counts:
  - `NSE Universe` — number of symbols being simulated (20).
  - `Price Qualified` — how many satisfy `30 ≤ LTP ≤ 500`.
  - `Liquidity Qualified` — how many satisfy `bid_qty > 10L AND ask_qty > 10L`.
  - `Active Signals` — `0`, because the crossover engine is a Phase-2 feature.
- **Stock table** – one row per symbol. The `Screen` cell shows the pass/fail
  status. Cells with `—` or `Pending` are reserved for Phase 2/3 features and
  intentionally not fabricated.
- **Detail panel** – click a row to see the full market depth for that
  symbol. Sections for Chart / ML analysis are shown as
  `Not implemented in Phase 1` placeholders.

## Screening rules

- Price: `30 ≤ LTP ≤ 500` (both ends inclusive).
- Liquidity: `bid_qty > 1,000,000 AND ask_qty > 1,000,000` (strict).
- Only rows that pass **both** are marked as fully qualified.

## Refresh cadence

The dashboard polls `/api/snapshot` every 2 seconds. Cells whose value
changed flash briefly — green if the number went up, red if it went down.

## Stopping the app

- Ctrl+C in each terminal.
