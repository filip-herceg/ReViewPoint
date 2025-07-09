from typing import cast

from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

# Delay config and engine import to runtime to avoid top-level config loading


async def validate_config() -> None:
    """
    Validate required environment variables and config logic.
    Raises:
        RuntimeError: If required environment variables are missing.
    """
    missing: list[str] = []
    from src.core.config import get_settings

    settings = get_settings()
    db_url: str | None = cast(str | None, getattr(settings, "db_url", None))
    environment: str | None = cast(str | None, getattr(settings, "environment", None))
    jwt_secret: str | None = (
        cast(str | None, getattr(settings, "jwt_secret", None))
        if hasattr(settings, "jwt_secret")
        else None
    )
    if not db_url:
        missing.append("REVIEWPOINT_DB_URL")
    if not environment:
        missing.append("REVIEWPOINT_ENVIRONMENT")
    if hasattr(settings, "jwt_secret") and not jwt_secret:
        missing.append("REVIEWPOINT_JWT_SECRET")
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )


async def db_healthcheck() -> None:
    """
    Run a simple DB health check query.
    Raises:
        RuntimeError: If the database is not healthy or connection fails.
        SQLAlchemyError: If SQLAlchemy encounters a DB error.
    """
    import src.core.database as db_module
    from src.core.database import ensure_engine_initialized

    try:
        # Ensure engine is initialized before attempting health check
        if db_module.engine is None:
            ensure_engine_initialized()

        engine: AsyncEngine | None = db_module.engine
        if engine is None:
            raise RuntimeError("Database engine is not initialized.")
        async with engine.connect() as conn:
            connection: AsyncConnection = conn
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        error_msg: str = str(e)
        logger.error(f"Database health check failed: {error_msg}")
        raise RuntimeError(f"Database health check failed: {error_msg}") from e
    except Exception as exc:
        logger.error(f"Unexpected error during DB health check: {exc}")
        raise


def log_startup_complete() -> None:
    """
    Log startup completion information.
    Raises:
        Exception: If engine or pool access fails.
    """
    import src.core.database as db_module
    from src.core.config import get_settings
    from src.core.database import ensure_engine_initialized

    settings = get_settings()
    environment: str | None = cast(str | None, getattr(settings, "environment", None))
    db_url: str | None = cast(str | None, getattr(settings, "db_url", None))
    db_type: str = db_url.split("://")[0] if db_url else "unknown"

    # Ensure engine is initialized for startup logging
    if db_module.engine is None:
        ensure_engine_initialized()

    try:
        # SQLAlchemy AsyncEngine does not always expose pool.size(), so we use a safe fallback
        pool_size: int | str
        pool = getattr(db_module.engine, "pool", None)
        if pool is not None and hasattr(pool, "size") and callable(pool.size):
            pool_size = str(pool.size())
        else:
            pool_size = "n/a"
    except Exception:
        pool_size = "n/a"

    logger.info(f"Startup complete. Environment: {environment}, DB: {db_type}")
    logger.info(f"DB pool size: {pool_size}")


async def on_startup() -> None:
    """
    FastAPI startup event handler.
    Raises:
        RuntimeError: If startup fails at any stage.
    """
    try:
        logger.info("Starting up application...")
        await validate_config()
        logger.info("Configuration validated.")
        await db_healthcheck()
        logger.info("Database connection pool initialized and healthy.")
        # Optional: Initialize cache
        # await cache.init()
        # logger.info("Cache initialized.")
        log_startup_complete()
    except Exception as e:
        error_msg: str = str(e)
        logger.error(f"Startup failed: {error_msg}")
        raise RuntimeError(f"Startup failed: {error_msg}") from e


async def on_shutdown() -> None:
    """
    FastAPI shutdown event handler.
    Raises:
        RuntimeError: If shutdown fails at any stage.
    """
    try:
        logger.info("Shutting down application...")
        # Complete pending tasks if any (custom logic here)
        # Optional: Close cache
        # await close_cache()
        # logger.info("Cache closed.")
        from src.core.database import engine

        if engine is not None:
            await engine.dispose()
            logger.info("Database connections closed.")
    except Exception as e:
        error_msg: str = str(e)
        logger.error(f"Shutdown error: {error_msg}")
        raise RuntimeError(f"Shutdown failed: {error_msg}") from e
    finally:
        logger.info("Shutdown complete.")
