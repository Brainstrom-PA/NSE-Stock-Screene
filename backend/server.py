"""
Application entry-point for the FastAPI service.

The FastAPI application is defined in app.main and re-exported here
for the ASGI server entry-point.
"""

from app.main import app

__all__ = ["app"]
