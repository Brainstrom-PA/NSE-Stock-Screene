"""Tests for ML training + prediction + insufficient-data behaviour."""
from app.ml.model_registry import ModelRegistry
from app.ml.predict import predict
from app.ml.train import train_and_register
from app.signals.trade_engine import CompletedTrade


def _fake_trade(i, profitable, feats):
    return CompletedTrade(
        symbol="X",
        direction="BUY",
        entry_ts=f"2026-01-01T12:{i // 60:02d}:{i % 60:02d}Z",
        exit_ts=f"2026-01-01T13:{i // 60:02d}:{i % 60:02d}Z",
        entry_price=100.0,
        exit_price=101.0 if profitable else 99.0,
        pnl=1.0 if profitable else -1.0,
        profitable=profitable,
        features=feats,
    )


def test_no_trades_leaves_registry_untrained():
    reg = ModelRegistry()
    assert train_and_register([], reg) is False
    assert reg.is_trained is False
    prob, decision, explanation = predict({"a": 1.0}, reg)
    assert prob is None and decision is None and explanation is None
    assert reg.reason.startswith("insufficient_data")


def test_below_minimum_trades_stays_untrained():
    reg = ModelRegistry()
    trades = [_fake_trade(i, True, {"a": float(i), "b": 1.0}) for i in range(5)]
    assert train_and_register(trades, reg) is False
    assert reg.is_trained is False


def test_single_class_data_stays_untrained():
    """Even with 40 examples, a model can't be trained on one class only."""
    reg = ModelRegistry()
    trades = [_fake_trade(i, True, {"a": float(i), "b": 1.0}) for i in range(40)]
    assert train_and_register(trades, reg) is False
    assert reg.is_trained is False
    assert "single_class" in reg.reason


def test_sufficient_balanced_data_trains_and_predicts():
    reg = ModelRegistry()
    trades = []
    for i in range(20):
        trades.append(_fake_trade(i, True, {"a": 10.0 + i * 0.1, "b": 1.0}))
    for i in range(20):
        trades.append(_fake_trade(1000 + i, False, {"a": -10.0 - i * 0.1, "b": 1.0}))
    assert train_and_register(trades, reg) is True
    assert reg.is_trained is True
    assert reg.metrics["primary_model"] == "random_forest"
    prob, decision, explanation = predict({"a": 15.0, "b": 1.0}, reg)
    assert prob is not None and 0.0 <= prob <= 1.0
    assert decision in ("ACCEPT", "AVOID")
    assert isinstance(explanation, str) and len(explanation) > 0


def test_higher_feature_value_gives_higher_probability_when_positively_correlated():
    reg = ModelRegistry()
    trades = []
    for i in range(20):
        trades.append(_fake_trade(i, True, {"a": 5.0 + i, "b": 0.0}))
    for i in range(20):
        trades.append(_fake_trade(1000 + i, False, {"a": -5.0 - i, "b": 0.0}))
    assert train_and_register(trades, reg) is True
    high, _, _ = predict({"a": 30.0, "b": 0.0}, reg)
    low, _, _ = predict({"a": -30.0, "b": 0.0}, reg)
    assert high > low
