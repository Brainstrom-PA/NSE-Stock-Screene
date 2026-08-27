"""Plain-English ACCEPT/AVOID rationale built from REAL feature values.

Uses the logistic-regression baseline for directional attribution:
    per-feature log-odds contribution = scaled_feature × lr.coef_[feature]

The top |contributions| that support the model's decision drive a short,
concrete sentence — no random templates.
"""
from __future__ import annotations

from typing import Dict, Optional

import numpy as np

from app.ml.model_registry import ModelRegistry


# (positive-story, negative-story) tied to each real feature.
_FEATURE_STORIES = {
    "ltq_accel":       ("strong LTQ acceleration",             "weak LTQ acceleration"),
    "avg_ltq_2m":      ("elevated short-term trade size",      "quiet short-term trade size"),
    "avg_ltq_5m":      ("healthy 5-minute trade activity",     "low 5-minute trade activity"),
    "momentum":        ("positive price momentum vs 20m avg",  "negative price momentum vs 20m avg"),
    "return_1m":       ("recent price move supports the signal","recent price move against the signal"),
    "depth_imbalance": ("favourable market-depth imbalance",   "unfavourable market-depth imbalance"),
    "bid_ask_ratio":   ("bid-side pressure on the book",       "ask-side pressure on the book"),
    "volatility_20m":  ("low 20m realised volatility",         "elevated 20m volatility"),
    "etq_ratio_5_20":  ("rising volume vs 20m baseline",       "shrinking volume vs 20m baseline"),
    "etq_ratio_20_60": ("session-wide volume expansion",       "session-wide volume contraction"),
    "smma_spread_pct": ("wide SMMA spread confirming trend",   "narrow SMMA spread — weak trend"),
    "smma20_slope":    ("rising fast SMMA",                    "falling fast SMMA"),
    "spread":          ("tight bid-ask spread",                "wide bid-ask spread"),
}


def build_explanation(
    features: Dict[str, float],
    decision: str,
    probability: float,
    registry: ModelRegistry,
) -> Optional[str]:
    if not registry.is_trained or registry.lr is None or registry.scaler is None:
        return None
    names = registry.feature_names
    x = np.array([float(features.get(k, 0.0)) for k in names], dtype=float)
    scaled = (x - registry.scaler.mean_) / registry.scaler.scale_
    coefs = registry.lr.coef_[0]
    contribs = scaled * coefs  # log-odds contribution per feature

    if decision == "ACCEPT":
        order = np.argsort(-contribs)
        want_positive = True
    else:
        order = np.argsort(contribs)
        want_positive = False

    phrases = []
    for idx in order:
        if len(phrases) >= 2:
            break
        c = float(contribs[idx])
        if want_positive and c <= 0:
            continue
        if not want_positive and c >= 0:
            continue
        story = _FEATURE_STORIES.get(names[idx])
        if not story:
            continue
        phrases.append(story[0] if want_positive else story[1])

    pct = f"{probability * 100:.0f}% confidence"
    if not phrases:
        return f"{decision} at {pct}"
    return f"{decision}: " + " and ".join(phrases) + f" — {pct}"
