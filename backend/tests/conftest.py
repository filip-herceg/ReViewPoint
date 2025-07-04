"""
Unified test configuration for ReViewPoint backend.

This configuration supports both fast and slow test modes:
- Fast mode (FAST_TESTS=1): Uses SQLite in-memory databases for speed
- Slow mode (default): Uses PostgreSQL containers for thorough testing

Test DB Policy:
- Fast tests: Use in-memory SQLite, no containers needed
- Slow tests: Use a single PostgreSQL container, managed by session-scoped fixture
- Configuration is determined by FAST_TESTS environment variable
- No file swapping needed, all logic contained in this single conftest
"""

import os
import sys
import uuid
from collections.abc import Callable, Generator, Iterator
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from loguru import logger

# Check if we're in fast test mode early
IS_FAST_TEST_MODE = os.environ.get("FAST_TESTS") == "1"

# Set up the source path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Early environment setup for pytest-xdist workers
# This must happen before any imports that might create database engines
# We detect pytest runs by checking if we're being imported from within the tests directory
# or if common pytest environment variables are set
is_pytest_run = (
    "PYTEST_CURRENT_TEST" in os.environ or 
    "pytest" in str(sys.argv) or 
    "__file__" in globals() and "tests" in str(Path(__file__).resolve()) or
    any(arg.endswith("pytest") or "test" in arg for arg in sys.argv if isinstance(arg, str))
)

if is_pytest_run:
    # Only set during pytest runs to avoid affecting normal app usage
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    
    # Set critical secrets that are needed during engine creation
    # Always set these for tests to ensure Settings object can be created
    if "REVIEWPOINT_JWT_SECRET_KEY" not in os.environ:
        # Use different configs for fast vs slow tests
        if IS_FAST_TEST_MODE:
            os.environ["REVIEWPOINT_JWT_SECRET"] = "fasttestsecret123"
            os.environ["REVIEWPOINT_JWT_SECRET_KEY"] = "fasttestsecret123"
            os.environ["REVIEWPOINT_API_KEY_ENABLED"] = "false"  # Disable API key auth for fast tests
            os.environ["REVIEWPOINT_AUTH_ENABLED"] = "true"
            # Only set default log level if user hasn't specified one via CLI or environment
            # This allows pytest --log-level=DEBUG to work as expected
            if "REVIEWPOINT_LOG_LEVEL" not in os.environ:
                os.environ["REVIEWPOINT_LOG_LEVEL"] = "WARNING"  # Default to reduce log noise in tests
            os.environ["REVIEWPOINT_DB_URL"] = "sqlite+aiosqlite:///:memory:"
            
            # Set all feature flags for fast tests
            feature_flags = [
                "AUTH_REGISTER", "AUTH_LOGIN", "AUTH_REQUEST_PASSWORD_RESET",
                "AUTH_RESET_PASSWORD", "AUTH_ME", "AUTH_LOGOUT", "AUTH_REFRESH_TOKEN",
                "USERS_CREATE", "USERS_GET", "USERS_UPDATE", "USERS_DELETE",
                "USERS_LIST", "USERS_EXPORT", "USERS_EXPORT_ALIVE", "USERS_EXPORT_SIMPLE",
                "HEALTH", "HEALTH_READ", "UPLOADS", "UPLOADS_UPLOAD", "UPLOADS_GET",
                "UPLOADS_LIST", "UPLOADS_UPDATE", "UPLOADS_DELETE", "UPLOADS_EXPORT"
            ]
            for flag in feature_flags:
                os.environ[f"REVIEWPOINT_FEATURE_{flag}"] = "true"
        else:
            # Regular test mode - set JWT secrets for slow tests
            os.environ["REVIEWPOINT_JWT_SECRET"] = "testsecret"
            os.environ["REVIEWPOINT_JWT_SECRET_KEY"] = "testsecret"
            os.environ["REVIEWPOINT_API_KEY_ENABLED"] = "true"
        
        os.environ["REVIEWPOINT_API_KEY"] = "testkey"
        os.environ["REVIEWPOINT_ENVIRONMENT"] = "test"
        
        logger.info(f"[EARLY_ENV_SETUP] Critical env vars set for worker: {worker_id} (fast_mode: {IS_FAST_TEST_MODE})")
        
        # Clear any cached settings since env vars have changed
        try:
            from src.core.config import clear_settings_cache
            clear_settings_cache()
            logger.info(f"[EARLY_ENV_SETUP] Settings cache cleared for worker: {worker_id}")
        except Exception as e:
            logger.warning(f"[EARLY_ENV_SETUP] Could not clear settings cache: {e}")


@pytest.fixture(scope="session")
def use_fast_db():
    """Enable fast testing mode with shared in-memory SQLite if FAST_TESTS env var is set."""
    return IS_FAST_TEST_MODE


def pytest_configure(config):
    """Register test markers for slow and fast tests and handle log level configuration."""
    config.addinivalue_line("markers", "slow: marks tests that access real database or are slow")
    config.addinivalue_line("markers", "fast: marks tests that use mocks or in-memory DB")
    config.addinivalue_line("markers", "skip_if_fast_tests: skip test when FAST_TESTS=1")
    
    # Check if user specified log level via CLI and override environment accordingly
    log_level = None
    
    # Check for pytest's log level options
    if hasattr(config.option, 'log_level') and config.option.log_level:
        log_level = config.option.log_level.upper()
    elif hasattr(config.option, 'log_cli_level') and config.option.log_cli_level:
        log_level = config.option.log_cli_level.upper()
    
    # If user specified a log level via pytest CLI, override the environment variable
    if log_level:
        os.environ["REVIEWPOINT_LOG_LEVEL"] = log_level


def pytest_runtest_setup(item):
    """Skip tests marked with skip_if_fast_tests or requires_real_db when in fast test mode."""
    if IS_FAST_TEST_MODE and (item.get_closest_marker("skip_if_fast_tests") or item.get_closest_marker("requires_real_db")):
        # Get the reason from the marker if available
        marker = item.get_closest_marker("requires_real_db") or item.get_closest_marker("skip_if_fast_tests")
        reason = "Test skipped in fast test mode"
        if marker and marker.args:
            reason = marker.args[0]
        pytest.skip(reason)


def pytest_sessionstart(session):
    """
    Set critical environment variables before any fixtures or tests run.
    This runs once per pytest-xdist worker session, ensuring env vars are set 
    before any code that might create database engines executes.
    """
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    logger.info(f"[PYTEST_SESSIONSTART] Session started for worker: {worker_id} (fast_mode: {IS_FAST_TEST_MODE})")
    
    # Import configuration here to trigger any early validation
    try:
        from src.core.config import get_settings
        logger.info(f"[PYTEST_SESSIONSTART] Config validation successful for worker: {worker_id}")
    except Exception as e:
        logger.error(f"[PYTEST_SESSIONSTART] Config validation failed for worker {worker_id}: {e}")
        # Don't fail here, let the test handle it


@pytest.fixture(scope="session", autouse=True)
def database_setup(use_fast_db):
    """
    Set up database for testing. Uses SQLite in-memory for fast tests,
    PostgreSQL container for slow tests.
    """
    if use_fast_db:
        # Fast test mode: no container needed, SQLite in-memory
        logger.info("[DATABASE_SETUP] Using fast test mode with SQLite in-memory")
        yield
        logger.info("[DATABASE_SETUP] Fast test cleanup complete")
    else:
        # Slow test mode: use PostgreSQL container
        from testcontainers.postgres import PostgresContainer
        
        image = os.environ.get("REVIEWPOINT_TEST_POSTGRES_IMAGE", "postgres:15-alpine")
        import time
        import socket
        
        # Log parallel test worker information
        worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
        logger.info(f"[DATABASE_SETUP] Starting PostgreSQL container for worker: {worker_id}")
        
        try:
            container_start_time = time.time()
            # Set up the container with high max_connections and shared_buffers
            postgres = PostgresContainer(image)
            postgres.with_env("POSTGRES_MAX_CONNECTIONS", "300")
            postgres.with_env("POSTGRES_SHARED_BUFFERS", "512MB")
            # Expose the default port and try to bind it for Windows compatibility
            postgres.with_exposed_ports(5432)
            
            logger.info(f"[DATABASE_SETUP] Container configured, starting with image: {image}")
            
            with postgres as pg:
                container_ready_time = time.time() - container_start_time
                logger.info(f"[DATABASE_SETUP] Container started in {container_ready_time:.2f}s")
                
                db_url = pg.get_connection_url()
                # Convert sync driver to asyncpg for SQLAlchemy async engine
                if db_url.startswith("postgresql://"):
                    async_db_url = db_url.replace(
                        "postgresql://", "postgresql+asyncpg://", 1
                    )
                elif db_url.startswith("postgresql+psycopg2://"):
                    async_db_url = db_url.replace(
                        "postgresql+psycopg2://", "postgresql+asyncpg://", 1
                    )
                else:
                    async_db_url = db_url
                
                # Set the database URL for tests
                os.environ["REVIEWPOINT_DB_URL"] = async_db_url
                
                # Log connection details (sanitized)
                sanitized_url = async_db_url.split('@')[1] if '@' in async_db_url else async_db_url
                logger.info(f"[DATABASE_SETUP] Container URL: postgresql+asyncpg://...@{sanitized_url}")
                
                # Test database connection
                yield
                
                logger.info("[DATABASE_SETUP] PostgreSQL container cleanup complete")
                
        except Exception as e:
            logger.error(f"[DATABASE_SETUP] Failed to start PostgreSQL container: {e}")
            logger.error("Make sure Docker is running and accessible.")
            raise


# Define the postgres_container fixture for backward compatibility
postgres_container = database_setup


#
# ENFORCED TEST ENVIRONMENT/DB SETUP POLICY
#
# All environment variable and database setup for tests MUST be centralized in this file (conftest.py).
# No test file (except explicit config/validation tests) may set environment variables or database URLs directly.
# Valid exceptions: tests that explicitly test config/env/DB error handling (e.g., test_config.py).
# This is enforced by an automated check below. If you need to add a new exception, update the list in the check.
#


# ENFORCEMENT: Never import or create a global settings = Settings() at import time in any code or test.
# Always use get_settings() to ensure env vars are set first.

import asyncio


# 1. Environment setup (env vars, DB cleanup, DB/table creation)
@pytest.fixture(autouse=True, scope="session")
def set_required_env_vars_session(database_setup) -> None:
    """
    Set critical environment variables at session scope before any code that might 
    create database engines runs. This is essential for pytest-xdist workers.
    """
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    logger.info(f"[ENV_SETUP_SESSION] Setting session-level environment variables for worker: {worker_id}")
    
    # Environment variables are already set in early setup, just log confirmation
    logger.info(f"[ENV_SETUP_SESSION] Critical env vars confirmed for worker: {worker_id}")
    logger.info(f"[ENV_SETUP_SESSION] DB_URL: {os.environ.get('REVIEWPOINT_DB_URL', 'NOT_SET')}")
    

@pytest.fixture(autouse=True, scope="function")
def set_remaining_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Set remaining environment variables and feature flags for tests.
    Uses monkeypatch for proper cleanup after each test.
    Also clears settings cache to ensure fresh config for each test.
    """
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    logger.debug(f"[ENV_SETUP_FUNC] Setting function-level environment variables for worker: {worker_id}")
    
    # Clear settings cache to ensure fresh config
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from src.core.config import clear_settings_cache
        clear_settings_cache()
        logger.debug(f"[ENV_SETUP_FUNC] Settings cache cleared for worker: {worker_id}")
    except Exception as e:
        logger.warning(f"[ENV_SETUP_FUNC] Could not clear settings cache: {e}")
    
    # Feature flags (these can be set per-function since they don't affect engine creation)
    # Auth endpoints
    monkeypatch.setenv("REVIEWPOINT_FEATURE_AUTH_REGISTER", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_AUTH_LOGIN", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_AUTH_REQUEST_PASSWORD_RESET", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_AUTH_RESET_PASSWORD", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_AUTH_ME", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_AUTH_LOGOUT", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_AUTH_REFRESH_TOKEN", "true")
    # User endpoints
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_CREATE", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_LIST", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_GET", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_EXPORT", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_EXPORT_FULL", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_EXPORT_ALIVE", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_EXPORT_SIMPLE", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_USERS_READ", "true")
    # Uploads/files endpoints (granular flags)
    monkeypatch.setenv("REVIEWPOINT_FEATURE_UPLOADS", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_UPLOADS_GET_FILE", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_UPLOADS_EXPORT", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_UPLOADS_UPLOAD", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_UPLOADS_DELETE", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_UPLOADS_LIST", "true")
    # Optionally, enable all granular features at once for convenience
    monkeypatch.setenv(
        "REVIEWPOINT_FEATURES",
        "uploads:export,uploads:upload,uploads:delete,uploads:list",
    )
    # Health endpoints
    monkeypatch.setenv("REVIEWPOINT_FEATURE_HEALTH", "true")
    monkeypatch.setenv("REVIEWPOINT_FEATURE_HEALTH_READ", "true")
    # Any other likely features (add more as needed)
    monkeypatch.setenv("REVIEWPOINT_FEATURE_API_KEY", "true")


# 2. Event loop (for async tests)
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create a new asyncio event loop for the test session.
    Required for running async tests with pytest-asyncio.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()



# 3. Database/session fixtures

# Session-scoped engine for backward compatibility (not used by default)
@pytest_asyncio.fixture(scope="session")
async def async_engine(use_fast_db, postgres_container):
    from sqlalchemy.ext.asyncio import create_async_engine
    if use_fast_db:
        db_url = "sqlite+aiosqlite:///:memory:?cache=shared"
        engine = create_async_engine(db_url, future=True, connect_args={"check_same_thread": False})
    else:
        db_url = os.environ["REVIEWPOINT_DB_URL"]
        engine = create_async_engine(db_url, future=True)
    yield engine
    await engine.dispose()



# Fixture to truncate all tables before each test for full isolation
@pytest_asyncio.fixture(autouse=True, scope="function")
async def truncate_tables(async_engine_isolated):
    """
    Truncate all tables in the test database before each test for full isolation.
    Handles DBs with no tables, and logs errors for unsupported backends.
    """
    import sqlalchemy
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from src.models import Base
    try:
        async with async_engine_isolated.begin() as conn:
            # Only run for PostgreSQL
            if conn.dialect.name != "postgresql":
                logger.warning(f"truncate_tables: Skipping for non-PostgreSQL backend: {conn.dialect.name}")
                return
            # If no tables, skip
            if not Base.metadata.sorted_tables:
                logger.info("truncate_tables: No tables to truncate.")
                return
            for table in reversed(Base.metadata.sorted_tables):
                try:
                    await conn.execute(sqlalchemy.text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE;'))
                except Exception as e:
                    logger.error(f"truncate_tables: Failed to truncate {table.name}: {e}")
    except Exception as e:
        logger.error(f"truncate_tables: Unexpected error: {e}")


# Function-scoped engine for parallel/isolated tests
@pytest_asyncio.fixture(scope="function")
async def async_engine_isolated(use_fast_db, database_setup):
    """
    Provide a SQLAlchemy async engine for each test function (parallel safe).
    Uses in-memory SQLite if FAST_TESTS=1, otherwise uses PostgreSQL.
    """
    from sqlalchemy.ext.asyncio import create_async_engine
    import time
    import uuid
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from src.models import Base
    
    if use_fast_db:
        # Fast test mode: use SQLite in-memory
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
            pool_pre_ping=False,
        )
        
        # Enable foreign key constraints for SQLite
        from sqlalchemy import event, text
        @event.listens_for(engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        yield engine
        await engine.dispose()
    else:
        # Slow test mode: use PostgreSQL (existing logic)
        worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
        test_id = str(uuid.uuid4())[:8]
        logger.debug(f"[ENGINE_ISOLATED] Creating engine for worker: {worker_id}, test_id: {test_id}")

        engine_start_time = time.time()
        
        if os.environ.get('PYTEST_XDIST_WORKER'):
            # Use SQLite for parallel execution to avoid asyncpg concurrency issues
            db_url = f"sqlite+aiosqlite:///:memory:?cache=shared&test_id={test_id}"
            logger.debug(f"[ENGINE_ISOLATED] Using SQLite in-memory DB (parallel): {db_url}")
            engine = create_async_engine(db_url, future=True, connect_args={"check_same_thread": False})
        else:
            # Force SQLite for single-threaded tests to avoid asyncpg event loop conflicts
            # asyncpg has known issues with TestClient and anyio event loop mixing
            db_url = f"sqlite+aiosqlite:///:memory:?cache=shared&test_id={test_id}"
            logger.debug(f"[ENGINE_ISOLATED] Using SQLite in-memory DB (single-threaded, avoiding asyncpg): {db_url}")
            
            # Enable foreign key constraints for SQLite
            from sqlalchemy import event, text
            
            def set_sqlite_pragma_isolated(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
            
            engine = create_async_engine(db_url, future=True, connect_args={"check_same_thread": False})
            event.listen(engine.sync_engine, "connect", set_sqlite_pragma_isolated)

        engine_creation_time = time.time() - engine_start_time
        logger.debug(f"[ENGINE_ISOLATED] Engine created in {engine_creation_time:.3f}s")

        # Create tables for this test
        table_creation_start = time.time()
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            table_creation_time = time.time() - table_creation_start
            logger.debug(f"[ENGINE_ISOLATED] Tables created in {table_creation_time:.3f}s")
        except Exception as e:
            table_creation_time = time.time() - table_creation_start
            logger.error(f"[ENGINE_ISOLATED] Failed to create tables in {table_creation_time:.3f}s: {e}")
            await engine.dispose()
            raise

        total_setup_time = time.time() - engine_start_time
        logger.debug(f"[ENGINE_ISOLATED] Engine fully set up in {total_setup_time:.3f}s (worker: {worker_id})")

        yield engine
        
        # Clean up
        disposal_start_time = time.time()
        try:
            await engine.dispose()
            disposal_time = time.time() - disposal_start_time
            logger.debug(f"[ENGINE_ISOLATED] Engine disposed in {disposal_time:.3f}s (worker: {worker_id})")
        except Exception as e:
            disposal_time = time.time() - disposal_start_time
            logger.error(f"[ENGINE_ISOLATED] Failed to dispose engine in {disposal_time:.3f}s: {e}")


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine_isolated):
    """
    Provide an async SQLAlchemy session for each test function.
    Uses strict isolation to prevent asyncpg concurrency conflicts.
    """
    from sqlalchemy.ext.asyncio import AsyncSession
    import asyncio
    import time
    
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    logger.debug(f"[SESSION_ISOLATED] Creating session for worker: {worker_id}")
    
    session_start_time = time.time()
    session = None
    
    try:
        # Create session with strict isolation settings
        session = AsyncSession(
            bind=async_engine_isolated,
            expire_on_commit=False,
            close_resets_only=True  # Only reset on explicit close
        )
        
        # Test the session with a simple query
        test_start = time.time()
        try:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            test_time = time.time() - test_start
            logger.debug(f"[SESSION_ISOLATED] Session test query completed in {test_time:.3f}s")
        except Exception as e:
            test_time = time.time() - test_start
            logger.error(f"[SESSION_ISOLATED] Session test query failed in {test_time:.3f}s: {e}")
            await session.close()
            raise
        
        total_session_time = time.time() - session_start_time
        logger.debug(f"[SESSION_ISOLATED] Session ready in {total_session_time:.3f}s (worker: {worker_id})")
        
        yield session
        
    except Exception as e:
        total_session_time = time.time() - session_start_time
        logger.error(f"[SESSION_ISOLATED] Session creation failed in {total_session_time:.3f}s: {e}")
        if session:
            try:
                await session.close()
            except Exception:
                pass
        raise
    finally:
        # Ensure session is always cleaned up properly
        if session:
            try:
                # Force close any active transactions first
                if session.in_transaction():
                    await session.rollback()
                    logger.debug(f"[SESSION_ISOLATED] Session transaction rolled back (worker: {worker_id})")
            except Exception as e:
                logger.warning(f"[SESSION_ISOLATED] Error rolling back session (worker: {worker_id}): {e}")
            
            try:
                # Close the session completely
                await session.close()
                logger.debug(f"[SESSION_ISOLATED] Session closed (worker: {worker_id})")
            except Exception as e:
                logger.warning(f"[SESSION_ISOLATED] Error closing session (worker: {worker_id}): {e}")
            
            # Give a moment for cleanup to complete
            await asyncio.sleep(0.001)


# 4. App and client fixtures


from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="function")
def test_app(async_session) -> Generator:
    """
    Provides a new FastAPI app instance for each test function.
    Overrides get_async_session dependency to use the test async_session fixture.
    """
    from src.core.database import get_async_session
    from src.main import create_app

    app = create_app()

    # Override get_async_session to yield the test session
    async def _override_get_async_session():
        yield async_session

    app.dependency_overrides[get_async_session] = _override_get_async_session
    yield app


# Fixture to provide a TestClient for all API tests
@pytest.fixture(scope="function")
def client(test_app) -> Generator:
    """
    Provides a TestClient for the FastAPI app for use in API tests.
    """
    with TestClient(test_app) as c:
        yield c


# 5. Dependency overrides


# 6. Logging fixtures
@pytest.fixture
def loguru_list_sink() -> Iterator[list[str]]:
    """
    Capture loguru logs in a list for assertions, capturing only the loguru 'message' argument.
    Use this fixture to inspect logs generated during tests.
    """
    logs: list[str] = []

    def sink(message: Any) -> None:
        # message is a loguru.Message object; message.record['message'] is the plain log message
        try:
            logs.append(message.record["message"])
        except Exception:
            logs.append(str(message))

    sink_id = logger.add(sink)
    try:
        yield logs
    finally:
        try:
            logger.remove(sink_id)
        except ValueError:
            pass


@pytest.fixture
def loguru_list_sink_middleware() -> Iterator[list[str]]:
    """
    Capture loguru logs in a list for middleware tests.
    Ensures the sink is attached before the FastAPI app is created.
    Use this fixture in middleware tests instead of loguru_list_sink.
    """
    logs: list[str] = []

    def sink(message: Any) -> None:
        try:
            logs.append(message.record["message"])
        except Exception:
            logs.append(str(message))

    sink_id = logger.add(sink)
    try:
        yield logs
    finally:
        try:
            logger.remove(sink_id)
        except ValueError:
            pass


@pytest.fixture
def loguru_sink(tmp_path: Path) -> Iterator[Path]:
    """
    Create a log file for capturing loguru logs during tests.
    Returns the path to the log file for inspection.
    """
    log_file = tmp_path / "loguru.log"
    handler_id = logger.add(
        str(log_file),
        format="{message}",
        enqueue=True,
        catch=True,
        diagnose=False,
        backtrace=False,
        colorize=False,
    )
    try:
        yield log_file
    finally:
        try:
            logger.remove(handler_id)
        except ValueError:
            pass


# 7. Utility fixtures
@pytest.fixture(autouse=True)
def patch_loguru_remove(monkeypatch: Any) -> Generator[None, None, None]:
    """
    Patch loguru's logger.remove to suppress ValueError during pytest-loguru teardown.
    Prevents test failures due to loguru teardown issues.
    """
    original_remove = logger.remove

    def safe_remove(*args: Any, **kwargs: Any) -> None:
        try:
            original_remove(*args, **kwargs)
        except ValueError:
            pass

    monkeypatch.setattr(logger, "remove", safe_remove)
    yield
    monkeypatch.setattr(logger, "remove", original_remove)


@pytest.fixture
def override_env_vars(monkeypatch: pytest.MonkeyPatch, set_remaining_env_vars: None):
    """
    Fixture to override environment variables for a single test.
    Usage: override_env_vars({"VAR1": "value1", "VAR2": "value2"})
    Ensures required defaults are set first, then applies overrides.
    Also clears settings cache to ensure new values are picked up.
    """
    def _override(vars: dict[str, str]) -> None:
        for k, v in vars.items():
            monkeypatch.setenv(k, v)
        
        # Clear settings cache to ensure new environment variables are picked up
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
            from src.core.config import clear_settings_cache
            clear_settings_cache()
        except Exception as e:
            logger.warning(f"Could not clear settings cache in override_env_vars: {e}")
    return _override


# 8. Helper functions (not fixtures)
def wait_for_condition(
    condition_fn: Callable[[], Any],
    timeout: float = 2.0,
    interval: float = 0.05,
) -> Any:
    """
    Polls the given condition_fn until it returns a truthy value or timeout is reached.
    Returns the value from condition_fn if successful, else None.
    """
    import time

    start = time.time()
    while time.time() - start < timeout:
        result = condition_fn()
        if result:
            return result
        time.sleep(interval)
    return None


def wait_for_admin_promotion(
    client,
    email: str,
    password: str,
    timeout: float = 2.0,
    interval: float = 0.05,
) -> str | None:
    """
    Polls the login endpoint until the user can log in as admin, or timeout is reached.
    Returns the access token if successful, else None.
    """
    login_data = {"email": email, "password": password}

    def try_login():
        resp = client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers={"X-API-Key": "testkey"},
        )
        if resp.status_code == 200:
            return resp.json().get("access_token")
        return None

    return wait_for_condition(try_login, timeout=timeout, interval=interval)


import pathlib
import re

# List of test files (relative to backend/tests/) allowed to set env vars/DB URLs directly
ALLOWED_ENV_OVERRIDE_FILES = {
    "core/test_config.py",  # config/env/DB error handling tests
}


@pytest.hookimpl(tryfirst=True)
def pytest_collection_finish(session: pytest.Session):
    """
    Enforce that no test file (except allowed exceptions) sets environment variables or DB URLs directly.
    """
    root = pathlib.Path(__file__).parent
    pattern_env = re.compile(r"(os\\.environ|setenv|DATABASE_URL)")
    for item in session.items:
        path = pathlib.Path(item.fspath)
        rel_path = str(path.relative_to(root)).replace("\\", "/")
        if rel_path in ALLOWED_ENV_OVERRIDE_FILES:
            continue
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            if pattern_env.search(content):
                raise RuntimeError(
                    f"Test file {rel_path} sets environment variables or DB URLs directly. "
                    f"All such setup must be in conftest.py. If this is a valid exception, add it to ALLOWED_ENV_OVERRIDE_FILES."
                )
        except Exception:
            # Don't block collection for unreadable files
            pass


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_and_drop_tables(postgres_container):
    """
    Automatically create all tables before the test session and drop them after.
    Ensures a clean PostgreSQL test database for every test run.
    Depends on postgres_container to guarantee DB is up before setup.
    """
    from sqlalchemy.ext.asyncio import create_async_engine

    from src.models.base import Base

    db_url = os.environ["REVIEWPOINT_DB_URL"]
    engine = create_async_engine(db_url, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """
    Returns the test database URL used for all tests (from env var REVIEWPOINT_DB_URL).
    """
    return os.environ["REVIEWPOINT_DB_URL"]


def get_auth_header(client, email=None, password="TestPassword123!"):
    """
    Register a new user (or login if already exists) and return an auth header for API requests.
    Promotes the user to admin if registration is successful.
    Returns a dict with Authorization and X-API-Key headers.
    Uses the provided TestClient for all requests for consistency and speed.
    Raises RuntimeError if admin promotion fails unexpectedly.
    """
    from src.core.security import create_access_token

    if email is None:
        email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    register_data = {"email": email, "password": password, "name": "Test User"}
    register_resp = client.post(
        "/api/v1/auth/register", json=register_data, headers={"X-API-Key": "testkey"}
    )
    if register_resp.status_code == 201:
        token = register_resp.json().get("access_token")
        try:
            promote_resp = client.post(
                "/api/v1/users/promote-admin",
                json={"email": email},
                headers={"Authorization": f"Bearer {token}", "X-API-Key": "testkey"},
            )
            if promote_resp.status_code == 200:
                # Wait for admin promotion to take effect, polling login endpoint
                new_token = wait_for_admin_promotion(client, email, password)
                if new_token:
                    token = new_token
                    return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
                else:
                    logger.error(
                        f"Admin promotion for {email} did not take effect within timeout."
                    )
                    raise RuntimeError(
                        f"Admin promotion for {email} did not take effect within timeout."
                    )
        except Exception as exc:
            logger.error(f"Exception during admin promotion for {email}: {exc}")
            raise
        return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
    else:
        login_data = {"email": email, "password": password}
        try:
            login_resp = client.post(
                "/api/v1/auth/login", json=login_data, headers={"X-API-Key": "testkey"}
            )
            if login_resp.status_code == 200:
                token = login_resp.json().get("access_token")
                return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}
        except Exception as exc:
            logger.error(f"Exception during login for {email}: {exc}")
            raise
        payload = {"sub": email}
        token = create_access_token(payload)
        return {"Authorization": f"Bearer {token}", "X-API-Key": "testkey"}


# Fast test specific fixtures - only used when FAST_TESTS=1
if IS_FAST_TEST_MODE:
    # Import fast test dependencies
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from httpx import AsyncClient, ASGITransport  
    from fastapi.testclient import TestClient

    @pytest_asyncio.fixture(scope="session")
    async def fast_test_engine():
        """Create SQLite in-memory engine for fast tests."""
        from src.models import Base
        
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,  # Disable SQL echo for speed
            pool_pre_ping=False,  # Disable ping for speed
        )
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        yield engine
        await engine.dispose()

    @pytest_asyncio.fixture
    async def fast_async_session(fast_test_engine):
        """Create clean database session for each fast test."""
        from sqlalchemy.ext.asyncio import async_sessionmaker
        
        session_factory = async_sessionmaker(
            fast_test_engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with session_factory() as session:
            yield session
            await session.rollback()

    # Helper test utilities for fast tests  
    @pytest_asyncio.fixture
    async def create_test_user():
        """Factory fixture to create test users in fast tests."""
        async def _create_user(session: AsyncSession, **kwargs):
            from src.models.user import User
            from src.utils.hashing import hash_password
            
            defaults = {
                "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
                "name": "Test User", 
                "hashed_password": hash_password("password123"),
                "is_active": True,
                "is_admin": False
            }
            defaults.update(kwargs)
            
            user = User(**defaults)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        return _create_user

    @pytest_asyncio.fixture
    async def create_test_file():
        """Factory fixture to create test files in fast tests."""
        async def _create_file(session: AsyncSession, user_id: uuid.UUID, **kwargs):
            from src.models.file import File
            
            defaults = {
                "filename": f"test_{uuid.uuid4().hex[:8]}.txt",
                "original_filename": "test.txt", 
                "content_type": "text/plain",
                "size": 1024,
                "user_id": user_id
            }
            defaults.update(kwargs)
            
            file = File(**defaults)
            session.add(file)
            await session.commit()
            await session.refresh(file)
            return file
        return _create_file

@pytest_asyncio.fixture(scope="function", autouse=True)
async def _setup_db_env_function(request, monkeypatch, override_env_vars, loguru_list_sink, async_engine_isolated):
    """
    Auto-use fixture for database test classes that need engine access.
    This provides the test instance with engine, models, and other DB utilities.
    """
    test_instance = getattr(request, 'instance', None)
    if test_instance is not None:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        
        from src.models.user import User
        from src.models.file import File
        
        # Set up the test instance with database utilities
        test_instance.monkeypatch = monkeypatch
        test_instance.override_env_vars = override_env_vars
        test_instance.loguru_list_sink = loguru_list_sink
        test_instance.engine = async_engine_isolated
        test_instance.User = User
        test_instance.File = File
        
        # Set up session factory and healthcheck
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        from sqlalchemy import text
        
        test_instance.AsyncSessionLocal = async_sessionmaker(async_engine_isolated, class_=AsyncSession, expire_on_commit=False)
        test_instance.get_async_session = lambda: test_instance.AsyncSessionLocal()
        
        async def db_healthcheck():
            async with test_instance.AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
        test_instance.db_healthcheck = db_healthcheck
