from __future__ import annotations

import os
import threading
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Final, TypedDict

from loguru import logger
from sqlalchemy import text
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import get_settings

# Global state tracking for debugging
_engine_creation_count: int = 0
_session_creation_count: int = 0
_connection_failures: int = 0
_creation_lock: Final[threading.Lock] = threading.Lock()


def _log_worker_info() -> tuple[str, int, int]:
    """
    Log information about the current worker process for parallel test debugging.
    Returns:
        tuple[str, int, int]: (worker_id, process_id, thread_id)
    """
    worker_id: str = os.environ.get("PYTEST_XDIST_WORKER", "main")
    process_id: int = os.getpid()
    thread_id: int = threading.get_ident()
    logger.debug(
        f"[DB_DEBUG] Worker: {worker_id}, PID: {process_id}, Thread: {thread_id}"
    )
    return worker_id, process_id, thread_id


def _log_engine_pool_state(engine: AsyncEngine, context: str) -> None:
    """
    Log current connection pool state for debugging connection issues.
    Args:
        engine (AsyncEngine): The SQLAlchemy async engine.
        context (str): Contextual string for logging.
    Raises:
        Exception: If pool state cannot be retrieved.
    """
    try:
        pool = engine.pool
        worker_id, process_id, _ = _log_worker_info()
        logger.info(f"[DB_POOL_STATE] {context} - Worker: {worker_id}")
        logger.info(f"[DB_POOL_STATE] Pool size: {pool.size()}")
        logger.info(f"[DB_POOL_STATE] Checked out: {pool.checkedout()}")
        logger.info(f"[DB_POOL_STATE] Checked in: {pool.checkedin()}")
        logger.info(f"[DB_POOL_STATE] Overflow: {pool.overflow()}")
        logger.info(f"[DB_POOL_STATE] Invalid: {pool.invalidated()}")
        # Log connection URL (sanitized)
        db_url: str = str(engine.url)
        sanitized_url: str = db_url.split("@")[1] if "@" in db_url else db_url
        logger.info(f"[DB_POOL_STATE] DB URL: ...@{sanitized_url}")
    except Exception as exc:
        logger.warning(f"[DB_POOL_STATE] Failed to get pool state: {exc}")


def get_engine_and_sessionmaker() -> (
    tuple[AsyncEngine, async_sessionmaker[AsyncSession]]
):
    """
    Create and return a new AsyncEngine and async_sessionmaker.
    Returns:
        tuple[AsyncEngine, async_sessionmaker[AsyncSession]]: The engine and sessionmaker.
    Raises:
        Exception: If engine creation fails.
    """
    global _engine_creation_count
    with _creation_lock:
        _engine_creation_count += 1
        creation_count: int = _engine_creation_count
    worker_id, process_id, thread_id = _log_worker_info()
    logger.info(f"[DB_ENGINE_CREATE] Starting engine creation #{creation_count}")
    logger.info(
        f"[DB_ENGINE_CREATE] Worker: {worker_id}, PID: {process_id}, Thread: {thread_id}"
    )
    start_time: float = time.time()
    try:
        settings = get_settings()
        url_obj: URL = make_url(settings.async_db_url)
        logger.info(f"[DB_ENGINE_CREATE] Database: {url_obj.database}")
        logger.info(f"[DB_ENGINE_CREATE] Host: {url_obj.host}:{url_obj.port}")
        logger.info(f"[DB_ENGINE_CREATE] Driver: {url_obj.drivername}")
        engine_kwargs: dict[str, object] = {
            "pool_pre_ping": True,
            "future": True,
        }
        if url_obj.drivername.startswith("postgresql"):
            if os.environ.get("PYTEST_XDIST_WORKER"):
                engine_kwargs["pool_size"] = 1
                engine_kwargs["max_overflow"] = 1
                engine_kwargs["pool_reset_on_return"] = "commit"
                engine_kwargs["connect_args"] = {
                    "server_settings": {
                        "application_name": f"reviewpoint_test_{worker_id}_{process_id}",
                    }
                }
                logger.info(
                    "[DB_ENGINE_CREATE] Using parallel test pool settings: size=1, overflow=1, reset_on_return=commit"
                )
            else:
                engine_kwargs["pool_size"] = int(
                    10 if settings.environment == "prod" else 5
                )
                engine_kwargs["max_overflow"] = int(
                    20 if settings.environment == "prod" else 10
                )
                logger.info(
                    f"[DB_ENGINE_CREATE] Using standard pool settings: size={engine_kwargs['pool_size']}, overflow={engine_kwargs['max_overflow']}"
                )
        elif url_obj.drivername.startswith("sqlite"):
            connect_args: dict[str, object] = engine_kwargs.get("connect_args", {})
            if not isinstance(connect_args, dict):
                connect_args = {}
            connect_args["check_same_thread"] = False
            engine_kwargs["connect_args"] = connect_args
            logger.info(
                "[DB_ENGINE_CREATE] Using SQLite settings: check_same_thread=False"
            )
        else:
            logger.info(
                f"[DB_ENGINE_CREATE] Unknown database type: {url_obj.drivername}, using default settings"
            )
        logger.info(f"[DB_ENGINE_CREATE] Engine kwargs: {engine_kwargs}")
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
        creation_time: float = time.time() - start_time
        logger.info(
            f"[DB_ENGINE_CREATE] Engine #{creation_count} created successfully in {creation_time:.3f}s"
        )
        _log_engine_pool_state(engine, f"After creation #{creation_count}")
        return engine, AsyncSessionLocal
    except Exception as exc:
        creation_time: float = time.time() - start_time
        logger.error(
            f"[DB_ENGINE_CREATE] Failed to create engine #{creation_count} after {creation_time:.3f}s: {exc}"
        )
        logger.error(f"[DB_ENGINE_CREATE] Error type: {type(exc).__name__}")
        logger.error(f"[DB_ENGINE_CREATE] Worker: {worker_id}, PID: {process_id}")
        raise


# Delay engine/session creation to runtime to avoid top-level config loading
engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def ensure_engine_initialized() -> None:
    """
    Ensure the global engine and sessionmaker are initialized.
    """
    global engine, AsyncSessionLocal
    if engine is None or AsyncSessionLocal is None:
        logger.info("[DB_INIT] Initializing global engine and sessionmaker")
        engine, AsyncSessionLocal = get_engine_and_sessionmaker()


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes/services.
    Yields:
        AsyncSession: The SQLAlchemy async session.
    Raises:
        SQLAlchemyError: If a SQLAlchemy error occurs.
        Exception: For any other error.
    """
    global AsyncSessionLocal, _session_creation_count, _connection_failures
    with _creation_lock:
        _session_creation_count += 1
        session_count: int = _session_creation_count
    worker_id, process_id, thread_id = _log_worker_info()
    logger.debug(
        f"[DB_SESSION] Creating session #{session_count} - Worker: {worker_id}"
    )
    session_start_time: float = time.time()
    if AsyncSessionLocal is None:
        logger.info(
            "[DB_SESSION] SessionLocal not initialized, creating engine/sessionmaker"
        )
        try:
            ensure_engine_initialized()
        except Exception as exc:
            logger.error(f"[DB_SESSION] Failed to initialize SessionLocal: {exc}")
            raise
    session: AsyncSession | None = None
    try:
        # Log pre-session pool state
        if hasattr(AsyncSessionLocal, "bind") and getattr(
            AsyncSessionLocal, "bind", None
        ):
            _log_engine_pool_state(
                AsyncSessionLocal.bind, f"Before session #{session_count}"
            )
        session_creation_start: float = time.time()
        session = AsyncSessionLocal()  # type: ignore[call-arg]
        session_creation_time: float = time.time() - session_creation_start
        logger.debug(
            f"[DB_SESSION] Session #{session_count} created in {session_creation_time:.3f}s"
        )
        # Test the connection immediately
        connection_test_start: float = time.time()
        try:
            await session.execute(text("SELECT 1"))
            connection_test_time: float = time.time() - connection_test_start
            logger.debug(
                f"[DB_SESSION] Session #{session_count} connection test passed in {connection_test_time:.3f}s"
            )
        except Exception as exc:
            connection_test_time: float = time.time() - connection_test_start
            logger.error(
                f"[DB_SESSION] Session #{session_count} connection test failed in {connection_test_time:.3f}s: {exc}"
            )
            raise
        yield session
        # Log successful session completion
        total_session_time: float = time.time() - session_start_time
        logger.debug(
            f"[DB_SESSION] Session #{session_count} completed successfully in {total_session_time:.3f}s"
        )
    except SQLAlchemyError as exc:
        with _creation_lock:
            _connection_failures += 1
            failure_count: int = _connection_failures
        total_session_time: float = time.time() - session_start_time
        logger.error(
            f"[DB_SESSION] Session #{session_count} SQLAlchemy error #{failure_count} after {total_session_time:.3f}s: {exc}"
        )
        logger.error(f"[DB_SESSION] Error type: {type(exc).__name__}")
        logger.error(f"[DB_SESSION] Worker: {worker_id}, PID: {process_id}")
        if session:
            try:
                await session.rollback()
                logger.debug(
                    f"[DB_SESSION] Session #{session_count} rollback completed"
                )
            except Exception as rollback_error:
                logger.error(
                    f"[DB_SESSION] Session #{session_count} rollback failed: {rollback_error}"
                )
        raise
    except Exception as exc:
        with _creation_lock:
            _connection_failures += 1
            failure_count: int = _connection_failures
        total_session_time: float = time.time() - session_start_time
        logger.error(
            f"[DB_SESSION] Session #{session_count} unexpected error #{failure_count} after {total_session_time:.3f}s: {exc}"
        )
        logger.error(f"[DB_SESSION] Error type: {type(exc).__name__}")
        logger.error(f"[DB_SESSION] Worker: {worker_id}, PID: {process_id}")
        raise
    finally:
        if session:
            try:
                close_start_time: float = time.time()
                await session.close()
                close_time: float = time.time() - close_start_time
                logger.debug(
                    f"[DB_SESSION] Session #{session_count} closed in {close_time:.3f}s"
                )
            except Exception as close_error:
                logger.error(
                    f"[DB_SESSION] Session #{session_count} close failed: {close_error}"
                )
        # Log post-session pool state
        if (
            AsyncSessionLocal
            and hasattr(AsyncSessionLocal, "bind")
            and getattr(AsyncSessionLocal, "bind", None)
        ):
            _log_engine_pool_state(
                AsyncSessionLocal.bind, f"After session #{session_count}"
            )


async def db_healthcheck() -> bool:
    """
    Check if the database connection is healthy.
    Returns:
        bool: True if healthy, False otherwise.
    Raises:
        Exception: If connection or query fails.
    """
    global engine
    worker_id, process_id, thread_id = _log_worker_info()
    logger.info(f"[DB_HEALTHCHECK] Starting healthcheck - Worker: {worker_id}")
    healthcheck_start_time: float = time.time()
    if engine is None:
        logger.info("[DB_HEALTHCHECK] Engine not initialized, creating new engine")
        try:
            engine, _ = get_engine_and_sessionmaker()
        except Exception as exc:
            healthcheck_time: float = time.time() - healthcheck_start_time
            logger.error(
                f"[DB_HEALTHCHECK] Failed to create engine in {healthcheck_time:.3f}s: {exc}"
            )
            return False
    try:
        connection_start_time: float = time.time()
        async with engine.connect() as conn:
            connection_time: float = time.time() - connection_start_time
            logger.debug(
                f"[DB_HEALTHCHECK] Connection established in {connection_time:.3f}s"
            )
            query_start_time: float = time.time()
            await conn.execute(text("SELECT 1"))
            query_time: float = time.time() - query_start_time
            total_healthcheck_time: float = time.time() - healthcheck_start_time
            logger.info(
                f"[DB_HEALTHCHECK] SUCCESS - Total: {total_healthcheck_time:.3f}s, Query: {query_time:.3f}s"
            )
        _log_engine_pool_state(engine, "After successful healthcheck")
        return True
    except Exception as exc:
        total_healthcheck_time: float = time.time() - healthcheck_start_time
        logger.error(
            f"[DB_HEALTHCHECK] FAILED after {total_healthcheck_time:.3f}s: {exc}"
        )
        logger.error(f"[DB_HEALTHCHECK] Error type: {type(exc).__name__}")
        logger.error(f"[DB_HEALTHCHECK] Worker: {worker_id}, PID: {process_id}")
        if engine:
            _log_engine_pool_state(engine, "After failed healthcheck")
        return False


class ConnectionDebugInfo(TypedDict, total=False):
    worker_id: str
    process_id: int
    thread_id: int
    engine_creation_count: int
    session_creation_count: int
    connection_failures: int
    engine_initialized: bool
    sessionmaker_initialized: bool
    pool_size: int
    pool_checked_out: int
    pool_checked_in: int
    pool_overflow: int
    pool_invalidated: int
    pool_error: str


def get_connection_debug_info() -> ConnectionDebugInfo:
    """
    Get current connection state for debugging.
    Returns:
        ConnectionDebugInfo: Dictionary of connection debug info.
    """
    global engine, AsyncSessionLocal, _engine_creation_count, _session_creation_count, _connection_failures
    worker_id, process_id, thread_id = _log_worker_info()
    info: ConnectionDebugInfo = ConnectionDebugInfo(
        worker_id=worker_id,
        process_id=process_id,
        thread_id=thread_id,
        engine_creation_count=_engine_creation_count,
        session_creation_count=_session_creation_count,
        connection_failures=_connection_failures,
        engine_initialized=engine is not None,
        sessionmaker_initialized=AsyncSessionLocal is not None,
    )
    if engine:
        try:
            pool = engine.pool
            info.update(
                {
                    "pool_size": pool.size(),
                    "pool_checked_out": pool.checkedout(),
                    "pool_checked_in": pool.checkedin(),
                    "pool_overflow": pool.overflow(),
                    "pool_invalidated": pool.invalidated(),
                }
            )
        except Exception as exc:
            info["pool_error"] = str(exc)
    return info


__all__: tuple[str, ...] = (
    "AsyncSessionLocal",
    "db_healthcheck",
    "get_async_session",
    "get_connection_debug_info",
)
