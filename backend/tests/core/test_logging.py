from __future__ import annotations

import importlib
import logging
import sys
from pathlib import Path
from types import ModuleType
from typing import Final

import pytest
from _pytest.capture import CaptureFixture
from _pytest.tmpdir import TempPathFactory

from tests.test_templates import LogCaptureTestTemplate

MODULE: Final[str] = "src.core.logging"


class TestLogging(LogCaptureTestTemplate):
    """Test class for logging configuration and functionality."""

    def reload_logging(self) -> ModuleType:
        """
        Reload the logging module to ensure clean state between tests.
        
        Returns:
            The reloaded logging module.
        """
        if MODULE in sys.modules:
            importlib.reload(sys.modules[MODULE])
        return importlib.import_module(MODULE)

    def test_root_level_and_format(self, capsys: CaptureFixture[str]) -> None:
        """Test that logging level and format are correctly applied."""
        log_mod: ModuleType = self.reload_logging()
        log_mod.init_logging(level="DEBUG")
        test_logger: logging.Logger = logging.getLogger("test")
        test_logger.debug("hello")
        out: str = capsys.readouterr().out
        assert "DEBUG" in out and "hello" in out

    def test_color_and_json_flags(self, capsys: CaptureFixture[str]) -> None:
        """Test that color and JSON flags work correctly."""
        log_mod: ModuleType = self.reload_logging()
        log_mod.init_logging(level="INFO", color=False)
        logging.getLogger().info("color-off")
        out: str = capsys.readouterr().out
        assert "color-off" in out
        log_mod.init_logging(level="INFO", json=True)
        logging.getLogger().info("json")
        out2: str = capsys.readouterr().out
        assert "json" in out2

    def test_idempotent(self) -> None:
        """Test that init_logging is idempotent (can be called multiple times safely)."""
        log_mod: ModuleType = self.reload_logging()
        log_mod.init_logging()
        first_cnt: int = len(logging.root.handlers)
        log_mod.init_logging()
        assert len(logging.root.handlers) == first_cnt

    def test_uvicorn_access_muted(self) -> None:
        """Test that uvicorn.access logger propagation is disabled."""
        log_mod: ModuleType = self.reload_logging()
        log_mod.init_logging()
        assert logging.getLogger("uvicorn.access").propagate is False

    def test_structured_extra(self, capsys: CaptureFixture[str]) -> None:
        """Test that structured logging with extra fields works correctly."""
        log_mod: ModuleType = self.reload_logging()
        log_mod.init_logging(json=True)
        logging.getLogger("svc").info("with-extra", extra={"request_id": "abc"})
        out: str = capsys.readouterr().out
        assert "with-extra" in out

    def test_file_logging(self, tmp_path: Path) -> None:
        """Test that logging to file works correctly."""
        log_mod: ModuleType = self.reload_logging()
        logfile: Path = tmp_path / "app.log"
        log_mod.init_logging(level="INFO", logfile=str(logfile))
        logging.getLogger().info("to-file")
        assert logfile.exists() and "to-file" in logfile.read_text()

    def test_core_logging_import_smoke(self) -> None:
        """Smoke test to ensure the logging module can be imported and has expected attributes."""
        import src.core.logging

        assert hasattr(src.core.logging, "init_logging")
