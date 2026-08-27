"""
Supervisor entry-point.

Emergent's supervisord runs `uvicorn server:app` from /app/backend, so
this module simply re-exports the FastAPI application defined in
`app.main`. All routing, screening and demo simulation live there.
"""
from app.main import app  # re-export for `uvicorn server:app`

__all__ = ["app"]
