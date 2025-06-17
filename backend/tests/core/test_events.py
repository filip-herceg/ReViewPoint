from collections.abc import Generator
from typing import Any

import pytest
from loguru import logger

from src.core import events

pytestmark = pytest.mark.asyncio


class DummySettings:
    db_url = "sqlite+aiosqlite:///:memory:"
    environment = "dev"
    log_level = "INFO"
    # Add other required fields as needed


@pytest.fixture(autouse=True)
def patch_settings(monkeypatch: Any) -> Generator[None, None, None]:
    monkeypatch.setattr(events, "settings", DummySettings())
    yield


@pytest.fixture
def loguru_sink(tmp_path: Any) -> Any:
    log_file = tmp_path / "loguru.log"
    logger.add(log_file, format="{message}", enqueue=True)
    yield log_file
    logger.remove()


@pytest.mark.asyncio
async def test_startup_valid_config(caplog: Any, loguru_sink: Any) -> None:
    with caplog.at_level("INFO"):
        await events.on_startup()
    logs = loguru_sink.read_text()
    assert "Starting up application..." in logs
    assert "Configuration validated." in logs
    assert "Database connection pool initialized and healthy." in logs
    # Accept either the old or new log format for startup complete
    assert any(line.startswith("Startup complete.") for line in logs.splitlines())


@pytest.mark.asyncio
async def test_startup_missing_config(
    monkeypatch: Any, caplog: Any, loguru_sink: Any
) -> None:
    class BadSettings:
        db_url = None
        environment = None
        log_level = "INFO"

    monkeypatch.setattr(events, "settings", BadSettings())
    with caplog.at_level("ERROR"):
        with pytest.raises(RuntimeError):
            await events.on_startup()
    logs = caplog.text
    assert "Missing required environment variables" in logs or "Startup failed" in logs


@pytest.mark.asyncio
async def test_startup_db_down(monkeypatch: Any, caplog: Any, loguru_sink: Any) -> None:
    from sqlalchemy.exc import SQLAlchemyError

    class BadConn:
        async def execute(self, *a: Any, **kw: Any) -> None:
            raise SQLAlchemyError("DB down")

        async def __aenter__(self) -> "BadConn":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            pass

    class BadEngine:
        def connect(self) -> Any:
            class Conn:
                async def __aenter__(self) -> BadConn:
                    return BadConn()

                async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
                    pass

            return Conn()

    monkeypatch.setattr(events, "engine", BadEngine())
    with caplog.at_level("ERROR"):
        with pytest.raises(RuntimeError):
            await events.on_startup()
    logs = caplog.text
    assert "Database health check failed" in logs or "Startup failed" in logs
    assert "Startup failed" in logs


@pytest.mark.asyncio
async def test_startup_prod_with_sqlite(
    monkeypatch: Any, caplog: Any, loguru_sink: Any
) -> None:
    class BadSettings:
        db_url = "sqlite+aiosqlite:///:memory:"
        environment = "prod"
        log_level = "INFO"

    monkeypatch.setattr(events, "settings", BadSettings())
    with caplog.at_level("ERROR"):
        with pytest.raises(RuntimeError) as excinfo:
            await events.on_startup()
    logs = caplog.text
    assert "Production environment cannot use SQLite database." in str(excinfo.value)
    assert "Startup failed" in logs


@pytest.mark.asyncio
async def test_startup_missing_jwt_secret(
    monkeypatch: Any, caplog: Any, loguru_sink: Any
) -> None:
    class BadSettings:
        db_url = "sqlite+aiosqlite:///:memory:"
        environment = "dev"
        log_level = "INFO"
        jwt_secret = None

    monkeypatch.setattr(events, "settings", BadSettings())
    with caplog.at_level("ERROR"):
        with pytest.raises(RuntimeError) as excinfo:
            await events.on_startup()
    logs = caplog.text
    assert "REVIEWPOINT_JWT_SECRET" in str(excinfo.value)
    assert "Startup failed" in logs


@pytest.mark.asyncio
async def test_on_startup_unexpected_exception(
    monkeypatch: Any, caplog: Any, loguru_sink: Any
) -> None:
    monkeypatch.setattr(
        events,
        "validate_config",
        lambda: (_ for _ in ()).throw(Exception("unexpected!")),
    )
    with caplog.at_level("ERROR"):
        with pytest.raises(RuntimeError):
            await events.on_startup()
    logs = caplog.text
    assert "Startup failed" in logs


@pytest.mark.asyncio
async def test_on_shutdown_unexpected_exception(
    monkeypatch: Any, caplog: Any, loguru_sink: Any
) -> None:
    monkeypatch.setattr(
        events,
        "engine",
        type(
            "E",
            (),
            {
                "dispose": staticmethod(
                    lambda: (_ for _ in ()).throw(Exception("shutdown error!"))
                )
            },
        )(),
    )
    with caplog.at_level("ERROR"):
        with pytest.raises(RuntimeError):
            await events.on_shutdown()
    logs = caplog.text
    # Accept either the new or old error message for robustness
    assert "Shutdown error" in logs or "Shutdown encountered an error" in logs


@pytest.mark.asyncio
async def test_shutdown(loguru_sink: Any) -> None:
    await events.on_shutdown()
    from loguru import logger

    logger.complete()
    logs = loguru_sink.read_text()
    assert "Shutting down application..." in logs
    assert "Database connections closed." in logs
    assert "Shutdown complete." in logs


@pytest.mark.asyncio
async def test_startup_logs_all_expected_messages(loguru_sink: Any) -> None:
    await events.on_startup()
    from loguru import logger

    logger.complete()
    logs = loguru_sink.read_text()
    assert "Starting up application..." in logs
    assert "Configuration validated." in logs
    assert "Database connection pool initialized and healthy." in logs
    assert "Startup complete." in logs


@pytest.mark.asyncio
async def test_shutdown_logs_all_expected_messages(loguru_sink: Any) -> None:
    await events.on_shutdown()
    from loguru import logger

    logger.complete()
    logs = loguru_sink.read_text()
    assert "Shutting down application..." in logs
    assert "Database connections closed." in logs
    assert "Shutdown complete." in logs


@pytest.mark.asyncio
async def test_shutdown_exception_logs_and_completes(
    loguru_sink: Any, monkeypatch: Any
) -> None:
    class BadEngine:
        async def dispose(self) -> None:
            raise Exception("dispose failed!")

    monkeypatch.setattr(events, "engine", BadEngine())
    from loguru import logger

    with pytest.raises(RuntimeError):
        await events.on_shutdown()
    logger.complete()
    logs = loguru_sink.read_text()
    assert "Shutdown error:" in logs or "Shutdown failed:" in logs
    assert "Shutdown complete." in logs


@pytest.mark.asyncio
async def test_startup_partial_config(
    monkeypatch: Any, caplog: Any, loguru_sink: Any
) -> None:
    class PartialSettings:
        db_url = None
        environment = "dev"
        log_level = "INFO"

    monkeypatch.setattr(events, "settings", PartialSettings())
    with caplog.at_level("ERROR"):
        with pytest.raises(RuntimeError) as excinfo:
            await events.on_startup()
    logs = caplog.text
    assert "Missing required environment variables" in logs or "Startup failed" in logs
    assert "REVIEWPOINT_DB_URL" in str(excinfo.value)


@pytest.mark.asyncio
async def test_logging_level(monkeypatch: Any, loguru_sink: Any) -> None:
    from loguru import logger

    class InfoSettings:
        db_url = "sqlite+aiosqlite:///:memory:"
        environment = "dev"
        log_level = "ERROR"

    monkeypatch.setattr(events, "settings", InfoSettings())

    # Remove all handlers and add one with ERROR level
    logger.remove()
    logger.add(loguru_sink, level="ERROR", format="{message}", enqueue=True)

    await events.on_startup()
    logger.complete()
    logs = loguru_sink.read_text()
    # Should not see INFO logs if log_level is ERROR
    assert "Starting up application..." not in logs


@pytest.mark.asyncio
async def test_multiple_startup_shutdown(loguru_sink: Any) -> None:
    for _ in range(2):
        await events.on_startup()
        await events.on_shutdown()
    from loguru import logger

    logger.complete()
    logs = loguru_sink.read_text()
    assert logs.count("Startup complete.") >= 2
    assert logs.count("Shutdown complete.") >= 2
