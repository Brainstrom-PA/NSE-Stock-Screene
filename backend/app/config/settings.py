"""
Central application settings.

All environment-driven configuration is resolved here.
The rest of the codebase must NOT read os.environ directly for behaviour
that could differ between demo/live mode.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent  # /app/backend
PROJECT_ROOT = BACKEND_ROOT.parent                            # /app
RUNTIME_DIR = PROJECT_ROOT / "data" / "runtime"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Settings:
    """Immutable application settings."""

    # "demo" | "live"
    data_mode: str = os.environ.get("DATA_MODE", "demo").strip().lower()

    # How often (seconds) the demo provider ticks new synthetic data.
    demo_tick_seconds: float = float(os.environ.get("DEMO_TICK_SECONDS", "2.0"))

    # SQLite database file (Phase 1 storage foundation).
    sqlite_path: Path = RUNTIME_DIR / "market_screener.sqlite3"

    # CORS
    cors_origins: str = os.environ.get("CORS_ORIGINS", "*")

    # Angel One (Phase 2). Never required in Phase 1.
    angel_api_key: str = os.environ.get("ANGEL_API_KEY", "")
    angel_client_id: str = os.environ.get("ANGEL_CLIENT_ID", "")

    @property
    def is_demo(self) -> bool:
        return self.data_mode == "demo"

    @property
    def is_live(self) -> bool:
        return self.data_mode == "live"


settings = Settings()
