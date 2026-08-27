"""
AngelOneMarketDataProvider — Phase 2 INTEGRATION BOUNDARY (stub).

This module defines the *interface* only. It does NOT connect to Angel One
and does NOT require any credentials in Phase 1.

When Phase 2 is implemented, this class will:

  1. Authenticate via SmartAPI using ANGEL_API_KEY / CLIENT_ID / PASSWORD / TOTP.
  2. Subscribe to a market-data WebSocket feed.
  3. Convert every Angel One frame into a `MarketTick` via
     `app.data.normalizer.normalize_angel_one_tick`.
  4. Expose the same `get_snapshot()` contract as the demo provider.

The rest of the application will not require any code changes when
this provider is switched on via `DATA_MODE=live`.
"""
from __future__ import annotations

from typing import List

from .base_provider import BaseMarketDataProvider
from .models import MarketTick


class AngelOneMarketDataProvider(BaseMarketDataProvider):
    """Placeholder Angel One provider — NOT implemented in Phase 1."""

    name = "angel_one"

    def __init__(self) -> None:
        # Deliberately do nothing. No credentials are read here in Phase 1.
        self._connected = False

    def is_ready(self) -> bool:
        return False  # Never ready in Phase 1.

    def get_snapshot(self) -> List[MarketTick]:
        raise NotImplementedError(
            "AngelOneMarketDataProvider is a Phase 2 integration boundary. "
            "Phase 1 uses the DemoMarketDataProvider. Set DATA_MODE=demo."
        )
