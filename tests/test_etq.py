"""Tests for ETQ rolling-window computation."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.quant.etq import etq_window


@dataclass
class R:
    ts: datetime
    ltq: int


NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_etq_sums_ltq_only_within_the_time_window():
    history = [
        R(NOW - timedelta(minutes=70), 999),   # OUTSIDE all windows
        R(NOW - timedelta(minutes=30), 200),   # in 60m
        R(NOW - timedelta(minutes=10), 50),    # in 20m
        R(NOW - timedelta(minutes=3), 40),     # in 5m
        R(NOW - timedelta(seconds=10), 20),    # in 5m
    ]
    assert etq_window(history, 5, NOW) == 60         # 40 + 20
    assert etq_window(history, 20, NOW) == 110       # 50 + 40 + 20
    assert etq_window(history, 60, NOW) == 310       # 200 + 50 + 40 + 20


def test_etq_boundary_is_inclusive():
    """A record exactly at (now - window) is included."""
    history = [R(NOW - timedelta(minutes=5), 100)]
    assert etq_window(history, 5, NOW) == 100


def test_etq_empty_history_is_zero():
    assert etq_window([], 5, NOW) == 0
    assert etq_window([], 20, NOW) == 0
    assert etq_window([], 60, NOW) == 0


def test_etq_uses_ltq_only_never_day_volume():
    """Regression: ETQ MUST come from LTQ (per-tick executed qty)."""
    history = [
        R(NOW - timedelta(seconds=30), 100),
        R(NOW - timedelta(seconds=1), 200),
    ]
    # A naive "day volume" implementation would return one giant number.
    # We simply sum LTQ values in the window.
    assert etq_window(history, 5, NOW) == 300
