"""
Thin repository layer over SQLite.

Phase 1 exposes minimal helpers used by the pipeline / API.
"""
from __future__ import annotations

from typing import List

from .database import get_connection


def count_market_observations() -> int:
    """Return the total number of stored market observations."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM market_observations"
        ).fetchone()
        return int(row["n"]) if row else 0


def list_tables() -> List[str]:
    """Return the list of tables present in the SQLite database."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        return [r["name"] for r in rows]
