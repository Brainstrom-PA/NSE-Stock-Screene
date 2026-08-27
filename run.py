"""
Local runner for the AI Market Screener backend.

Usage:
    python run.py             # start FastAPI on http://127.0.0.1:8001
    python run.py --host 0.0.0.0 --port 8001

The React frontend is a separate process — see README.md.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make `app.*` importable without installing the package.
BACKEND = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Market Screener (Phase 1)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--reload", action="store_true", help="dev auto-reload")
    args = parser.parse_args()

    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
