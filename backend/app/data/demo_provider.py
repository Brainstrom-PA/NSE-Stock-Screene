"""
DemoMarketDataProvider — Phase 1 fully-functional simulator.

Produces deterministic-random walks on top of the seed instrument master
so the dashboard visibly "moves" every tick while remaining reproducible
within a single process.

IMPORTANT: This provider is clearly labelled `source="demo"` on every
tick. The UI displays this. Simulated data must NEVER be presented
as real market data.
"""
from __future__ import annotations

import random
import threading
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from .base_provider import BaseMarketDataProvider
from .instrument_master import DEMO_UNIVERSE, DemoInstrument
from .models import MarketTick


class DemoMarketDataProvider(BaseMarketDataProvider):
    """A synthetic, thread-safe market-data provider for Phase 1."""

    name = "demo"

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)
        self._lock = threading.Lock()
        self._state: Dict[str, MarketTick] = {}
        self._day_volume: Dict[str, int] = {}
        self._bootstrap()

    # --- Public API --------------------------------------------------------

    def is_ready(self) -> bool:
        return len(self._state) > 0

    def get_snapshot(self) -> List[MarketTick]:
        """Advance the simulation one tick and return the current snapshot."""
        with self._lock:
            self._step()
            return list(self._state.values())

    def simulate_backdated_snapshots(
        self, count: int, interval_seconds: float
    ) -> List[List[MarketTick]]:
        """Return `count` full-universe snapshots with backdated timestamps.

        Used at startup so demo mode has ~60 minutes of ETQ / avg-LTP
        history available on the very first API call, and so a few
        crossovers accumulate for the ML model. RNG state advances
        normally — the "live" simulation continues from where this stops.
        """
        end = datetime.now(timezone.utc)
        snapshots: List[List[MarketTick]] = []
        with self._lock:
            for i in range(count):
                ts = end - timedelta(seconds=(count - i - 1) * interval_seconds)
                self._step(ts)
                snapshots.append(list(self._state.values()))
        return snapshots

    # --- Internals ---------------------------------------------------------

    def _bootstrap(self) -> None:
        for inst in DEMO_UNIVERSE:
            self._state[inst.symbol] = self._make_initial_tick(inst)
            self._day_volume[inst.symbol] = self._rng.randint(50_000, 500_000)

    def _make_initial_tick(self, inst: DemoInstrument) -> MarketTick:
        spread = max(0.05, round(inst.base_price * 0.0005, 2))
        return MarketTick(
            symbol=inst.symbol,
            token=inst.token,
            exchange="NSE",
            timestamp=datetime.now(timezone.utc),
            ltp=round(inst.base_price, 2),
            ltq=self._rng.randint(50, 800),
            day_volume=0,
            bid_price=round(inst.base_price - spread, 2),
            bid_quantity=inst.base_bid_qty,
            ask_price=round(inst.base_price + spread, 2),
            ask_quantity=inst.base_ask_qty,
            source="demo",
        )

    def _step(self, ts: Optional[datetime] = None) -> None:
        """Advance every instrument by one small random step.

        When `ts` is provided it is used as the tick's timestamp instead of
        `now()`; this lets the pipeline seed backdated historical ticks so
        the ETQ / avg-LTP rolling windows are populated immediately.
        """
        now = ts if ts is not None else datetime.now(timezone.utc)
        for inst in DEMO_UNIVERSE:
            prev = self._state[inst.symbol]

            # Price random walk, mean-reverting to base_price.
            pct = self._rng.uniform(-0.004, 0.004)
            drift = (inst.base_price - prev.ltp) * 0.02
            new_ltp = max(0.05, round(prev.ltp * (1 + pct) + drift, 2))

            spread = max(0.05, round(new_ltp * 0.0005, 2))
            bid_price = round(new_ltp - spread, 2)
            ask_price = round(new_ltp + spread, 2)

            # Liquidity jitter around the base values (+/- 10%).
            bid_qty = max(0, int(inst.base_bid_qty * self._rng.uniform(0.9, 1.1)))
            ask_qty = max(0, int(inst.base_ask_qty * self._rng.uniform(0.9, 1.1)))

            ltq = self._rng.randint(20, 900)
            self._day_volume[inst.symbol] += ltq

            self._state[inst.symbol] = MarketTick(
                symbol=inst.symbol,
                token=inst.token,
                exchange="NSE",
                timestamp=now,
                ltp=new_ltp,
                ltq=ltq,
                day_volume=self._day_volume[inst.symbol],
                bid_price=bid_price,
                bid_quantity=bid_qty,
                ask_price=ask_price,
                ask_quantity=ask_qty,
                source="demo",
            )
