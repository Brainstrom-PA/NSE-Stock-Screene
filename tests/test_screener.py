"""
Screening tests — the most important tests in Phase 1.

Verifies the exact assignment rules and boundary behaviour:
    30 <= LTP <= 500  (inclusive)
    Bid Quantity > 1,000,000  (strict)
    Ask Quantity > 1,000,000  (strict)
"""
from app.config.thresholds import THRESHOLDS
from app.data.models import MarketTick
from app.screening.screener import (
    is_liquidity_qualified,
    is_price_qualified,
    screen_tick,
    screen_universe,
)


def _tick(ltp: float, bid: int, ask: int) -> MarketTick:
    return MarketTick(
        symbol="TEST", token="T", ltp=ltp,
        bid_price=ltp - 0.1, bid_quantity=bid,
        ask_price=ltp + 0.1, ask_quantity=ask,
    )


# --- Price boundaries -------------------------------------------------------

def test_price_boundary_30_inclusive():
    assert is_price_qualified(30.0) is True


def test_price_boundary_500_inclusive():
    assert is_price_qualified(500.0) is True


def test_price_boundary_below_30_rejected():
    assert is_price_qualified(29.99) is False


def test_price_boundary_above_500_rejected():
    assert is_price_qualified(500.01) is False


def test_price_middle_of_band():
    assert is_price_qualified(100.0) is True
    assert is_price_qualified(250.5) is True


# --- Liquidity (strict inequality) -----------------------------------------

def test_bid_qty_exactly_1M_rejected():
    assert is_liquidity_qualified(1_000_000, 2_000_000) is False


def test_ask_qty_exactly_1M_rejected():
    assert is_liquidity_qualified(2_000_000, 1_000_000) is False


def test_bid_and_ask_qty_1M_plus_1_qualifies():
    assert is_liquidity_qualified(1_000_001, 1_000_001) is True


def test_low_bid_qty_disqualifies_even_if_ask_ok():
    assert is_liquidity_qualified(999_000, 5_000_000) is False


def test_low_ask_qty_disqualifies_even_if_bid_ok():
    assert is_liquidity_qualified(5_000_000, 999_000) is False


# --- Combined --------------------------------------------------------------

def test_combined_pass():
    s = screen_tick(_tick(100.0, 1_500_000, 1_500_000))
    assert s.price_qualified and s.liquidity_qualified and s.qualified


def test_combined_price_fail():
    s = screen_tick(_tick(20.0, 1_500_000, 1_500_000))
    assert not s.price_qualified and s.liquidity_qualified and not s.qualified


def test_combined_liquidity_fail():
    s = screen_tick(_tick(100.0, 500_000, 500_000))
    assert s.price_qualified and not s.liquidity_qualified and not s.qualified


def test_combined_both_fail():
    s = screen_tick(_tick(1000.0, 500_000, 500_000))
    assert not s.qualified


def test_screen_universe_returns_one_result_per_input():
    ticks = [
        _tick(100.0, 1_500_000, 1_500_000),  # pass
        _tick(20.0, 1_500_000, 1_500_000),   # price fail
        _tick(100.0, 900_000, 900_000),      # liquidity fail
    ]
    out = screen_universe(ticks)
    assert len(out) == 3
    assert [s.qualified for s in out] == [True, False, False]


def test_thresholds_are_the_documented_values():
    """Guards against accidental drift of the assignment thresholds."""
    assert THRESHOLDS.price_min == 30.0
    assert THRESHOLDS.price_max == 500.0
    assert THRESHOLDS.bid_quantity_min_exclusive == 1_000_000
    assert THRESHOLDS.ask_quantity_min_exclusive == 1_000_000
