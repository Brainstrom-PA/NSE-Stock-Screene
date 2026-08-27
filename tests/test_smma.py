"""Tests for the SMMA calculator (streaming + reference values)."""
import math

from app.quant.smma import SMMACalculator, smma


def test_smma_warmup_returns_none_until_period_prices():
    calc = SMMACalculator(period=5)
    for p in [10.0, 11.0, 12.0, 13.0]:
        assert calc.update(p) is None
        assert calc.is_ready is False
    val = calc.update(14.0)  # 5th price -> seed
    assert calc.is_ready is True
    assert math.isclose(val, (10 + 11 + 12 + 13 + 14) / 5)


def test_smma_recurrence_after_warmup():
    """SMMA_t = ((N-1) * SMMA_(t-1) + Price_t) / N."""
    prices = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0]
    calc = SMMACalculator(period=5)
    for p in prices[:-1]:
        calc.update(p)
    seeded = calc.value
    expected = ((5 - 1) * seeded + 15.0) / 5
    got = calc.update(15.0)
    assert math.isclose(got, expected)


def test_smma_constant_series_equals_constant():
    calc = SMMACalculator(period=10)
    for _ in range(50):
        v = calc.update(100.0)
    assert math.isclose(v, 100.0)


def test_smma_lags_a_rising_series():
    calc = SMMACalculator(period=10)
    v = None
    for p in range(1, 51):
        v = calc.update(float(p))
    # SMMA must lag the latest price 50 in a rising series.
    assert v is not None and v < 50.0
    # And be well above the seed mean.
    assert v > 30.0


def test_smma_convenience_matches_streaming():
    prices = [float(i) for i in range(1, 40)]
    calc = SMMACalculator(period=10)
    last = None
    for p in prices:
        last = calc.update(p)
    assert math.isclose(smma(prices, 10), last)


def test_smma_rejects_bad_period():
    for bad in (0, 1, -3):
        try:
            SMMACalculator(bad)
        except ValueError:
            continue
        raise AssertionError(f"period={bad} should have raised")
