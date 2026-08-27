"""
SMMA crossover detection — Phase 2 implementation.

BUY event at bar t:
    SMMA20_(t-1) <= SMMA120_(t-1)   AND   SMMA20_t > SMMA120_t

SELL event at bar t:
    SMMA20_(t-1) >= SMMA120_(t-1)   AND   SMMA20_t < SMMA120_t

A crossover is an EVENT (transition), not a state. This module returns
`None` unless the transition literally happened between the previous and
the current bar.
"""
from __future__ import annotations

from typing import Optional

BUY = "BUY"
SELL = "SELL"


def detect_crossover(
    prev_fast: Optional[float],
    prev_slow: Optional[float],
    curr_fast: Optional[float],
    curr_slow: Optional[float],
) -> Optional[str]:
    """Return "BUY", "SELL" or None for the given fast/slow SMMA pair."""
    if (
        prev_fast is None
        or prev_slow is None
        or curr_fast is None
        or curr_slow is None
    ):
        return None
    if prev_fast <= prev_slow and curr_fast > curr_slow:
        return BUY
    if prev_fast >= prev_slow and curr_fast < curr_slow:
        return SELL
    return None


def stance(fast: Optional[float], slow: Optional[float]) -> Optional[str]:
    """Return the current SMMA stance (BULLISH / BEARISH / FLAT / None)."""
    if fast is None or slow is None:
        return None
    if fast > slow:
        return "BULLISH"
    if fast < slow:
        return "BEARISH"
    return "FLAT"
