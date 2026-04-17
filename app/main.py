"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.database import (
    check_db_connection, close_db_connection, create_db_extensions,
)
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.integrations import mqtt
from app.workers.scheduler import shutdown_scheduler, start_scheduler

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_extensions()
    await mqtt.connect()
    start_scheduler()
    logger.info("Application startup complete: %s v%s", settings.APP_NAME, settings.APP_VERSION)

    yield

    shutdown_scheduler()
    await mqtt.disconnect()
    await close_db_connection()
    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/health", tags=["Health"])
async def health() -> dict:
    return {"status": "ok"}


@app.get("/readiness", tags=["Health"])
async def readiness() -> dict:
    db_ok = await check_db_connection()
    return {
        "status": "ready" if db_ok else "degraded",
        "database": "up" if db_ok else "down",
    }
