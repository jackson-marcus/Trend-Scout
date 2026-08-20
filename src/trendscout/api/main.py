"""FastAPI application factory."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from trendscout import __version__
from trendscout.api.routes import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def create_app() -> FastAPI:
    app = FastAPI(
        title="trendscout",
        description="News intelligence: RSS ingestion, near-duplicate detection, online story clustering, burst-based trend detection, and a cited daily-brief writing agent.",
        version=__version__,
    )
    app.include_router(router)
    return app


app = create_app()
