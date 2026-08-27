# Quantitative methodology (Phase 2 plan)

**Not implemented in Phase 1.** This document freezes the definitions
so Phase 2 code matches the spec exactly.

## SMMA (Smoothed Moving Average)

Recurrence:

```
SMMA_t = ((N - 1) · SMMA_(t-1) + Price_t) / N
```

Two horizons: `N = 20` and `N = 120`. Seed value: simple mean of the
first `N` prices.

## Crossover events

An **event** (not a state).

BUY crossover at time `t`:

```
SMMA20_(t-1) <= SMMA120_(t-1)   AND   SMMA20_t > SMMA120_t
```

SELL crossover at time `t`:

```
SMMA20_(t-1) >= SMMA120_(t-1)   AND   SMMA20_t < SMMA120_t
```

## LTQ features

- Current `LTQ`
- Average LTQ over 2m / 5m
- LTQ acceleration = `(avg_LTQ_2m − avg_LTQ_5m) / avg_LTQ_5m`

## ETQ (Effective Traded Quantity) windows

Sum of executed quantity in the trailing 5 / 20 / 60 minutes.

## Price features

- `average LTP 20m`, `average LTP 60m`
- Momentum = `(ltp_t − avg_ltp_20m) / avg_ltp_20m`
- Volatility = rolling std-dev of returns over 20m

## Market-depth features

- Bid/ask ratio = `bid_qty / ask_qty`
- Spread = `ask_price − bid_price`

## Trade outcome (paper P/L)

- BUY: `Entry = LTP at BUY crossover`, `Exit = LTP at next SELL crossover`.
  `P/L = Exit − Entry`.
- SELL: mirrored. `P/L = Entry − Exit`.
- Profitable iff `P/L > 0`.
