"""Tests for TradeTracker BUY/SELL P/L bookkeeping."""
from app.signals.trade_engine import TradeTracker


def test_buy_then_sell_computes_positive_pnl():
    tt = TradeTracker()
    assert tt.record_crossover("ITC", "BUY", "t1", 100.0, {}) is None
    c = tt.record_crossover("ITC", "SELL", "t2", 105.0, {})
    assert c is not None
    assert c.direction == "BUY"
    assert c.entry_price == 100.0
    assert c.exit_price == 105.0
    assert c.pnl == 5.0
    assert c.profitable is True


def test_sell_then_buy_uses_entry_minus_exit():
    tt = TradeTracker()
    tt.record_crossover("X", "SELL", "t1", 100.0, {})
    c = tt.record_crossover("X", "BUY", "t2", 95.0, {})
    assert c.direction == "SELL"
    assert c.entry_price == 100.0
    assert c.exit_price == 95.0
    assert c.pnl == 5.0  # entry − exit for a SELL
    assert c.profitable is True


def test_buy_that_ends_lower_is_a_loss():
    tt = TradeTracker()
    tt.record_crossover("X", "BUY", "t1", 100.0, {})
    c = tt.record_crossover("X", "SELL", "t2", 95.0, {})
    assert c.pnl == -5.0
    assert c.profitable is False


def test_sell_that_ends_higher_is_a_loss():
    tt = TradeTracker()
    tt.record_crossover("X", "SELL", "t1", 100.0, {})
    c = tt.record_crossover("X", "BUY", "t2", 110.0, {})
    assert c.pnl == -10.0
    assert c.profitable is False


def test_same_direction_repeat_does_not_close_a_trade():
    """A BUY immediately followed by another BUY must NOT double-count."""
    tt = TradeTracker()
    tt.record_crossover("X", "BUY", "t1", 100.0, {})
    c = tt.record_crossover("X", "BUY", "t2", 110.0, {})
    assert c is None
    assert len(tt.completed) == 0
    # The original open trade is preserved.
    assert tt.open["X"].entry_price == 100.0


def test_symbols_are_tracked_independently():
    tt = TradeTracker()
    tt.record_crossover("A", "BUY", "t1", 100.0, {})
    tt.record_crossover("B", "SELL", "t1", 200.0, {})
    ca = tt.record_crossover("A", "SELL", "t2", 105.0, {})
    cb = tt.record_crossover("B", "BUY", "t2", 190.0, {})
    assert ca.symbol == "A" and ca.pnl == 5.0
    assert cb.symbol == "B" and cb.pnl == 10.0
    assert len(tt.completed) == 2


def test_features_captured_at_entry_survive_to_completed():
    tt = TradeTracker()
    entry_feats = {"a": 1.0, "b": 2.5}
    tt.record_crossover("X", "BUY", "t1", 100.0, entry_feats)
    c = tt.record_crossover("X", "SELL", "t2", 105.0, {"a": 99.0, "b": 99.0})
    # The completed trade must use the ENTRY-time features, not exit features.
    assert c.features == entry_feats
