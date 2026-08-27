# Data dictionary — normalized MarketTick

Every field the rest of the application ever sees. All providers MUST
produce this exact shape.

| Field           | Type      | Unit           | Meaning |
|-----------------|-----------|----------------|---------|
| `symbol`        | string    | —              | NSE trading symbol, e.g. `RELIANCE`. |
| `token`         | string    | —              | Instrument token / exchange identifier. Broker-specific in Phase 2; opaque here. |
| `exchange`      | string    | —              | Exchange code. Defaults to `NSE`. |
| `timestamp`     | ISO 8601  | UTC            | Server-side observation time. Always timezone-aware. |
| `ltp`           | float     | ₹              | Last Traded Price. |
| `ltq`           | int       | shares         | Last Traded Quantity — number of shares in the most recent trade. |
| `day_volume`    | int       | shares         | Cumulative traded volume since the session opened. |
| `bid_price`     | float     | ₹              | Best (highest) buy price on the order book. |
| `bid_quantity`  | int       | shares         | Aggregate quantity at `bid_price`. |
| `ask_price`     | float     | ₹              | Best (lowest) sell price on the order book. |
| `ask_quantity`  | int       | shares         | Aggregate quantity at `ask_price`. |
| `source`        | string    | —              | `demo` or `angel_one`. Used by the UI to label data provenance. |

## ScreenedStock

Adds screening flags and Phase-2/3 placeholders (all `None` in Phase 1):

| Field                                   | Type / status |
|-----------------------------------------|---------------|
| `tick`                                  | `MarketTick`  |
| `price_qualified`                       | `bool` — `30 ≤ ltp ≤ 500` |
| `liquidity_qualified`                   | `bool` — `bid_qty > 1_000_000 AND ask_qty > 1_000_000` |
| `qualified`                             | `bool` — AND of both above |
| `smma20`, `smma120`                     | `float \| null` — Phase 2 |
| `etq_5m`, `etq_20m`, `etq_60m`          | `float \| null` — Phase 2 |
| `avg_ltp_20m`, `avg_ltp_60m`            | `float \| null` — Phase 2 |
| `signal`                                | `"BUY" \| "SELL" \| null` — Phase 2 |
| `ai_probability`                        | `float \| null` — Phase 3 |
| `decision`                              | `"ACCEPT" \| "AVOID" \| null` — Phase 3 |
