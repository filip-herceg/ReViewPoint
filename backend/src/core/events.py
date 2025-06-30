from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.core.config import settings
from src.core.database import engine


async def validate_config() -> None:
    """Validate required environment variables and config logic."""
    missing = []
    if not getattr(settings, "db_url", None):
        missing.append("REVIEWPOINT_DB_URL")
    if not getattr(settings, "environment", None):
        missing.append("REVIEWPOINT_ENVIRONMENT")
    # Example: JWT secret check (add if present in config)
    if hasattr(settings, "jwt_secret") and not getattr(settings, "jwt_secret", None):
        missing.append("REVIEWPOINT_JWT_SECRET")
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )


async def db_healthcheck() -> None:
    """Run a simple DB health check query. Raises on DB error."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        error_msg = str(e)
        logger.error(f"Database health check failed: {error_msg}")
        raise RuntimeError(f"Database health check failed: {error_msg}") from e
    except Exception as exc:
        logger.error(f"Unexpected error during DB health check: {exc}")
        raise


def log_startup_complete() -> None:
    """Log startup completion information."""
    environment = settings.environment
    db_type = settings.db_url.split("://")[0] if settings.db_url else "unknown"
    pool_size = engine.pool.size() if hasattr(engine.pool, "size") else "n/a"

    logger.info(f"Startup complete. Environment: {environment}, DB: {db_type}")
    logger.info(f"DB pool size: {pool_size}")


async def on_startup() -> None:
    """FastAPI startup event handler."""
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
        error_msg = str(e)
        logger.error(f"Startup failed: {error_msg}")
        raise RuntimeError(f"Startup failed: {error_msg}") from e


async def on_shutdown() -> None:
    """FastAPI shutdown event handler."""
    try:
        logger.info("Shutting down application...")
        # Complete pending tasks if any (custom logic here)
        # Optional: Close cache
        # await close_cache()
        # logger.info("Cache closed.")
        await engine.dispose()
        logger.info("Database connections closed.")
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Shutdown error: {error_msg}")
        raise RuntimeError(f"Shutdown failed: {error_msg}") from e
    finally:
        logger.info("Shutdown complete.")
