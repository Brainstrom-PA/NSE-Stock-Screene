"""
Demo instrument master.

A curated list of NSE-like equity symbols used by the demo provider.
The list is intentionally diverse so that the screening logic
can visibly demonstrate stocks that PASS and FAIL each rule:

- Some symbols price BELOW ₹30
- Some between ₹30 and ₹500 (the qualifying band)
- Some ABOVE ₹500

- Some with bid/ask quantity BELOW 1,000,000
- Some ABOVE 1,000,000

The `base_price` and `base_liquidity` are seeds; the demo provider
adds deterministic-random walk on top.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class DemoInstrument:
    symbol: str
    token: str
    base_price: float
    base_bid_qty: int
    base_ask_qty: int


# Curated demo universe (20 symbols) — mix designed to exercise every
# branch of the Phase 1 screener.
DEMO_UNIVERSE: List[DemoInstrument] = [
    # --- BELOW ₹30 (price should FAIL) ---
    DemoInstrument("SUZLON",     "T0001",   24.50, 4_200_000, 3_900_000),
    DemoInstrument("YESBANK",    "T0002",   19.75, 5_100_000, 4_800_000),
    DemoInstrument("IDEA",       "T0003",   14.20, 8_400_000, 7_800_000),

    # --- ABOVE ₹500 (price should FAIL) ---
    DemoInstrument("TCS",        "T0004", 3820.00,   380_000,   410_000),
    DemoInstrument("RELIANCE",   "T0005", 2915.50,   920_000, 1_050_000),
    DemoInstrument("HDFCBANK",   "T0006", 1610.25, 1_120_000, 1_180_000),

    # --- WITHIN ₹30–₹500 but LOW liquidity (should FAIL on qty) ---
    DemoInstrument("BEL",        "T0007",  238.40,   420_000,   380_000),
    DemoInstrument("NMDC",       "T0008",  212.15,   740_000, 1_150_000),  # bid low
    DemoInstrument("IOC",        "T0009",  168.90, 1_240_000,   860_000),  # ask low

    # --- WITHIN band AND HIGH liquidity (should PASS) ---
    DemoInstrument("ITC",        "T0010",  442.30, 1_820_000, 1_910_000),
    DemoInstrument("ONGC",       "T0011",  278.55, 2_150_000, 2_260_000),
    DemoInstrument("PNB",        "T0012",   96.10, 3_400_000, 3_120_000),
    DemoInstrument("SAIL",       "T0013",  128.75, 2_640_000, 2_480_000),
    DemoInstrument("BHEL",       "T0014",  254.00, 1_450_000, 1_610_000),
    DemoInstrument("TATASTEEL",  "T0015",  152.60, 3_120_000, 2_970_000),
    DemoInstrument("GAIL",       "T0016",  198.40, 1_780_000, 1_820_000),
    DemoInstrument("NHPC",       "T0017",   87.25, 2_240_000, 2_310_000),
    DemoInstrument("VEDL",       "T0018",  452.10, 1_060_000, 1_140_000),

    # --- Edge-of-band symbols (near ₹30 / ₹500) ---
    DemoInstrument("EDGE_LOW",   "T0019",   30.40, 1_500_000, 1_500_000),  # just above 30
    DemoInstrument("EDGE_HIGH",  "T0020",  498.20, 1_500_000, 1_500_000),  # just below 500
]
