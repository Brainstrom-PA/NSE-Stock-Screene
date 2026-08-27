"""
Pipeline service.

provider → screener → SMMA → crossover → trade tracking → ML prediction.

Owns the ONLY market-data provider, per-symbol tick history + SMMA
state, the TradeTracker (BUY/SELL P/L bookkeeping) and the ML model
registry. Populates every downstream field on `ScreenedStock`
(ETQ / avg-LTP / signal / ai_probability / decision / explanation).
"""
from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Deque, Dict, List, Optional, Tuple

from app.config.settings import settings
from app.data.base_provider import BaseMarketDataProvider
from app.data.demo_provider import DemoMarketDataProvider
from app.data.angel_one_provider import AngelOneMarketDataProvider
from app.data.models import MarketTick, ScreenedStock
from app.screening.screener import screen_universe
from app.quant.smma import SMMACalculator
from app.quant.etq import etq_window
from app.quant.price_features import avg_ltp_window
from app.quant.feature_engine import build_features
from app.signals.crossover import detect_crossover
from app.signals.trade_engine import TradeTracker
from app.ml.model_registry import registry
from app.ml.train import train_and_register
from app.ml.predict import predict

logger = logging.getLogger(__name__)


SMMA_FAST_PERIOD = 20
SMMA_SLOW_PERIOD = 120
HISTORY_MAX_MINUTES = 60
DEMO_SEED_MINUTES = 60
RETRAIN_EVERY_N_TRADES = 5


@dataclass
class TickRecord:
    """Minimal in-memory tick used by the rolling windows."""
    ts: datetime
    ltp: float
    ltq: int
    bid_price: float
    bid_quantity: int
    ask_price: float
    ask_quantity: int


@dataclass
class SymbolState:
    """Per-symbol streaming state (SMMA + history + last prediction)."""

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
    history: Deque[TickRecord] = field(default_factory=lambda: deque(maxlen=2500))
    smma_fast_history: Deque[Tuple[datetime, float]] = field(
        default_factory=lambda: deque(maxlen=200)
    )
    # Persisted between crossovers so the UI keeps showing the latest prediction.
    last_ai_probability: Optional[float] = None
    last_decision: Optional[str] = None
    last_explanation: Optional[str] = None

    def step(
        self, tick: MarketTick
    ) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """Advance one bar: append history (trim >60m), update SMMAs, detect event."""
        self.history.append(TickRecord(
            ts=tick.timestamp, ltp=tick.ltp, ltq=tick.ltq,
            bid_price=tick.bid_price, bid_quantity=tick.bid_quantity,
            ask_price=tick.ask_price, ask_quantity=tick.ask_quantity,
        ))
        cutoff = tick.timestamp - timedelta(minutes=HISTORY_MAX_MINUTES)
        while self.history and self.history[0].ts < cutoff:
            self.history.popleft()

        curr_fast = self.smma_fast.update(tick.ltp)
        curr_slow = self.smma_slow.update(tick.ltp)
        if curr_fast is not None:
            self.smma_fast_history.append((tick.timestamp, curr_fast))
        event = detect_crossover(self.prev_fast, self.prev_slow, curr_fast, curr_slow)
        if event is not None:
            self.last_signal = event
            self.last_signal_at = tick.timestamp.isoformat()
        self.prev_fast = curr_fast
        self.prev_slow = curr_slow
        return curr_fast, curr_slow, event

    def smma_fast_slope_pct(self, minutes: int = 5) -> float:
        """(latest - old) / |old| where `old` is the fast SMMA `minutes` ago."""
        if len(self.smma_fast_history) < 2:
            return 0.0
        latest_ts, latest_val = self.smma_fast_history[-1]
        target = latest_ts - timedelta(minutes=minutes)
        old_val: Optional[float] = None
        for ts, v in self.smma_fast_history:
            if ts <= target:
                old_val = v
            else:
                break
        if old_val is None or old_val == 0:
            return 0.0
        return (latest_val - old_val) / abs(old_val)


def _build_provider() -> BaseMarketDataProvider:
    if settings.is_live:
        return AngelOneMarketDataProvider()
    return DemoMarketDataProvider()


class Pipeline:
    """provider → screener → SMMA → crossover → trades → ML."""

    def __init__(self) -> None:
        self.provider: BaseMarketDataProvider = _build_provider()
        self._states: Dict[str, SymbolState] = {}
        self.trades = TradeTracker()
        self._new_completed_since_train = 0

        if isinstance(self.provider, DemoMarketDataProvider):
            self._seed_from_history()

    # ---- Startup seeding --------------------------------------------------

    def _seed_from_history(self) -> None:
        """Pre-seed each symbol with `DEMO_SEED_MINUTES` of backdated ticks.

        This gives the ETQ / avg-LTP windows real values on the first API
        response and lets a few crossovers accumulate for initial ML
        training. Nothing here is fabricated — the same simulator that
        drives the live loop drives the seed.
        """
        count = int((DEMO_SEED_MINUTES * 60) / settings.demo_tick_seconds)
        snapshots = self.provider.simulate_backdated_snapshots(
            count=count, interval_seconds=settings.demo_tick_seconds
        )
        for snap in snapshots:
            for tick in snap:
                st = self._states.setdefault(tick.symbol, SymbolState())
                _f, _s, event = st.step(tick)
                if event is not None:
                    self._on_crossover(st, tick, event)
        train_and_register(self.trades.completed, registry)
        self._new_completed_since_train = 0
        logger.info(
            "Seeded %d symbols with %dm history — %d completed trades, model_trained=%s",
            len(self._states), DEMO_SEED_MINUTES,
            len(self.trades.completed), registry.is_trained,
        )

    # ---- Event handling ---------------------------------------------------

    def _on_crossover(self, st: SymbolState, tick: MarketTick, event: str) -> None:
        features = build_features(
            history=st.history,
            now_ts=tick.timestamp,
            latest=st.history[-1],
            smma_fast=st.prev_fast,
            smma_slow=st.prev_slow,
            smma_fast_slope_pct=st.smma_fast_slope_pct(5),
            direction=event,
        )
        completed = self.trades.record_crossover(
            symbol=tick.symbol,
            direction=event,
            ts_iso=tick.timestamp.isoformat(),
            price=tick.ltp,
            features=features,
        )
        if completed is not None:
            self._new_completed_since_train += 1
        prob, decision, expl = predict(features, registry)
        st.last_ai_probability = prob
        st.last_decision = decision
        st.last_explanation = expl

    def _maybe_retrain(self) -> None:
        if self._new_completed_since_train < RETRAIN_EVERY_N_TRADES:
            return
        trained = train_and_register(self.trades.completed, registry)
        self._new_completed_since_train = 0
        if not trained:
            return
        # Refresh predictions for open trades so the UI reflects the new model.
        for symbol, open_trade in self.trades.open.items():
            st = self._states.get(symbol)
            if st is None:
                continue
            p, d, e = predict(open_trade.features, registry)
            st.last_ai_probability = p
            st.last_decision = d
            st.last_explanation = e

    # ---- Public API -------------------------------------------------------

    def run_once(self) -> List[ScreenedStock]:
        """Fetch → screen → SMMA → crossover → trades → ML → populate."""
        ticks = self.provider.get_snapshot()
        screened = screen_universe(ticks)
        for s in screened:
            st = self._states.setdefault(s.tick.symbol, SymbolState())
            curr_fast, curr_slow, event = st.step(s.tick)
            s.smma20 = round(curr_fast, 2) if curr_fast is not None else None
            s.smma120 = round(curr_slow, 2) if curr_slow is not None else None
            now_ts = s.tick.timestamp
            s.etq_5m = etq_window(st.history, 5, now_ts)
            s.etq_20m = etq_window(st.history, 20, now_ts)
            s.etq_60m = etq_window(st.history, 60, now_ts)
            avg20 = avg_ltp_window(st.history, 20, now_ts)
            avg60 = avg_ltp_window(st.history, 60, now_ts)
            s.avg_ltp_20m = round(avg20, 2) if avg20 is not None else None
            s.avg_ltp_60m = round(avg60, 2) if avg60 is not None else None
            s.signal = event
            s.last_signal = st.last_signal
            s.last_signal_at = st.last_signal_at
            if event is not None:
                self._on_crossover(st, s.tick, event)
            s.ai_probability = st.last_ai_probability
            s.decision = st.last_decision
            s.explanation = st.last_explanation
        self._maybe_retrain()
        return screened

    def describe_source(self) -> dict:
        return {
            "mode": settings.data_mode,
            "provider": self.provider.name,
            "ready": self.provider.is_ready(),
            "label": "DEMO / SIMULATED" if settings.is_demo else "LIVE",
            "model": registry.status(),
            "completed_trades": len(self.trades.completed),
        }


# Process-wide singleton.
pipeline = Pipeline()
