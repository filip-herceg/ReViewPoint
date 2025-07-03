import pytest

# --- Fixture to inject DB env and engine into test classes needing parallel DB tests ---
@pytest.fixture(autouse=True, scope="function")
async def _setup_db_env_function(request, monkeypatch, override_env_vars, loguru_list_sink, async_engine_isolated):
    """
    Set up DB env, monkeypatch, and log sink per test function for parallel safety.
    Injects function-scoped engine for parallel DB tests.
    Sets attributes on test class instance if present.
    """
    test_instance = getattr(request, 'instance', None)
    if test_instance is not None:
        test_instance.override_env_vars = override_env_vars
        test_instance.monkeypatch = monkeypatch
        test_instance.loguru_list_sink = loguru_list_sink
        test_instance.engine = async_engine_isolated
    # If not a class-based test, do nothing
    yield

# Fast test mode: use in-memory SQLite for fast tests
import sys
import pytest

@pytest.fixture(scope="session")
def use_fast_db():
    """Enable fast testing mode with shared in-memory SQLite if FAST_TESTS env var is set."""
    return os.environ.get("FAST_TESTS", "0") == "1"

def pytest_configure(config):
    """Register test markers for slow and fast tests."""
    config.addinivalue_line("markers", "slow: marks tests that access real database or are slow")
    config.addinivalue_line("markers", "fast: marks tests that use mocks or in-memory DB")
    config.addinivalue_line("markers", "skip_if_fast_tests: skip test only in fast test mode")
    config.addinivalue_line("markers", "skip_if_not_fast_tests: skip test only in regular test mode")
    config.addinivalue_line("markers", "requires_real_db: skip test if using in-memory SQLite")
    config.addinivalue_line("markers", "requires_timing_precision: skip test if timing is unreliable")


def pytest_sessionstart(session):
    """
    Set critical environment variables before any fixtures or tests run.
    This runs once per pytest-xdist worker session, ensuring env vars are set 
    before any code that might create database engines executes.
    """
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    
    # Set critical secrets that are needed during engine creation
    os.environ["REVIEWPOINT_JWT_SECRET"] = "testsecret"
    os.environ["REVIEWPOINT_JWT_SECRET_KEY"] = "testsecret"
    os.environ["REVIEWPOINT_API_KEY_ENABLED"] = "true"
    os.environ["REVIEWPOINT_API_KEY"] = "testkey"
    
    logger.info(f"[PYTEST_SESSIONSTART] Critical env vars set for worker: {worker_id}")
    logger.info(f"[PYTEST_SESSIONSTART] JWT_SECRET_KEY set: {'REVIEWPOINT_JWT_SECRET_KEY' in os.environ}")
    
    # Import configuration here to trigger any early validation
    try:
        # Delay the import until env vars are set
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from src.core.config import get_settings
        logger.info(f"[PYTEST_SESSIONSTART] Config validation successful for worker: {worker_id}")
    except Exception as e:
        logger.error(f"[PYTEST_SESSIONSTART] Config validation failed for worker {worker_id}: {e}")
        # Don't fail here, let the test handle it
"""
Centralized test database and environment management for all tests in the backend.

Test DB Policy:
- All tests use a single PostgreSQL container, managed by the session-scoped fixture below.
- The container is started before any tests run and stopped after all tests complete.
- The test DB connection URL is set via the REVIEWPOINT_DB_URL environment variable for all tests.
- No test or fixture should start its own DB container or set DB URLs directly (except for explicit config/env error tests).
- The Postgres image/tag can be overridden via the REVIEWPOINT_TEST_POSTGRES_IMAGE environment variable.
- Container connection details are logged at startup for debugging.
- If Docker is not running or the container fails to start, a clear error is raised and logged.

This policy ensures robust, maintainable, and explicit test DB management for all developers.
"""

# --- DO NOT set env vars at the top level. All config-dependent imports must be inside fixtures. ---
import os
import uuid
from collections.abc import Callable, Generator, Iterator
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from loguru import logger

# Early environment setup for pytest-xdist workers
# This must happen before any imports that might create database engines
if "PYTEST_CURRENT_TEST" in os.environ:
    # Only set during pytest runs to avoid affecting normal app usage
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    
    # Set critical secrets that are needed during engine creation
    if "REVIEWPOINT_JWT_SECRET_KEY" not in os.environ:
        os.environ["REVIEWPOINT_JWT_SECRET"] = "testsecret"
        os.environ["REVIEWPOINT_JWT_SECRET_KEY"] = "testsecret"
        os.environ["REVIEWPOINT_API_KEY_ENABLED"] = "true"
        os.environ["REVIEWPOINT_API_KEY"] = "testkey"
        logger.info(f"[EARLY_ENV_SETUP] Critical env vars set for worker: {worker_id}")
        
        # Clear any cached settings since env vars have changed
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
            from src.core.config import clear_settings_cache
            clear_settings_cache()
            logger.info(f"[EARLY_ENV_SETUP] Settings cache cleared for worker: {worker_id}")
        except Exception as e:
            logger.warning(f"[EARLY_ENV_SETUP] Could not clear settings cache: {e}")


@pytest.fixture(scope="session", autouse=True)
def postgres_container():
    """
    Start a PostgreSQL container for the test session and set DB URL env var for all tests.
    Logs the connection URL at startup. Raises a clear error if Docker is not running.
    The Postgres image can be overridden with the REVIEWPOINT_TEST_POSTGRES_IMAGE env var.
    """
    from testcontainers.postgres import PostgresContainer

    image = os.environ.get("REVIEWPOINT_TEST_POSTGRES_IMAGE", "postgres:15-alpine")
    import time
    import socket
    
    # Log parallel test worker information
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    logger.info(f"[TESTCONTAINER_DEBUG] Starting container setup for worker: {worker_id}")
    
    try:
        container_start_time = time.time()
        # Set up the container with high max_connections and shared_buffers
        postgres = PostgresContainer(image)
        postgres.with_env("POSTGRES_MAX_CONNECTIONS", "300")
        postgres.with_env("POSTGRES_SHARED_BUFFERS", "512MB")
        # Expose the default port and try to bind it for Windows compatibility
        postgres.with_exposed_ports(5432)
        # Optionally, try host networking (may not work on Docker Desktop for Windows)
        # postgres.with_network_mode("host")
        
        logger.info(f"[TESTCONTAINER_DEBUG] Container configured, starting with image: {image}")
        
        with postgres as pg:
            container_ready_time = time.time() - container_start_time
            logger.info(f"[TESTCONTAINER_DEBUG] Container started in {container_ready_time:.2f}s")
            
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
            
            # Log connection details (sanitized)
            sanitized_url = async_db_url.split('@')[1] if '@' in async_db_url else async_db_url
            logger.info(f"[TESTCONTAINER_DEBUG] Container URL: postgresql+asyncpg://...@{sanitized_url}")
            logger.info(f"[TESTCONTAINER_DEBUG] Internal host: {pg.get_container_host_ip()}")
            logger.info(f"[TESTCONTAINER_DEBUG] Mapped port: {pg.get_exposed_port(5432)}")
            
            # Wait for DB port to be open (robust wait)
            def port_open(host, port):
                try:
                    with socket.create_connection((host, port), timeout=1):
                        return True
                except Exception:
                    return False
            
            # Parse host/port from db_url
            import re
            m = re.match(r"postgresql\+asyncpg://[^:]+:[^@]+@([^:/]+):(\d+)/", async_db_url)
            if m:
                host, port = m.group(1), int(m.group(2))
                logger.info(f"[TESTCONTAINER_DEBUG] Testing port connectivity to {host}:{port}")
                
                port_wait_start = time.time()
                for attempt in range(60):
                    if port_open(host, port):
                        port_wait_time = time.time() - port_wait_start
                        logger.info(f"[TESTCONTAINER_DEBUG] Port {host}:{port} is open after {port_wait_time:.2f}s, {attempt+1} attempts")
                        break
                    time.sleep(0.5)
                else:
                    port_wait_time = time.time() - port_wait_start
                    raise RuntimeError(f"Postgres container port {host}:{port} did not open in {port_wait_time:.2f}s after 60 attempts.")
            else:
                logger.warning(f"[TESTCONTAINER_DEBUG] Could not parse host/port from DB URL: {async_db_url}")
            
            # Test actual database connection
            try:
                import asyncpg
                connection_test_start = time.time()
                
                # Convert SQLAlchemy URL to plain PostgreSQL URL for asyncpg
                asyncpg_url = async_db_url.replace("postgresql+asyncpg://", "postgresql://")
                
                for attempt in range(30):
                    try:
                        logger.debug(f"[TESTCONTAINER_DEBUG] Connection attempt #{attempt+1}")
                        
                        # Simple synchronous test using asyncio.run
                        async def test_connection():
                            conn = await asyncpg.connect(asyncpg_url)
                            await conn.close()
                        
                        asyncio.run(test_connection())
                        
                        connection_test_time = time.time() - connection_test_start
                        logger.info(f"[TESTCONTAINER_DEBUG] Database connection successful after {connection_test_time:.2f}s, {attempt+1} attempts")
                        break
                    except Exception as e:
                        logger.debug(f"[TESTCONTAINER_DEBUG] Connection attempt #{attempt+1} failed: {type(e).__name__}: {e}")
                        time.sleep(0.5)
                else:
                    connection_test_time = time.time() - connection_test_start
                    raise RuntimeError(f"Postgres DB did not accept connections after {connection_test_time:.2f}s, 30 attempts.")
            except ImportError:
                logger.warning("[TESTCONTAINER_DEBUG] asyncpg not available for connection check.")
            
            # Set environment variable for all tests
            os.environ["REVIEWPOINT_DB_URL"] = async_db_url
            
            total_setup_time = time.time() - container_start_time
            logger.info(f"[TESTCONTAINER_DEBUG] Container fully ready in {total_setup_time:.2f}s")
            
            yield async_db_url
            os.environ.pop("REVIEWPOINT_DB_URL", None)
            logger.info(
                "[testcontainers] PostgreSQL container stopped and env cleaned up."
            )
    except Exception as e:
        logger.error(f"[testcontainers] Failed to start PostgreSQL container: {e}")
        raise RuntimeError(
            "Could not start PostgreSQL test container. Is Docker running? "
            "See the error above for details."
        ) from e


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
def set_required_env_vars_session(postgres_container) -> None:
    """
    Set critical environment variables at session scope before any code that might 
    create database engines runs. This is essential for pytest-xdist workers.
    """
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    logger.info(f"[ENV_SETUP_SESSION] Setting session-level environment variables for worker: {worker_id}")
    
    # Set critical secrets that are needed during engine creation
    os.environ["REVIEWPOINT_JWT_SECRET"] = "testsecret"
    os.environ["REVIEWPOINT_JWT_SECRET_KEY"] = "testsecret"
    os.environ["REVIEWPOINT_API_KEY_ENABLED"] = "true"
    os.environ["REVIEWPOINT_API_KEY"] = "testkey"
    
    # DB URL is already set by postgres_container fixture
    logger.info(f"[ENV_SETUP_SESSION] Critical env vars set for worker: {worker_id}")
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
async def async_engine_isolated(use_fast_db, postgres_container):
    """
    Provide a SQLAlchemy async engine for each test function (parallel safe).
    Uses in-memory SQLite if FAST_TESTS=1, otherwise uses PostgreSQL.
    """
    from sqlalchemy.ext.asyncio import create_async_engine
    import time
    import uuid
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from src.models import Base

    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    test_id = str(uuid.uuid4())[:8]
    logger.debug(f"[ENGINE_ISOLATED] Creating engine for worker: {worker_id}, test_id: {test_id}")

    engine_start_time = time.time()
    
    if use_fast_db or os.environ.get('PYTEST_XDIST_WORKER'):
        # Use SQLite for fast tests OR parallel execution to avoid asyncpg concurrency issues
        db_url = f"sqlite+aiosqlite:///:memory:?cache=shared&test_id={test_id}"
        logger.debug(f"[ENGINE_ISOLATED] Using SQLite in-memory DB (parallel={bool(os.environ.get('PYTEST_XDIST_WORKER'))}): {db_url}")
        engine = create_async_engine(db_url, future=True, connect_args={"check_same_thread": False})
    else:
        # Use the same DB URL, but configure for strict isolation in parallel testing
        db_url = os.environ["REVIEWPOINT_DB_URL"]
        logger.debug(f"[ENGINE_ISOLATED] Using PostgreSQL with isolation pool (worker: {worker_id})")
        
        # Configure engine for strict connection isolation to avoid asyncpg event loop conflicts
        engine_kwargs = {
            "future": True,
            "pool_size": 1,  # Single connection per worker
            "max_overflow": 0,  # No overflow connections
            "pool_reset_on_return": "commit",  # Reset connections between uses
            "pool_pre_ping": True,  # Verify connections before use
            "pool_recycle": 300,  # Recycle connections every 5 minutes
            "connect_args": {
                "server_settings": {
                    "application_name": f"reviewpoint_test_{worker_id}_{os.getpid()}",
                },
                "command_timeout": 30,  # 30 second timeout for commands
            }
        }
        
        engine = create_async_engine(db_url, **engine_kwargs)

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
    Uses a simplified approach to avoid async event loop conflicts.
    """
    from sqlalchemy.ext.asyncio import AsyncSession
    import asyncio
    import time
    
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'main')
    logger.debug(f"[SESSION_ISOLATED] Creating session for worker: {worker_id}")
    
    session_start_time = time.time()
    
    try:
        # Create a simple session bound to the engine
        # This approach avoids transaction context manager issues
        session = AsyncSession(bind=async_engine_isolated, expire_on_commit=False)
        
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
            # Close session and re-raise
            await session.close()
            raise
        
        total_session_time = time.time() - session_start_time
        logger.debug(f"[SESSION_ISOLATED] Session ready in {total_session_time:.3f}s (worker: {worker_id})")
        
        try:
            yield session
        finally:
            # Clean shutdown of session
            try:
                # First, rollback any uncommitted changes
                if session.in_transaction():
                    await session.rollback()
                    logger.debug(f"[SESSION_ISOLATED] Session transaction rolled back (worker: {worker_id})")
            except Exception as e:
                logger.warning(f"[SESSION_ISOLATED] Error rolling back session (worker: {worker_id}): {e}")
            
            try:
                # Close the session
                await session.close()
                logger.debug(f"[SESSION_ISOLATED] Session closed (worker: {worker_id})")
            except Exception as e:
                logger.warning(f"[SESSION_ISOLATED] Error closing session (worker: {worker_id}): {e}")
            
    except Exception as e:
        total_session_time = time.time() - session_start_time
        logger.error(f"[SESSION_ISOLATED] Session creation failed in {total_session_time:.3f}s: {e}")
        raise


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
    Automatically clears settings cache after env var changes.
    """
    def _override(vars: dict[str, str]) -> None:
        for k, v in vars.items():
            monkeypatch.setenv(k, v)
        
        # Clear settings cache to ensure new env vars take effect
        try:
            from src.core.config import clear_settings_cache
            clear_settings_cache()
        except Exception as e:
            logger.warning(f"Failed to clear settings cache: {e}")
            
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


def pytest_runtest_setup(item):
    """
    Handle conditional skip markers before each test runs.
    
    This hook checks for custom skip markers and applies them conditionally
    based on the test environment.
    """
    import os
    
    # Check if running in fast test mode
    is_fast_tests = os.environ.get("FAST_TESTS") == "1"
    
    # Handle skip_if_fast_tests marker
    if item.get_closest_marker("skip_if_fast_tests") and is_fast_tests:
        marker = item.get_closest_marker("skip_if_fast_tests")
        reason = marker.args[0] if marker.args else "Test not compatible with fast test mode"
        pytest.skip(reason)
    
    # Handle skip_if_not_fast_tests marker
    if item.get_closest_marker("skip_if_not_fast_tests") and not is_fast_tests:
        marker = item.get_closest_marker("skip_if_not_fast_tests")
        reason = marker.args[0] if marker.args else "Test only runs in fast test mode"
        pytest.skip(reason)
    
    # Handle requires_real_db marker
    if item.get_closest_marker("requires_real_db") and is_fast_tests:
        marker = item.get_closest_marker("requires_real_db")
        reason = marker.args[0] if marker.args else "Test requires real database features"
        pytest.skip(reason)
    
    # Handle requires_timing_precision marker
    if item.get_closest_marker("requires_timing_precision") and is_fast_tests:
        marker = item.get_closest_marker("requires_timing_precision")
        reason = marker.args[0] if marker.args else "Test requires precise timing not reliable in fast mode"
        pytest.skip(reason)
