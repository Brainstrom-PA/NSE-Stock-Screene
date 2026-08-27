"""
Provider abstraction: BaseMarketDataProvider.

Any concrete provider (demo, Angel One, ...) must return `MarketTick`
objects. The rest of the pipeline depends only on this interface.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from .models import MarketTick


class BaseMarketDataProvider(ABC):
    """Abstract base for market-data providers."""

    #: Unique short name of the provider, e.g. "demo", "angel_one".
    name: str = "base"

    @abstractmethod
    def get_snapshot(self) -> List[MarketTick]:
        """Return the current normalized market snapshot for all tracked symbols."""
        raise NotImplementedError

    @abstractmethod
    def is_ready(self) -> bool:
        """Return True if the provider is initialised and can serve data."""
        raise NotImplementedError

    def describe(self) -> dict:
        """Human-readable description of the provider state."""
        return {"name": self.name, "ready": self.is_ready()}
