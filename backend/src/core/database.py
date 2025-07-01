from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import get_settings


def get_engine_and_sessionmaker():
    settings = get_settings()
    url_obj = make_url(settings.async_db_url)
    engine_kwargs: dict[str, object] = {
        "echo": settings.debug,
        "pool_pre_ping": True,
        "future": True,
    }
    # Only PostgreSQL supported
    engine_kwargs["pool_size"] = int(10 if settings.environment == "prod" else 5)
    engine_kwargs["max_overflow"] = int(20 if settings.environment == "prod" else 10)

    engine: AsyncEngine = create_async_engine(
        settings.async_db_url,
        **engine_kwargs,
    )
    AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return engine, AsyncSessionLocal


# Delay engine/session creation to runtime to avoid top-level config loading
engine = None
AsyncSessionLocal = None


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes/services."""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        _, AsyncSessionLocal = get_engine_and_sessionmaker()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as exc:
            logger.error(f"DB session error: {exc}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def db_healthcheck() -> bool:
    """Check if the database connection is healthy."""
    global engine
    if engine is None:
        engine, _ = get_engine_and_sessionmaker()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error(f"DB healthcheck failed: {exc}")
        return False


__all__ = [
    "AsyncSessionLocal",
    "db_healthcheck",
    "get_async_session",
]
