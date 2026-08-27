"""Tests for the demo provider and provider abstraction."""
from app.data.base_provider import BaseMarketDataProvider
from app.data.demo_provider import DemoMarketDataProvider
from app.data.angel_one_provider import AngelOneMarketDataProvider
from app.data.instrument_master import DEMO_UNIVERSE
from app.data.models import MarketTick


def test_demo_provider_is_a_base_provider():
    assert issubclass(DemoMarketDataProvider, BaseMarketDataProvider)
    assert issubclass(AngelOneMarketDataProvider, BaseMarketDataProvider)


def test_demo_provider_is_ready_after_init():
    p = DemoMarketDataProvider()
    assert p.is_ready() is True
    assert p.name == "demo"


def test_demo_provider_snapshot_shape():
    p = DemoMarketDataProvider(seed=1)
    snap = p.get_snapshot()
    assert len(snap) == len(DEMO_UNIVERSE)
    for t in snap:
        assert isinstance(t, MarketTick)
        assert t.source == "demo"
        assert t.exchange == "NSE"
        assert t.ltp > 0
        assert t.bid_price < t.ask_price
        assert t.bid_quantity >= 0 and t.ask_quantity >= 0


def test_demo_provider_ticks_change_over_time():
    p = DemoMarketDataProvider(seed=1)
    first = {t.symbol: t.ltp for t in p.get_snapshot()}
    changed = False
    for _ in range(5):
        second = {t.symbol: t.ltp for t in p.get_snapshot()}
        if any(second[s] != first[s] for s in first):
            changed = True
            break
    assert changed, "demo provider must produce moving prices"


def test_angel_one_provider_is_not_ready_and_raises():
    p = AngelOneMarketDataProvider()
    assert p.is_ready() is False
    try:
        p.get_snapshot()
    except NotImplementedError:
        return
    raise AssertionError("Angel One provider must not return data in Phase 1")
