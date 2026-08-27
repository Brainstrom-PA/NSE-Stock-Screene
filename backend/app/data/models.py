"""
Normalized market-data model.

Every provider (Demo, Angel One, ...) MUST produce this exact structure.
Downstream layers (screener, quant, ML, UI) depend only on this model,
never on broker-specific field names.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class MarketTick(BaseModel):
    """A single normalized market snapshot for one instrument."""

    model_config = ConfigDict(extra="ignore")

    # --- Identity ---
    symbol: str = Field(..., description="Trading symbol, e.g. RELIANCE")
    token: str = Field(..., description="Instrument token / exchange id")
    exchange: str = Field("NSE", description="Exchange code, e.g. NSE")

    # --- Timing ---
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the observation",
    )

    # --- Price / Trade ---
    ltp: float = Field(..., description="Last Traded Price (₹)")
    ltq: int = Field(0, description="Last Traded Quantity")
    day_volume: int = Field(0, description="Cumulative traded volume for the day")

    # --- Market depth: top-of-book ---
    bid_price: float = Field(0.0, description="Best bid price (₹)")
    bid_quantity: int = Field(0, description="Best bid aggregate quantity")
    ask_price: float = Field(0.0, description="Best ask price (₹)")
    ask_quantity: int = Field(0, description="Best ask aggregate quantity")

    # --- Metadata ---
    source: str = Field("demo", description="Data source: demo | angel_one")


class ScreenedStock(BaseModel):
    """A MarketTick augmented with screening pass/fail info."""

    tick: MarketTick
    price_qualified: bool
    liquidity_qualified: bool
    qualified: bool  # AND of the two above

    # Future fields (Phase 2+): explicitly None so consumers know
    # they are not yet implemented.
    smma20: Optional[float] = None
    smma120: Optional[float] = None
    etq_5m: Optional[float] = None
    etq_20m: Optional[float] = None
    etq_60m: Optional[float] = None
    avg_ltp_20m: Optional[float] = None
    avg_ltp_60m: Optional[float] = None
    signal: Optional[str] = None            # Fresh crossover EVENT on THIS tick.
    last_signal: Optional[str] = None       # Most recent BUY/SELL event ever seen for this symbol.
    last_signal_at: Optional[str] = None    # ISO timestamp of `last_signal`.
    ai_probability: Optional[float] = None
    decision: Optional[str] = None          # "ACCEPT" | "AVOID" | None (Pending)
