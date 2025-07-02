from __future__ import annotations

import os
import threading
import time
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

# Global state tracking for debugging
_engine_creation_count = 0
_session_creation_count = 0
_connection_failures = 0
_creation_lock = threading.Lock()


def _log_worker_info():
    """Log information about the current worker process for parallel test debugging."""
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    process_id = os.getpid()
    thread_id = threading.get_ident()
    logger.debug(f"[DB_DEBUG] Worker: {worker_id}, PID: {process_id}, Thread: {thread_id}")
    return worker_id, process_id, thread_id


def _log_engine_pool_state(engine: AsyncEngine, context: str):
    """Log current connection pool state for debugging connection issues."""
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
        db_url = str(engine.url)
        sanitized_url = db_url.split('@')[1] if '@' in db_url else db_url
        logger.info(f"[DB_POOL_STATE] DB URL: ...@{sanitized_url}")
        
    except Exception as e:
        logger.warning(f"[DB_POOL_STATE] Failed to get pool state: {e}")


def get_engine_and_sessionmaker():
    global _engine_creation_count
    
    with _creation_lock:
        _engine_creation_count += 1
        creation_count = _engine_creation_count
    
    worker_id, process_id, thread_id = _log_worker_info()
    logger.info(f"[DB_ENGINE_CREATE] Starting engine creation #{creation_count}")
    logger.info(f"[DB_ENGINE_CREATE] Worker: {worker_id}, PID: {process_id}, Thread: {thread_id}")
    
    start_time = time.time()
    
    try:
        settings = get_settings()
        url_obj = make_url(settings.async_db_url)
        
        # Log database connection details
        logger.info(f"[DB_ENGINE_CREATE] Database: {url_obj.database}")
        logger.info(f"[DB_ENGINE_CREATE] Host: {url_obj.host}:{url_obj.port}")
        logger.info(f"[DB_ENGINE_CREATE] Driver: {url_obj.drivername}")
        
        engine_kwargs: dict[str, object] = {
            "pool_pre_ping": True,
            "future": True,
        }
        
        # Only apply pool settings for PostgreSQL databases (SQLite doesn't support them)
        if url_obj.drivername.startswith('postgresql'):
            # Adjust pool settings for parallel testing
            if os.environ.get('PYTEST_XDIST_WORKER'):
                # Smaller pools for parallel workers to avoid connection exhaustion
                # Use very minimal settings to avoid asyncpg event loop conflicts
                engine_kwargs["pool_size"] = 1
                engine_kwargs["max_overflow"] = 1
                engine_kwargs["pool_reset_on_return"] = "commit"
                # Additional asyncpg-specific settings for parallel testing
                engine_kwargs["connect_args"] = {
                    "server_settings": {
                        "application_name": f"reviewpoint_test_{worker_id}_{process_id}",
                    }
                }
                logger.info(f"[DB_ENGINE_CREATE] Using parallel test pool settings: size=1, overflow=1, reset_on_return=commit")
            else:
                # Standard pool settings
                engine_kwargs["pool_size"] = int(10 if settings.environment == "prod" else 5)
                engine_kwargs["max_overflow"] = int(20 if settings.environment == "prod" else 10)
                logger.info(f"[DB_ENGINE_CREATE] Using standard pool settings: size={engine_kwargs['pool_size']}, overflow={engine_kwargs['max_overflow']}")
        elif url_obj.drivername.startswith('sqlite'):
            # SQLite-specific settings
            connect_args = engine_kwargs.get("connect_args", {})
            if not isinstance(connect_args, dict):
                connect_args = {}
            connect_args["check_same_thread"] = False
            engine_kwargs["connect_args"] = connect_args
            logger.info(f"[DB_ENGINE_CREATE] Using SQLite settings: check_same_thread=False")
        else:
            logger.info(f"[DB_ENGINE_CREATE] Unknown database type: {url_obj.drivername}, using default settings")

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
        
        creation_time = time.time() - start_time
        logger.info(f"[DB_ENGINE_CREATE] Engine #{creation_count} created successfully in {creation_time:.3f}s")
        
        # Log initial pool state
        _log_engine_pool_state(engine, f"After creation #{creation_count}")
        
        return engine, AsyncSessionLocal
        
    except Exception as e:
        creation_time = time.time() - start_time
        logger.error(f"[DB_ENGINE_CREATE] Failed to create engine #{creation_count} after {creation_time:.3f}s: {e}")
        logger.error(f"[DB_ENGINE_CREATE] Error type: {type(e).__name__}")
        logger.error(f"[DB_ENGINE_CREATE] Worker: {worker_id}, PID: {process_id}")
        raise


# Delay engine/session creation to runtime to avoid top-level config loading
engine = None
AsyncSessionLocal = None


def ensure_engine_initialized():
    """Ensure the global engine and sessionmaker are initialized."""
    global engine, AsyncSessionLocal
    if engine is None or AsyncSessionLocal is None:
        logger.info("[DB_INIT] Initializing global engine and sessionmaker")
        engine, AsyncSessionLocal = get_engine_and_sessionmaker()


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes/services."""
    global AsyncSessionLocal, _session_creation_count, _connection_failures
    
    with _creation_lock:
        _session_creation_count += 1
        session_count = _session_creation_count
    
    worker_id, process_id, thread_id = _log_worker_info()
    logger.debug(f"[DB_SESSION] Creating session #{session_count} - Worker: {worker_id}")
    
    session_start_time = time.time()
    
    if AsyncSessionLocal is None:
        logger.info(f"[DB_SESSION] SessionLocal not initialized, creating engine/sessionmaker")
        try:
            ensure_engine_initialized()
        except Exception as e:
            logger.error(f"[DB_SESSION] Failed to initialize SessionLocal: {e}")
            raise
    
    session = None
    try:
        # Log pre-session pool state
        if hasattr(AsyncSessionLocal, 'bind') and AsyncSessionLocal.bind:
            _log_engine_pool_state(AsyncSessionLocal.bind, f"Before session #{session_count}")
        
        session_creation_start = time.time()
        session = AsyncSessionLocal()
        session_creation_time = time.time() - session_creation_start
        
        logger.debug(f"[DB_SESSION] Session #{session_count} created in {session_creation_time:.3f}s")
        
        # Test the connection immediately
        connection_test_start = time.time()
        try:
            await session.execute(text("SELECT 1"))
            connection_test_time = time.time() - connection_test_start
            logger.debug(f"[DB_SESSION] Session #{session_count} connection test passed in {connection_test_time:.3f}s")
        except Exception as e:
            connection_test_time = time.time() - connection_test_start
            logger.error(f"[DB_SESSION] Session #{session_count} connection test failed in {connection_test_time:.3f}s: {e}")
            raise
        
        yield session
        
        # Log successful session completion
        total_session_time = time.time() - session_start_time
        logger.debug(f"[DB_SESSION] Session #{session_count} completed successfully in {total_session_time:.3f}s")
        
    except SQLAlchemyError as exc:
        with _creation_lock:
            _connection_failures += 1
            failure_count = _connection_failures
        
        total_session_time = time.time() - session_start_time
        logger.error(f"[DB_SESSION] Session #{session_count} SQLAlchemy error #{failure_count} after {total_session_time:.3f}s: {exc}")
        logger.error(f"[DB_SESSION] Error type: {type(exc).__name__}")
        logger.error(f"[DB_SESSION] Worker: {worker_id}, PID: {process_id}")
        
        if session:
            try:
                await session.rollback()
                logger.debug(f"[DB_SESSION] Session #{session_count} rollback completed")
            except Exception as rollback_error:
                logger.error(f"[DB_SESSION] Session #{session_count} rollback failed: {rollback_error}")
        raise
    except Exception as exc:
        with _creation_lock:
            _connection_failures += 1
            failure_count = _connection_failures
        
        total_session_time = time.time() - session_start_time
        logger.error(f"[DB_SESSION] Session #{session_count} unexpected error #{failure_count} after {total_session_time:.3f}s: {exc}")
        logger.error(f"[DB_SESSION] Error type: {type(exc).__name__}")
        logger.error(f"[DB_SESSION] Worker: {worker_id}, PID: {process_id}")
        raise
    finally:
        if session:
            try:
                close_start_time = time.time()
                await session.close()
                close_time = time.time() - close_start_time
                logger.debug(f"[DB_SESSION] Session #{session_count} closed in {close_time:.3f}s")
            except Exception as close_error:
                logger.error(f"[DB_SESSION] Session #{session_count} close failed: {close_error}")
        
        # Log post-session pool state
        if AsyncSessionLocal and hasattr(AsyncSessionLocal, 'bind') and AsyncSessionLocal.bind:
            _log_engine_pool_state(AsyncSessionLocal.bind, f"After session #{session_count}")


async def db_healthcheck() -> bool:
    """Check if the database connection is healthy."""
    global engine
    
    worker_id, process_id, thread_id = _log_worker_info()
    logger.info(f"[DB_HEALTHCHECK] Starting healthcheck - Worker: {worker_id}")
    
    healthcheck_start_time = time.time()
    
    if engine is None:
        logger.info(f"[DB_HEALTHCHECK] Engine not initialized, creating new engine")
        try:
            engine, _ = get_engine_and_sessionmaker()
        except Exception as e:
            healthcheck_time = time.time() - healthcheck_start_time
            logger.error(f"[DB_HEALTHCHECK] Failed to create engine in {healthcheck_time:.3f}s: {e}")
            return False
    
    try:
        connection_start_time = time.time()
        async with engine.connect() as conn:
            connection_time = time.time() - connection_start_time
            logger.debug(f"[DB_HEALTHCHECK] Connection established in {connection_time:.3f}s")
            
            query_start_time = time.time()
            await conn.execute(text("SELECT 1"))
            query_time = time.time() - query_start_time
            
            total_healthcheck_time = time.time() - healthcheck_start_time
            logger.info(f"[DB_HEALTHCHECK] SUCCESS - Total: {total_healthcheck_time:.3f}s, Query: {query_time:.3f}s")
            
        # Log pool state after successful healthcheck
        _log_engine_pool_state(engine, "After successful healthcheck")
        return True
        
    except Exception as exc:
        total_healthcheck_time = time.time() - healthcheck_start_time
        logger.error(f"[DB_HEALTHCHECK] FAILED after {total_healthcheck_time:.3f}s: {exc}")
        logger.error(f"[DB_HEALTHCHECK] Error type: {type(exc).__name__}")
        logger.error(f"[DB_HEALTHCHECK] Worker: {worker_id}, PID: {process_id}")
        
        # Log pool state after failed healthcheck
        if engine:
            _log_engine_pool_state(engine, "After failed healthcheck")
        
        return False


def get_connection_debug_info() -> dict:
    """Get current connection state for debugging."""
    global engine, AsyncSessionLocal, _engine_creation_count, _session_creation_count, _connection_failures
    
    worker_id, process_id, thread_id = _log_worker_info()
    
    info = {
        "worker_id": worker_id,
        "process_id": process_id,
        "thread_id": thread_id,
        "engine_creation_count": _engine_creation_count,
        "session_creation_count": _session_creation_count,
        "connection_failures": _connection_failures,
        "engine_initialized": engine is not None,
        "sessionmaker_initialized": AsyncSessionLocal is not None,
    }
    
    if engine:
        try:
            pool = engine.pool
            info.update({
                "pool_size": pool.size(),
                "pool_checked_out": pool.checkedout(),
                "pool_checked_in": pool.checkedin(),
                "pool_overflow": pool.overflow(),
                "pool_invalidated": pool.invalidated(),
            })
        except Exception as e:
            info["pool_error"] = str(e)
    
    return info


__all__ = [
    "AsyncSessionLocal",
    "db_healthcheck",
    "get_async_session",
    "get_connection_debug_info",
]
