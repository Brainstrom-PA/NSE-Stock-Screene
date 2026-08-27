"""Effective Traded Quantity (ETQ) — sum of LTQ over a rolling time window.

ETQ MUST NOT be day_volume. It is the sum of the LTQ values in every tick
whose timestamp falls within the last N minutes.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable


def etq_window(history: Iterable, minutes: int, now_ts: datetime) -> int:
    """Return the sum of `record.ltq` for records with `ts >= now_ts - minutes`."""
    cutoff = now_ts - timedelta(minutes=minutes)
    return sum(int(r.ltq) for r in history if r.ts >= cutoff)
