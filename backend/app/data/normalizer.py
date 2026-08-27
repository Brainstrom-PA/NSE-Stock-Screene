"""
Normalization helpers.

Converts broker-specific payloads into our normalized `MarketTick`.
Only demo normalization is implemented in Phase 1; Angel One's
normalizer is a placeholder.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from .models import MarketTick


def normalize_demo_tick(raw: Dict[str, Any]) -> MarketTick:
    """Pass-through normalizer for demo data (already in canonical shape)."""
    return MarketTick(**raw)


def normalize_angel_one_tick(raw: Dict[str, Any]) -> MarketTick:  # pragma: no cover
    """
    Phase 2: convert an Angel One SmartAPI WebSocket frame into a MarketTick.

    Left as a stub in Phase 1 so nothing silently pretends to work.
    """
    raise NotImplementedError(
        "Angel One tick normalization is scheduled for Phase 2."
    )
