"""LTQ moving-average helpers over rolling time windows."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, Optional


def avg_ltq_window(history: Iterable, minutes: int, now_ts: datetime) -> Optional[float]:
    """Return the average LTQ over the last `minutes` (None if empty)."""
    cutoff = now_ts - timedelta(minutes=minutes)
    values = [int(r.ltq) for r in history if r.ts >= cutoff]
    return sum(values) / len(values) if values else None
