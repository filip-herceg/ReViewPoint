"""Tests for application startup/shutdown events using EventTestTemplate."""

import pytest

from src.core import events
from tests.test_templates import EventTestTemplate


class DummySettings:
    db_url = "postgresql+asyncpg://user:password@localhost/testdb"
    environment = "dev"
    log_level = "INFO"
    # Add other required fields as needed


class BadSettings:
    db_url = None
    environment = None
    log_level = "INFO"


class TestEvents(EventTestTemplate):
    @pytest.mark.asyncio
    async def test_startup_valid_config(self):
        self.patch_settings(events, DummySettings())
        with self.caplog.at_level("INFO"):
            await events.on_startup()
        logs = self.get_loguru_text()
        assert "Starting up application..." in logs
        assert "Configuration validated." in logs
        assert "Database connection pool initialized and healthy." in logs
        assert "Startup complete" in logs

    @pytest.mark.asyncio
    async def test_startup_missing_config(self):
        self.patch_settings(events, BadSettings())
        with self.caplog.at_level("ERROR"):
            with pytest.raises(RuntimeError):
                await events.on_startup()
        self.assert_caplog_contains(
            "Missing required environment variables", level="ERROR"
        )
        self.assert_caplog_contains("Startup failed", level="ERROR")

    @pytest.mark.asyncio
    async def test_shutdown_logs(self):
        self.patch_settings(events, DummySettings())
        with self.caplog.at_level("INFO"):
            await events.on_shutdown()
        logs = self.get_loguru_text()
        assert "Shutting down application..." in logs
        assert "Database connections closed." in logs
        assert "Shutdown complete." in logs

    @pytest.mark.asyncio
    async def test_startup_db_healthcheck_error(self, monkeypatch):
        self.patch_settings(events, DummySettings())
        monkeypatch.setattr(
            events,
            "db_healthcheck",
            lambda: (_ for _ in ()).throw(RuntimeError("db fail")),
        )
        with self.caplog.at_level("ERROR"):
            with pytest.raises(RuntimeError) as excinfo:
                await events.on_startup()
        assert "db fail" in str(excinfo.value)
        self.assert_caplog_contains("Startup failed", level="ERROR")

    @pytest.mark.asyncio
    async def test_startup_unexpected_exception(self, monkeypatch):
        self.patch_settings(events, DummySettings())
        monkeypatch.setattr(
            events, "validate_config", lambda: (_ for _ in ()).throw(Exception("boom"))
        )
        with self.caplog.at_level("ERROR"):
            with pytest.raises(RuntimeError) as excinfo:
                await events.on_startup()
        assert "boom" in str(excinfo.value)
        self.assert_caplog_contains("Startup failed", level="ERROR")

    @pytest.mark.asyncio
    async def test_shutdown_handles_exception(self, monkeypatch):
        self.patch_settings(events, DummySettings())
        monkeypatch.setattr(
            events.engine,
            "dispose",
            lambda: (_ for _ in ()).throw(Exception("dispose fail")),
        )
        with self.caplog.at_level("ERROR"):
            with pytest.raises(RuntimeError) as excinfo:
                await events.on_shutdown()
        assert "dispose fail" in str(excinfo.value)
        self.assert_caplog_contains("Shutdown error", level="ERROR")
        self.assert_caplog_contains("Shutdown complete.")

    @pytest.mark.asyncio
    async def test_startup_with_legacy_jwt_secret(self):
        class LegacyJwtSettings(DummySettings):
            jwt_secret = "legacy"
            jwt_secret_key = None

        self.patch_settings(events, LegacyJwtSettings())
        with self.caplog.at_level("INFO"):
            await events.on_startup()
        logs = self.get_loguru_text()
        assert "Startup complete" in logs
