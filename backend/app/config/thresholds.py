"""
Centralised screening thresholds.

Assignment specification (do NOT change these values or operators):

    30 <= LTP <= 500
    Bid Quantity > 1,000,000
    Ask Quantity > 1,000,000

Note the strict `>` for quantities: exactly 1,000,000 does NOT qualify.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScreeningThresholds:
    price_min: float = 30.0
    price_max: float = 500.0
    bid_quantity_min_exclusive: int = 1_000_000
    ask_quantity_min_exclusive: int = 1_000_000


THRESHOLDS = ScreeningThresholds()
