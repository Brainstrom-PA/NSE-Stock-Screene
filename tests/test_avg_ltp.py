"""Tests for rolling average LTP computation."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.quant.price_features import avg_ltp_window, ltp_at_or_before


@dataclass
class R:
    ts: datetime
    ltp: float


NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_avg_ltp_averages_values_within_window():
    history = [
        R(NOW - timedelta(minutes=30), 100.0),   # in 60m, NOT in 20m
        R(NOW - timedelta(minutes=15), 110.0),   # in 20m + 60m
        R(NOW - timedelta(minutes=5), 120.0),    # in 20m + 60m
    ]
    assert avg_ltp_window(history, 20, NOW) == (110.0 + 120.0) / 2
    assert avg_ltp_window(history, 60, NOW) == (100.0 + 110.0 + 120.0) / 3


def test_avg_ltp_none_when_no_data_in_window():
    history = [R(NOW - timedelta(minutes=90), 100.0)]
    assert avg_ltp_window(history, 20, NOW) is None


def test_avg_ltp_empty_returns_none():
    assert avg_ltp_window([], 20, NOW) is None


def test_ltp_at_or_before_returns_most_recent_qualifying():
    history = [
        R(NOW - timedelta(minutes=5), 100.0),
        R(NOW - timedelta(minutes=3), 110.0),
        R(NOW - timedelta(minutes=1), 120.0),
    ]
    # Target = 2 min ago → the 3-min-ago record is the most recent ≤ target.
    assert ltp_at_or_before(history, NOW - timedelta(minutes=2)) == 110.0
    # Target = 10 min ago → no record ≤ target.
    assert ltp_at_or_before(history, NOW - timedelta(minutes=10)) is None
