"""Train the crossover-profitability classifier.

Uses a time-aware 80/20 split (no random shuffling of future observations
into training data). Both models are always fit:

    * Logistic Regression — baseline + used for feature attribution in
      the explanation.
    * Random Forest       — primary classifier used for prediction.

When there aren't enough completed trades OR only one class is present,
the registry stays untrained and downstream code shows
"Insufficient training data" instead of a fake probability.
"""
from __future__ import annotations

import logging
import os
from typing import Iterable

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from app.ml.dataset import build_dataset
from app.ml.model_registry import ModelRegistry
from app.signals.trade_engine import CompletedTrade

logger = logging.getLogger(__name__)

MIN_TRAINING_EXAMPLES = int(os.environ.get("ML_MIN_TRAINING_EXAMPLES", "20"))


def train_and_register(
    trades: Iterable[CompletedTrade],
    registry: ModelRegistry,
) -> bool:
    """Fit LR + RF and register them. Returns True on success."""
    X, y, feature_names = build_dataset(list(trades))
    n = 0 if X is None else int(len(X))
    positives = int(y.sum()) if y is not None else 0
    negatives = n - positives

    if X is None or n < MIN_TRAINING_EXAMPLES:
        registry.mark_untrained(
            reason=f"insufficient_data (have {n}, need {MIN_TRAINING_EXAMPLES})",
            metrics={"available_examples": n, "positives": positives, "negatives": negatives},
        )
        return False
    if len(set(y.tolist())) < 2:
        registry.mark_untrained(
            reason="single_class_only (need both profitable and non-profitable trades)",
            metrics={"available_examples": n, "positives": positives, "negatives": negatives},
        )
        return False

    # Time-aware 80/20 split — build_dataset already sorts by exit_ts.
    split = max(1, int(n * 0.8))
    X_train, y_train = X[:split], y[:split]
    X_test, y_test = X[split:], y[split:]

    scaler = StandardScaler().fit(X_train)
    X_train_s = scaler.transform(X_train)

    lr = LogisticRegression(max_iter=1000, class_weight="balanced").fit(
        X_train_s, y_train
    )
    rf = RandomForestClassifier(
        n_estimators=100, class_weight="balanced", random_state=42
    ).fit(X_train, y_train)

    def _auc(model, X_eval, scaled: bool):
        if len(X_eval) == 0 or len(set(y_test.tolist())) < 2:
            return None
        try:
            X_use = scaler.transform(X_eval) if scaled else X_eval
            return float(roc_auc_score(y_test, model.predict_proba(X_use)[:, 1]))
        except Exception:
            return None

    metrics = {
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "positives": positives,
        "negatives": negatives,
        "auc_lr": _auc(lr, X_test, scaled=True),
        "auc_rf": _auc(rf, X_test, scaled=False),
        "primary_model": "random_forest",
        "baseline_model": "logistic_regression",
    }
    registry.register(
        rf=rf, lr=lr, scaler=scaler,
        feature_names=feature_names, metrics=metrics,
    )
    logger.info("ML trained: %s", metrics)
    return True
