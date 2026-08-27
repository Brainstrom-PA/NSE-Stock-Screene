"""In-memory model registry.

Only ACTUALLY trained artefacts live here. When there is no trained
model, `is_trained` is False and downstream code MUST NOT invent fake
probabilities.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ModelRegistry:
    is_trained: bool = False
    rf: Any = None            # sklearn RandomForestClassifier (primary)
    lr: Any = None            # sklearn LogisticRegression (baseline + explanations)
    scaler: Any = None        # StandardScaler used only for LR / explanations
    feature_names: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    reason: str = "no_training_yet"

    def register(self, rf, lr, scaler, feature_names, metrics) -> None:
        self.rf = rf
        self.lr = lr
        self.scaler = scaler
        self.feature_names = list(feature_names)
        self.metrics = dict(metrics)
        self.is_trained = True
        self.reason = "trained"

    def mark_untrained(
        self, reason: str, metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        self.is_trained = False
        self.rf = None
        self.lr = None
        self.scaler = None
        self.feature_names = []
        self.metrics = dict(metrics or {})
        self.reason = reason

    def status(self) -> Dict[str, Any]:
        return {"trained": self.is_trained, "reason": self.reason, **self.metrics}


# Process-wide singleton.
registry = ModelRegistry()
