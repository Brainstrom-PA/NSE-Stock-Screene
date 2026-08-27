"""Tests for the crossover event detector."""
from app.signals.crossover import BUY, SELL, detect_crossover, stance


def test_returns_none_when_any_input_missing():
    assert detect_crossover(None, 1.0, 2.0, 1.5) is None
    assert detect_crossover(1.0, None, 2.0, 1.5) is None
    assert detect_crossover(1.0, 1.5, None, 1.5) is None
    assert detect_crossover(1.0, 1.5, 2.0, None) is None


def test_buy_event_fires_when_fast_crosses_above_slow():
    # prev: 20 <= 120 ; curr: 20 > 120  ->  BUY
    assert detect_crossover(10.0, 12.0, 13.0, 12.5) == BUY


def test_buy_event_prev_equal_slow_and_now_above():
    # equality on prev counts (uses <=)
    assert detect_crossover(12.0, 12.0, 13.0, 12.0) == BUY


def test_sell_event_fires_when_fast_crosses_below_slow():
    # prev: 20 >= 120 ; curr: 20 < 120  ->  SELL
    assert detect_crossover(13.0, 12.0, 11.5, 12.0) == SELL


def test_sell_event_prev_equal_slow_and_now_below():
    assert detect_crossover(12.0, 12.0, 11.5, 12.0) == SELL


def test_no_event_when_relationship_unchanged():
    # both bars have fast > slow, no event.
    assert detect_crossover(13.0, 12.0, 14.0, 12.5) is None
    # both bars have fast < slow, no event.
    assert detect_crossover(10.0, 12.0, 11.0, 12.5) is None


def test_stance_reflects_current_relationship():
    assert stance(13.0, 12.0) == "BULLISH"
    assert stance(11.0, 12.0) == "BEARISH"
    assert stance(12.0, 12.0) == "FLAT"
    assert stance(None, 12.0) is None
