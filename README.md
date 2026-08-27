# AI Market Screening — NSE Stock Screening & SMMA Crossover Analysis

A single-dashboard, AI/ML-based screening and analysis system for
NSE-listed stocks. Screens the universe by price + liquidity, computes
SMMA(20) & SMMA(120), detects BUY/SELL crossovers, tracks the realised
P/L of each completed BUY↔SELL pair, and predicts whether a fresh
crossover is likely to be profitable using a supervised ML model
trained on historical crossover outcomes.

## Project objective

Given a universe of NSE symbols, continuously answer:

1. **Which stocks are tradeable?** Price in ₹30–₹500 and both sides of
   the top-of-book quote > 10 lakh.
2. **What is the trend?** SMMA(20) vs SMMA(120).
3. **Did a crossover just fire?** Event, not state.
4. **Is this crossover likely to be profitable?** Probability, an
   ACCEPT/AVOID decision at a configurable threshold, and a plain
   English explanation drawn from actual features.

No trading order placement — analysis / screening only.

## Screening logic

- Price: `30 ≤ LTP ≤ 500` (inclusive both ends).
- Liquidity: `bid_quantity > 1,000,000` **AND** `ask_quantity > 1,000,000` (strict).

Thresholds are defined once in `backend/app/config/thresholds.py`.

## SMMA crossover logic

SMMA recurrence (seeded with the SMA of the first `N` prices):

```
SMMA_t = ((N − 1) · SMMA_(t−1) + Price_t) / N
```

- Fast: `N = 20`, Slow: `N = 120`.
- **BUY**  event when previous SMMA20 ≤ previous SMMA120 **and** current SMMA20 > current SMMA120.
- **SELL** event when previous SMMA20 ≥ previous SMMA120 **and** current SMMA20 < current SMMA120.

An event fires exactly once per transition — it is never re-emitted
while the state persists.

## LTQ vs ETQ

- **LTQ** — quantity executed in the most recent trade/tick.
- **ETQ over N minutes** — sum of `LTQ` values for ticks whose timestamps
  fall within the trailing N-minute window.

ETQ is **not** day volume. ETQ 5m / 20m / 60m are recomputed on every
poll from the timestamped tick history (`app.quant.etq.etq_window`).

## Trade outcome tracking

`app.signals.trade_engine.TradeTracker` keeps at most one open trade per
symbol.

- BUY entry → next SELL for the same symbol closes it. `P/L = exit − entry`.
- SELL entry → next BUY closes it. `P/L = entry − exit`.
- `profitable = P/L > 0`.

Feature values are captured at the ENTRY leg only — no future
information ever enters the training data.

## ML approach

`app.ml.*`:

- `dataset.build_dataset()` orders completed trades by `exit_ts`
  (time-aware, no random shuffling).
- `train.train_and_register()` fits a **Logistic Regression** baseline
  (also used for feature attribution in the explanation) and a
  **Random Forest Classifier** primary, using an 80/20 time-aware split.
- `predict.predict()` returns `(probability, decision, explanation)`.
  `ACCEPT` when `probability ≥ ML_THRESHOLD` (default `0.60`,
  overridable via env), else `AVOID`.
- `explain.build_explanation()` ranks features by their scaled LR
  contribution to log-odds and names the top 1–2 real factors behind
  the decision (no random templates).
- Below `ML_MIN_TRAINING_EXAMPLES` (default 20) completed trades or
  with only one class present, the model is left untrained and the UI
  shows **Insufficient training data / Pending ML training data** — no
  fabricated probabilities anywhere.

## Demo mode

Set `DATA_MODE=demo` (default). The demo provider seeds ~60 minutes of
backdated ticks on startup so ETQ 5m/20m/60m and the average-LTP
columns are meaningful on the very first API response, and a few
crossovers accumulate to allow initial ML training. Simulated data is
labelled `DEMO / SIMULATED` in the dashboard header — never presented as
real market data.

## Live Angel One mode

Set `DATA_MODE=live`. The isolated live provider
(`app.data.angel_one_provider.AngelOneMarketDataProvider`) normalises
Angel One SmartAPI ticks into the same `MarketTick` model, so nothing
else in the pipeline needs to change.

Credentials come from environment variables only — never source code,
never the frontend:

```
ANGEL_API_KEY
ANGEL_CLIENT_CODE / ANGEL_CLIENT_ID
ANGEL_PASSWORD
ANGEL_TOTP_SECRET
```

If any credential is missing, the app does **not** crash: it reports
that live credentials are not configured. Demo mode continues to work.

## Local running instructions

```bash
# 1. Backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

# 2. Frontend
cd frontend && yarn install && cd ..

# 3. Configure (optional — demo mode needs no keys)
cp .env.example .env

# 4. Run
python run.py                        # API at http://127.0.0.1:8001
cd frontend && yarn start            # dashboard at http://localhost:3000
```

## Tests

```bash
pytest -q
```

Covers screening thresholds, SMMA math, crossover detection, ETQ
windows, average LTP, BUY/SELL P/L bookkeeping, and ML
insufficient/sufficient-data behaviour.

## Project layout

```
ai-market-screener/
├── backend/
│   ├── server.py                  # supervisor entry-point
│   ├── requirements.txt
│   └── app/
│       ├── main.py                # FastAPI /api routes
│       ├── config/                # settings + thresholds
│       ├── data/                  # providers, normalizer, models
│       ├── screening/screener.py
│       ├── quant/                 # SMMA, ETQ, LTQ, price features, feature engine
│       ├── signals/               # crossover, trade engine
│       ├── ml/                    # dataset, train, predict, explain, registry
│       ├── storage/               # SQLite foundation
│       └── services/pipeline.py   # end-to-end orchestration
├── frontend/                      # React dashboard (single page)
├── tests/                         # pytest suite
├── docs/                          # architecture, data dictionary, SRS
├── run.py                         # local entry-point
├── .env.example
├── .gitignore
└── README.md
```
