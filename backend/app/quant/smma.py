"""
Smoothed Moving Average (SMMA) — Phase 2 implementation.

Recurrence:
    SMMA_t = ((N - 1) * SMMA_(t-1) + Price_t) / N

Seeded with the simple mean of the first N prices, as is standard.
"""
from __future__ import annotations

from collections import deque
from typing import Iterable, Optional


class SMMACalculator:
    """Streaming SMMA over a given period.

    Feed it one `price` per bar via `update(price)`. Returns None while
    still warming up (fewer than `period` prices have been observed).
    """

    def __init__(self, period: int) -> None:
        if period <= 1:
            raise ValueError("period must be > 1")
        self.period = period
        self._warmup: deque[float] = deque(maxlen=period)
        self._value: Optional[float] = None

    @property
    def value(self) -> Optional[float]:
        return self._value

    @property
    def is_ready(self) -> bool:
        return self._value is not None

    def update(self, price: float) -> Optional[float]:
        if self._value is None:
            self._warmup.append(float(price))
            if len(self._warmup) == self.period:
                # Seed with simple mean of the first `period` prices.
                self._value = sum(self._warmup) / self.period
        else:
            self._value = (
                (self.period - 1) * self._value + float(price)
            ) / self.period
        return self._value


def smma(prices: Iterable[float], period: int) -> Optional[float]:
    """Convenience: compute the final SMMA value over an iterable of prices."""
    calc = SMMACalculator(period)
    result: Optional[float] = None
    for p in prices:
        result = calc.update(p)
    return result
