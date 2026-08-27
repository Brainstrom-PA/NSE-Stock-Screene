"""Turn completed crossover trades into a chronologically-ordered (X, y) dataset."""
from __future__ import annotations

from typing import Iterable, List, Optional, Tuple

import numpy as np

from app.signals.trade_engine import CompletedTrade


def build_dataset(
    trades: Iterable[CompletedTrade],
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], List[str]]:
    """Return `(X, y, feature_names)` sorted by exit_ts (time-aware order)."""
    ordered = sorted(trades, key=lambda t: t.exit_ts)
    if not ordered:
        return None, None, []
    feature_names = sorted(ordered[0].features.keys())
    X = np.array(
        [[float(t.features.get(k, 0.0)) for k in feature_names] for t in ordered],
        dtype=float,
    )
    y = np.array([1 if t.profitable else 0 for t in ordered], dtype=int)
    return X, y, feature_names
