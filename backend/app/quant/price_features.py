"""Rolling price statistics (avg LTP, volatility, historical price lookup)."""
from __future__ import annotations

import statistics
from datetime import datetime, timedelta
from typing import Iterable, List, Optional


def avg_ltp_window(history: Iterable, minutes: int, now_ts: datetime) -> Optional[float]:
    """Arithmetic mean of LTP values over the last `minutes` (None if empty)."""
    cutoff = now_ts - timedelta(minutes=minutes)
    values = [float(r.ltp) for r in history if r.ts >= cutoff]
    return sum(values) / len(values) if values else None


def volatility_pct_window(
    history: Iterable, minutes: int, now_ts: datetime
) -> Optional[float]:
    """Population std-dev of tick-to-tick returns within the window.

    Returns None when there are fewer than 3 records in the window.
    """
    cutoff = now_ts - timedelta(minutes=minutes)
    window = [r for r in history if r.ts >= cutoff]
    if len(window) < 3:
        return None
    returns: List[float] = []
    for i in range(1, len(window)):
        prev = float(window[i - 1].ltp)
        if prev > 0:
            returns.append((float(window[i].ltp) - prev) / prev)
    if len(returns) < 2:
        return None
    return statistics.pstdev(returns)


def ltp_at_or_before(history: Iterable, target_ts: datetime) -> Optional[float]:
    """Most recent LTP whose timestamp <= `target_ts`, or None."""
    result: Optional[float] = None
    for r in history:
        if r.ts <= target_ts:
            result = float(r.ltp)
        else:
            break
    return result
