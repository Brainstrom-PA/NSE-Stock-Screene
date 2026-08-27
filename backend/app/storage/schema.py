"""
SQLite schema definitions.

Tables are prepared for the FULL system but written to sparingly in
Phase 1. Phase 2/3 will populate the remaining ones.
"""
from __future__ import annotations


CREATE_STATEMENTS = [
    # Every observed market tick (Phase 2+ will stream into this).
    """
    CREATE TABLE IF NOT EXISTS market_observations (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol        TEXT NOT NULL,
        token         TEXT NOT NULL,
        exchange      TEXT NOT NULL,
        ts            TEXT NOT NULL,
        ltp           REAL NOT NULL,
        ltq           INTEGER NOT NULL,
        day_volume    INTEGER NOT NULL,
        bid_price     REAL NOT NULL,
        bid_quantity  INTEGER NOT NULL,
        ask_price     REAL NOT NULL,
        ask_quantity  INTEGER NOT NULL,
        source        TEXT NOT NULL
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_mo_symbol_ts ON market_observations(symbol, ts);",

    # Crossover events (Phase 2).
    """
    CREATE TABLE IF NOT EXISTS crossover_events (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol       TEXT NOT NULL,
        ts           TEXT NOT NULL,
        direction    TEXT NOT NULL,           -- BUY | SELL
        ltp_at_event REAL NOT NULL,
        smma20       REAL NOT NULL,
        smma120      REAL NOT NULL
    );
    """,

    # Trade outcomes derived from paired crossovers (Phase 2).
    """
    CREATE TABLE IF NOT EXISTS trade_outcomes (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol         TEXT NOT NULL,
        entry_ts       TEXT NOT NULL,
        exit_ts        TEXT NOT NULL,
        direction      TEXT NOT NULL,
        entry_ltp      REAL NOT NULL,
        exit_ltp       REAL NOT NULL,
        pnl            REAL NOT NULL,
        profitable     INTEGER NOT NULL       -- 0/1
    );
    """,

    # ML training examples (Phase 3).
    """
    CREATE TABLE IF NOT EXISTS ml_training_examples (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        crossover_id   INTEGER NOT NULL,
        features_json  TEXT NOT NULL,
        label          INTEGER NOT NULL,
        created_at     TEXT NOT NULL
    );
    """,

    # Model registry (Phase 3).
    """
    CREATE TABLE IF NOT EXISTS ml_models (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT NOT NULL,
        version       TEXT NOT NULL,
        artifact_path TEXT NOT NULL,
        metrics_json  TEXT NOT NULL,
        created_at    TEXT NOT NULL
    );
    """,
]
