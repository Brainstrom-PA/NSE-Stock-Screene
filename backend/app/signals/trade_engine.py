"""Crossover trade tracking + realised P/L bookkeeping.

BUY crossover  → open BUY  trade. Closed by next SELL: P/L = exit − entry.
SELL crossover → open SELL trade. Closed by next BUY:  P/L = entry − exit.
Profitable = P/L > 0.

Features are captured at ENTRY time only, never using future information.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class OpenTrade:
    symbol: str
    direction: str          # "BUY" | "SELL"
    entry_ts: str           # ISO 8601 string
    entry_price: float
    features: Dict[str, float]


@dataclass
class CompletedTrade:
    symbol: str
    direction: str          # direction of the ENTRY leg
    entry_ts: str
    exit_ts: str
    entry_price: float
    exit_price: float
    pnl: float
    profitable: bool
    features: Dict[str, float]   # captured at ENTRY time


class TradeTracker:
    """Per-universe tracker of open + completed crossover trades."""

    def __init__(self) -> None:
        self.open: Dict[str, OpenTrade] = {}
        self.completed: List[CompletedTrade] = []

    def record_crossover(
        self,
        symbol: str,
        direction: str,
        ts_iso: str,
        price: float,
        features: Dict[str, float],
    ) -> Optional[CompletedTrade]:
        """Record a crossover; close a previous OPPOSITE-direction trade if
        one exists, and open a fresh trade in the new direction.

        Returns the newly completed trade (or None if no trade closed).
        Same-direction repeats are ignored so a single event is never
        double-counted.
        """
        completed: Optional[CompletedTrade] = None
        prev = self.open.get(symbol)
        if prev is not None and prev.direction != direction:
            if prev.direction == "BUY":
                pnl = price - prev.entry_price
            else:  # SELL
                pnl = prev.entry_price - price
            completed = CompletedTrade(
                symbol=symbol,
                direction=prev.direction,
                entry_ts=prev.entry_ts,
                exit_ts=ts_iso,
                entry_price=prev.entry_price,
                exit_price=price,
                pnl=pnl,
                profitable=pnl > 0,
                features=prev.features,
            )
            self.completed.append(completed)
        elif prev is not None and prev.direction == direction:
            # Same-direction repeat — keep the original entry, no P/L.
            return None
        self.open[symbol] = OpenTrade(
            symbol=symbol,
            direction=direction,
            entry_ts=ts_iso,
            entry_price=price,
            features=features,
        )
        return completed
