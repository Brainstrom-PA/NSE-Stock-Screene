"""
Pipeline service.

Wires provider → screener → quant (SMMA) → signal engine (crossover)
together. It owns the ONLY instance of the market-data provider and the
ONLY in-memory per-symbol state used by the process.

Phase 2 additions: streaming SMMA(20)/SMMA(120) and BUY/SELL crossover
event detection. Downstream ML / decision layers still stubbed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from app.config.settings import settings
from app.data.base_provider import BaseMarketDataProvider
from app.data.demo_provider import DemoMarketDataProvider
from app.data.angel_one_provider import AngelOneMarketDataProvider
from app.data.models import ScreenedStock
from app.screening.screener import screen_universe
from app.quant.smma import SMMACalculator
from app.signals.crossover import detect_crossover


SMMA_FAST_PERIOD = 20
SMMA_SLOW_PERIOD = 120
# 150 ticks pre-warm ensures SMMA120 is initialised before the first API call.
DEMO_WARMUP_TICKS = 150


@dataclass
class SymbolState:
    """Per-symbol streaming state (SMMA calculators + last crossover)."""

    smma_fast: SMMACalculator = field(
        default_factory=lambda: SMMACalculator(SMMA_FAST_PERIOD)
    )
    smma_slow: SMMACalculator = field(
        default_factory=lambda: SMMACalculator(SMMA_SLOW_PERIOD)
    )
    prev_fast: Optional[float] = None
    prev_slow: Optional[float] = None
    last_signal: Optional[str] = None
    last_signal_at: Optional[str] = None

    def step(
        self, price: float
    ) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """Advance one bar. Returns (fast, slow, fresh_event_or_None)."""
        curr_fast = self.smma_fast.update(price)
        curr_slow = self.smma_slow.update(price)
        event = detect_crossover(
            self.prev_fast, self.prev_slow, curr_fast, curr_slow
        )
        if event is not None:
            self.last_signal = event
            self.last_signal_at = datetime.now(timezone.utc).isoformat()
        self.prev_fast = curr_fast
        self.prev_slow = curr_slow
        return curr_fast, curr_slow, event


def _build_provider() -> BaseMarketDataProvider:
    """Pick the provider implementation based on DATA_MODE."""
    if settings.is_live:
        return AngelOneMarketDataProvider()  # Phase 2b — will raise if used.
    return DemoMarketDataProvider()


class Pipeline:
    """provider → screener → SMMA → crossover."""

    def __init__(self) -> None:
        self.provider: BaseMarketDataProvider = _build_provider()
        self._states: Dict[str, SymbolState] = {}
        # In demo mode, pre-warm so SMMA120 is meaningful on the first call.
        if isinstance(self.provider, DemoMarketDataProvider):
            self._warmup(DEMO_WARMUP_TICKS)

    def _warmup(self, ticks: int) -> None:
        for _ in range(ticks):
            for t in self.provider.get_snapshot():
                st = self._states.setdefault(t.symbol, SymbolState())
                st.step(t.ltp)

    def run_once(self) -> List[ScreenedStock]:
        """One synchronous pass: fetch → screen → SMMA → crossover."""
        ticks = self.provider.get_snapshot()
        screened = screen_universe(ticks)
        for s in screened:
            st = self._states.setdefault(s.tick.symbol, SymbolState())
            curr_fast, curr_slow, event = st.step(s.tick.ltp)
            s.smma20 = round(curr_fast, 2) if curr_fast is not None else None
            s.smma120 = round(curr_slow, 2) if curr_slow is not None else None
            s.signal = event
            s.last_signal = st.last_signal
            s.last_signal_at = st.last_signal_at
        return screened

    def describe_source(self) -> dict:
        """Metadata about the current data source (shown in the UI header)."""
        return {
            "mode": settings.data_mode,
            "provider": self.provider.name,
            "ready": self.provider.is_ready(),
            "label": "DEMO / SIMULATED" if settings.is_demo else "LIVE (Phase 2)",
        }


# Process-wide singleton.
pipeline = Pipeline()
