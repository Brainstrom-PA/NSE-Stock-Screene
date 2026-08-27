"""
Lightweight SQLite storage foundation.

Phase 1 only sets up the connection, schema and thin repository layer.
No heavy write-path is enabled yet — the goal is to prove the storage
architecture works and to let Phase 2 plug in without redesign.
"""
from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

from app.config.settings import settings
from .schema import CREATE_STATEMENTS


_lock = threading.Lock()
_initialised = False


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def initialise_database() -> None:
    """Create tables if they don't exist. Idempotent."""
    global _initialised
    with _lock:
        if _initialised:
            return
        _ensure_parent(settings.sqlite_path)
        with sqlite3.connect(settings.sqlite_path) as conn:
            for stmt in CREATE_STATEMENTS:
                conn.execute(stmt)
            conn.commit()
        _initialised = True


@contextmanager
def get_connection():
    """Yield a short-lived sqlite3.Connection (thread-local pattern)."""
    if not _initialised:
        initialise_database()
    conn = sqlite3.connect(settings.sqlite_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
