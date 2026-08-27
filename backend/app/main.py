"""
FastAPI application factory for the AI Market Screening system (Phase 1).

Exposes the following endpoints under the `/api` prefix required by the
Emergent Kubernetes ingress:

    GET  /api/health           - liveness probe
    GET  /api/source           - current data-source description
    GET  /api/universe         - the full demo instrument universe
    GET  /api/snapshot         - one screened market snapshot
    GET  /api/summary          - counts used by the dashboard KPI cards
    GET  /api/stock/{symbol}   - detailed info for a single symbol
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path

from app.config.settings import settings
from app.data.models import ScreenedStock
from app.services.pipeline import pipeline
from app.storage.database import initialise_database
from app.storage.repositories import list_tables


# Load /app/backend/.env if present.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ai_market_screener")


app = FastAPI(
    title="AI Market Screening (Phase 1)",
    description=(
        "NSE stock screening and quantitative-analysis foundation. "
        "Phase 1 runs in DEMO / SIMULATED mode."
    ),
    version="0.1.0",
)

api_router = APIRouter(prefix="/api")


# --- Endpoints --------------------------------------------------------------


@api_router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-market-screener",
        "version": "0.1.0",
        "time": datetime.now(timezone.utc).isoformat(),
    }


@api_router.get("/source")
def source():
    """Metadata about the active data source (DEMO or LIVE)."""
    src = pipeline.describe_source()
    src["storage_tables"] = list_tables()
    return src


@api_router.get("/universe")
def universe():
    """Return the full raw demo universe (initial ticks, no screening)."""
    return [t.model_dump(mode="json") for t in pipeline.provider.get_snapshot()]


@api_router.get("/snapshot", response_model=List[ScreenedStock])
def snapshot():
    """Return one screened market snapshot."""
    return pipeline.run_once()


@api_router.get("/summary")
def summary():
    """KPI counts used by the dashboard summary cards."""
    screened = pipeline.run_once()
    price_ok = sum(1 for s in screened if s.price_qualified)
    liq_ok = sum(1 for s in screened if s.liquidity_qualified)
    both_ok = sum(1 for s in screened if s.qualified)
    active = sum(1 for s in screened if s.signal is not None)
    lifetime = sum(1 for s in screened if s.last_signal is not None)
    return {
        "nse_universe": len(screened),
        "price_qualified": price_ok,
        "liquidity_qualified": liq_ok,
        "fully_qualified": both_ok,
        "active_signals": active,                    # events fired on THIS tick
        "lifetime_signals": lifetime,                # symbols with ANY past event
        "signals_status": "SMMA(20)/SMMA(120) crossover live",
        "as_of": datetime.now(timezone.utc).isoformat(),
    }


@api_router.get("/stock/{symbol}", response_model=ScreenedStock)
def stock_detail(symbol: str):
    screened = pipeline.run_once()
    for s in screened:
        if s.tick.symbol.upper() == symbol.upper():
            return s
    raise HTTPException(status_code=404, detail=f"Symbol {symbol!r} not found")


app.include_router(api_router)


# --- CORS -------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Lifecycle --------------------------------------------------------------


@app.on_event("startup")
def _startup() -> None:
    initialise_database()
    logger.info("AI Market Screener started — mode=%s", settings.data_mode)


@app.on_event("shutdown")
def _shutdown() -> None:
    logger.info("AI Market Screener stopped.")
