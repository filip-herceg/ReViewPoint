# type: ignore
from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,  # type: ignore[attr-defined]
    create_async_engine,
)

from backend.core.config import settings

logger = logging.getLogger(__name__)

# Create the async engine
url_obj = make_url(settings.async_db_url)
engine_kwargs: dict[str, object] = {
    "echo": settings.debug,
    "pool_pre_ping": True,
    "future": True,
}
if url_obj.drivername.startswith("sqlite"):
    # SQLite does not support pool_size/max_overflow
    pass
else:
    # Convert to int for type safety
    engine_kwargs["pool_size"] = int(10 if settings.environment == "prod" else 5)
    engine_kwargs["max_overflow"] = int(20 if settings.environment == "prod" else 10)

engine: AsyncEngine = create_async_engine(
    settings.async_db_url,
    **engine_kwargs,
)

# Session factory for dependency injection
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes/services."""
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
    """Check DB connectivity (for /health endpoint or startup)."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error(f"Database healthcheck failed: {exc}")
        return False


# Removed the reassignment of async_sessionmaker to None to avoid conflicts.
