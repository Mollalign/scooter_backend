"""
Database Configuration Module
=============================
Async SQLAlchemy setup for PostgreSQL.
Production-ready with SSL support and clean session handling.
"""

import ssl
import logging
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy import text
from typing import AsyncGenerator

from app.core.config import settings
from app.models.base import Base

logger = logging.getLogger(__name__)


# =========================================
# SSL CONFIGURATION
# =========================================

def build_ssl_context():
    """Create SSL context for secure DB connections."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    return ssl_context


# =========================================
# ENGINE CONFIGURATION
# =========================================

def build_engine() -> AsyncEngine:
    """
    Build async SQLAlchemy engine with connection pooling
    and optional SSL (controlled via config).
    """
    engine_kwargs = {
        "echo": settings.DB_ECHO,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": 30,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }

    connect_args = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "server_settings": {
            "application_name": settings.APP_NAME,
        },
    }

    if getattr(settings, "DB_USE_SSL", False):
        connect_args["ssl"] = build_ssl_context()
        logger.info("SSL enabled for database connection")

    engine_kwargs["connect_args"] = connect_args

    return create_async_engine(settings.DATABASE_URL, **engine_kwargs)


engine: AsyncEngine = build_engine()


# ==========================================
# SESSION FACTORY
# ==========================================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ==========================================
# DATABASE DEPENDENCY (FASTAPI)
# ==========================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session per request."""
    async with AsyncSessionLocal() as session:
        yield session


# ==========================================
# DATABASE UTILITIES
# ==========================================

async def create_db_extensions() -> None:
    """Ensure required PostgreSQL extensions exist."""
    try:
        async with engine.begin() as conn:
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto";'))
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "postgis";'))
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "btree_gist";'))
        logger.info("PostgreSQL extensions ready.")
    except Exception as e:
        logger.error(f"Extension creation failed: {e}")
        raise


async def init_db() -> None:
    """
    Create all tables (DEV ONLY).
    In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created (dev mode).")


async def drop_all_tables() -> None:
    """Drop all tables (DEV ONLY — destructive)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("All tables dropped.")


async def check_db_connection() -> bool:
    """Health check — returns True if the database responds to SELECT 1."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


async def close_db_connection() -> None:
    """Dispose engine and close all pooled connections."""
    logger.info("Closing database connection pool...")
    await engine.dispose()
    logger.info("Database connection pool closed.")