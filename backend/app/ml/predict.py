"""Inference for a single crossover event.

Returns `(probability, decision, explanation)`. When the model has not
yet been trained returns `(None, None, None)` — the UI shows a plain
"Insufficient training data" instead of a fake probability.
"""
from __future__ import annotations

import os
from typing import Dict, Optional, Tuple

import numpy as np

from app.ml.explain import build_explanation
from app.ml.model_registry import ModelRegistry

# ACCEPT threshold — 0.60 per assignment, overridable via env for testing.
ML_THRESHOLD = float(os.environ.get("ML_THRESHOLD", "0.60"))


def predict(
    features: Dict[str, float],
    registry: ModelRegistry,
) -> Tuple[Optional[float], Optional[str], Optional[str]]:
    if not registry.is_trained:
        return None, None, None
    x = np.array(
        [[float(features.get(k, 0.0)) for k in registry.feature_names]],
        dtype=float,
    )
    prob = float(registry.rf.predict_proba(x)[0, 1])
    decision = "ACCEPT" if prob >= ML_THRESHOLD else "AVOID"
    explanation = build_explanation(features, decision, prob, registry)
    return prob, decision, explanation
