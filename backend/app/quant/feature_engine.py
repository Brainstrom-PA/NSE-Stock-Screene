"""Feature engineering for the ML profitability model.

Every feature is computed from information available AT the moment of the
crossover event. No forward-looking data is ever used.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Iterable, Optional

from app.quant.etq import etq_window
from app.quant.ltq import avg_ltq_window
from app.quant.price_features import (
    avg_ltp_window,
    ltp_at_or_before,
    volatility_pct_window,
)


def _safe_div(a: float, b: float, default: float = 0.0) -> float:
    """Division that returns `default` on zero-denominator."""
    return (a / b) if b else default


def build_features(
    history: Iterable,
    now_ts: datetime,
    latest,                              # duck-typed TickRecord
    smma_fast: Optional[float],
    smma_slow: Optional[float],
    smma_fast_slope_pct: float,
    direction: str,
) -> Dict[str, float]:
    """Return the 20-element feature dict used by training + inference."""
    avg_ltq_2m = avg_ltq_window(history, 2, now_ts) or 0.0
    avg_ltq_5m = avg_ltq_window(history, 5, now_ts) or 0.0
    etq_5m = etq_window(history, 5, now_ts)
    etq_20m = etq_window(history, 20, now_ts)
    etq_60m = etq_window(history, 60, now_ts)
    ltp_1m_ago = ltp_at_or_before(history, now_ts - timedelta(minutes=1))
    avg_ltp_20m = avg_ltp_window(history, 20, now_ts) or float(latest.ltp)
    volatility_20m = volatility_pct_window(history, 20, now_ts) or 0.0
    smma_diff = (smma_fast or 0.0) - (smma_slow or 0.0)
    return_1m = (
        _safe_div(float(latest.ltp) - float(ltp_1m_ago), float(ltp_1m_ago))
        if ltp_1m_ago
        else 0.0
    )
    return {
        "ltq": float(latest.ltq),
        "avg_ltq_2m": avg_ltq_2m,
        "avg_ltq_5m": avg_ltq_5m,
        "ltq_ratio_2m_5m": _safe_div(avg_ltq_2m, avg_ltq_5m),
        "ltq_accel": _safe_div(avg_ltq_2m - avg_ltq_5m, avg_ltq_5m),
        "etq_5m": float(etq_5m),
        "etq_20m": float(etq_20m),
        "etq_60m": float(etq_60m),
        "etq_ratio_5_20": _safe_div(etq_5m, etq_20m),
        "etq_ratio_20_60": _safe_div(etq_20m, etq_60m),
        "return_1m": return_1m,
        "momentum": _safe_div(float(latest.ltp) - avg_ltp_20m, avg_ltp_20m),
        "volatility_20m": float(volatility_20m),
        "smma_diff": float(smma_diff),
        "smma_spread_pct": _safe_div(smma_diff, smma_slow or 1.0),
        "smma20_slope": float(smma_fast_slope_pct),
        "bid_ask_ratio": _safe_div(
            float(latest.bid_quantity), float(latest.ask_quantity)
        ),
        "depth_imbalance": _safe_div(
            float(latest.bid_quantity - latest.ask_quantity),
            float(latest.bid_quantity + latest.ask_quantity),
        ),
        "spread": float(latest.ask_price - latest.bid_price),
        "signal_direction": 1.0 if direction == "BUY" else -1.0,
    }
