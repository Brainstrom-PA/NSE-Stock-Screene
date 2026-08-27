"""Tests for the normalized market-data model."""
from datetime import datetime, timezone

from app.data.models import MarketTick, ScreenedStock


def test_market_tick_defaults():
    tick = MarketTick(symbol="ITC", token="T0010", ltp=440.0)
    assert tick.exchange == "NSE"
    assert tick.source == "demo"
    assert tick.ltq == 0
    assert tick.day_volume == 0
    assert isinstance(tick.timestamp, datetime)
    assert tick.timestamp.tzinfo is not None  # timezone-aware


def test_market_tick_full_payload():
    tick = MarketTick(
        symbol="ONGC",
        token="T0011",
        ltp=278.5,
        ltq=250,
        day_volume=1_234_567,
        bid_price=278.4,
        bid_quantity=2_150_000,
        ask_price=278.6,
        ask_quantity=2_260_000,
        source="demo",
    )
    assert tick.bid_price < tick.ask_price
    assert tick.bid_quantity > 0 and tick.ask_quantity > 0


def test_screened_stock_placeholders_are_none():
    tick = MarketTick(symbol="X", token="T", ltp=100.0)
    s = ScreenedStock(
        tick=tick, price_qualified=True, liquidity_qualified=False, qualified=False
    )
    # Phase-2 fields must default to None so no fake data is exposed.
    assert s.smma20 is None
    assert s.smma120 is None
    assert s.signal is None
    assert s.ai_probability is None
    assert s.decision is None
