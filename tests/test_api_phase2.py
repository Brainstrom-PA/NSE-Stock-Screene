"""Phase 2a API integration tests: SMMA/crossover on live /api/snapshot & /api/summary."""
import os
import re
from datetime import datetime, timezone, timedelta

import requests

def _read_frontend_env():
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError("REACT_APP_BACKEND_URL not set")


BASE = os.environ.get("REACT_APP_BACKEND_URL", _read_frontend_env()).rstrip("/")


ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


def test_snapshot_smma_populated():
    r = requests.get(f"{BASE}/api/snapshot", timeout=20)
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 20
    for row in rows:
        assert row["smma20"] is not None, f"{row['tick']['symbol']} smma20 null"
        assert row["smma120"] is not None, f"{row['tick']['symbol']} smma120 null"
        assert isinstance(row["smma20"], float)
        assert isinstance(row["smma120"], float)


def test_smma_close_to_ltp_but_lag():
    r = requests.get(f"{BASE}/api/snapshot", timeout=20)
    rows = r.json()
    for row in rows:
        ltp = row["tick"]["ltp"]
        # Within 25% of price (loose bound, mainly to catch order-of-magnitude bugs)
        assert abs(row["smma20"] - ltp) / ltp < 0.25
        assert abs(row["smma120"] - ltp) / ltp < 0.25


def test_signal_values_valid():
    r = requests.get(f"{BASE}/api/snapshot", timeout=20)
    rows = r.json()
    for row in rows:
        assert row["signal"] in (None, "BUY", "SELL")
        assert row["last_signal"] in (None, "BUY", "SELL")
        if row["last_signal"] is not None:
            assert row["last_signal_at"] is not None
            assert ISO_RE.match(row["last_signal_at"])


def test_summary_phase2_fields():
    r = requests.get(f"{BASE}/api/summary", timeout=20)
    assert r.status_code == 200
    d = r.json()
    assert d["signals_status"] == "SMMA(20)/SMMA(120) crossover live"
    assert isinstance(d["lifetime_signals"], int)
    assert isinstance(d["active_signals"], int)
    assert 0 <= d["active_signals"] <= 20


def test_active_signal_crossover_consistency():
    """When signal is BUY/SELL on this tick, last_signal == signal and last_signal_at is recent."""
    r = requests.get(f"{BASE}/api/snapshot", timeout=20)
    now = datetime.now(timezone.utc)
    for row in r.json():
        if row["signal"] is not None:
            assert row["last_signal"] == row["signal"]
            ts = datetime.fromisoformat(row["last_signal_at"].replace("Z", "+00:00"))
            assert now - ts < timedelta(seconds=60), f"stale last_signal_at for {row['tick']['symbol']}"


def test_pending_fields_still_none():
    r = requests.get(f"{BASE}/api/snapshot", timeout=20)
    for row in r.json():
        for k in ("etq_5m", "etq_20m", "etq_60m", "avg_ltp_20m", "avg_ltp_60m",
                  "ai_probability", "decision"):
            assert row[k] is None, f"{k} should be None for phase-2a"
