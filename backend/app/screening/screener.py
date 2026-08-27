"""
NSE screening engine — Phase 1.

Applies the assignment rules to every normalized MarketTick:

    30 <= LTP <= 500
    Bid Quantity > 1,000,000
    Ask Quantity > 1,000,000

Returns a list of `ScreenedStock` records annotated with the individual
qualification flags so the UI can show WHY a stock passed or failed.
"""
from __future__ import annotations

from typing import Iterable, List

from app.config.thresholds import THRESHOLDS
from app.data.models import MarketTick, ScreenedStock


def is_price_qualified(ltp: float) -> bool:
    """30 <= LTP <= 500 (inclusive on both ends)."""
    return THRESHOLDS.price_min <= ltp <= THRESHOLDS.price_max


def is_liquidity_qualified(bid_qty: int, ask_qty: int) -> bool:
    """Bid AND Ask quantity STRICTLY greater than 1,000,000."""
    return (
        bid_qty > THRESHOLDS.bid_quantity_min_exclusive
        and ask_qty > THRESHOLDS.ask_quantity_min_exclusive
    )


def screen_tick(tick: MarketTick) -> ScreenedStock:
    """Screen a single tick and return a ScreenedStock with pass/fail flags."""
    price_ok = is_price_qualified(tick.ltp)
    liq_ok = is_liquidity_qualified(tick.bid_quantity, tick.ask_quantity)
    return ScreenedStock(
        tick=tick,
        price_qualified=price_ok,
        liquidity_qualified=liq_ok,
        qualified=price_ok and liq_ok,
    )


def screen_universe(ticks: Iterable[MarketTick]) -> List[ScreenedStock]:
    """Screen an iterable of ticks (the full universe snapshot)."""
    return [screen_tick(t) for t in ticks]
