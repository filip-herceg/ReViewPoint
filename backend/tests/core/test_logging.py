from __future__ import annotations

import importlib
import logging

from backend.tests.test_templates import LogCaptureTestTemplate

MODULE = "src.core.logging"


class TestLogging(LogCaptureTestTemplate):
    def reload_logging(self):
        import sys

        if MODULE in sys.modules:
            importlib.reload(sys.modules[MODULE])
        return importlib.import_module(MODULE)

    def test_root_level_and_format(self, capsys):
        log_mod = self.reload_logging()
        log_mod.init_logging(level="DEBUG")
        logging.getLogger("test").debug("hello")
        out = capsys.readouterr().out
        assert "DEBUG" in out and "hello" in out

    def test_color_and_json_flags(self, capsys):
        log_mod = self.reload_logging()
        log_mod.init_logging(level="INFO", color=False)
        logging.getLogger().info("color-off")
        out = capsys.readouterr().out
        assert "color-off" in out
        log_mod.init_logging(level="INFO", json=True)
        logging.getLogger().info("json")
        out2 = capsys.readouterr().out
        assert "json" in out2

    def test_idempotent(self):
        log_mod = self.reload_logging()
        log_mod.init_logging()
        first_cnt = len(logging.root.handlers)
        log_mod.init_logging()
        assert len(logging.root.handlers) == first_cnt

    def test_uvicorn_access_muted(self):
        log_mod = self.reload_logging()
        log_mod.init_logging()
        assert logging.getLogger("uvicorn.access").propagate is False

    def test_structured_extra(self, capsys):
        log_mod = self.reload_logging()
        log_mod.init_logging(json=True)
        logging.getLogger("svc").info("with-extra", extra={"request_id": "abc"})
        out = capsys.readouterr().out
        assert "with-extra" in out

    def test_file_logging(self, tmp_path):
        log_mod = self.reload_logging()
        logfile = tmp_path / "app.log"
        log_mod.init_logging(level="INFO", logfile=str(logfile))
        logging.getLogger().info("to-file")
        assert logfile.exists() and "to-file" in logfile.read_text()

    def test_core_logging_import_smoke(self):
        import src.core.logging

        assert hasattr(src.core.logging, "init_logging")
