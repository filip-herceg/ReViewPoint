from __future__ import annotations

import importlib
import logging
from pathlib import Path
from types import ModuleType

import pytest

import src.core.logging  # Ensure coverage always sees this import

MODULE = "src.core.logging"


def _reload() -> ModuleType:
    """Reload core.logging frisch, reset Handler."""
    import sys
    if MODULE in sys.modules:
        importlib.reload(sys.modules[MODULE])
    return importlib.import_module(MODULE)


# --------------------------------------------------------------------------- #
# 1) root level & basic format                                                #
# --------------------------------------------------------------------------- #


def test_root_level_and_format(capsys: pytest.CaptureFixture[str]) -> None:
    log_mod = _reload()
    log_mod.init_logging(level="DEBUG")
    import logging

    logging.getLogger("test").debug("hello")
    out: str = capsys.readouterr().out
    assert "DEBUG" in out and "hello" in out


# --------------------------------------------------------------------------- #
# 2) color off & json on                                                      #
# --------------------------------------------------------------------------- #
def test_color_and_json_flags(capsys: pytest.CaptureFixture[str]) -> None:
    log_mod = _reload()
    log_mod.init_logging(level="INFO", color=False)
    import logging

    logging.getLogger().info("color-off")
    out: str = capsys.readouterr().out
    assert "color-off" in out
    log_mod.init_logging(level="INFO", json=True)
    logging.getLogger().info("json")
    out2: str = capsys.readouterr().out
    assert "json" in out2


# --------------------------------------------------------------------------- #
# 3) idempotent init                                                          #
# --------------------------------------------------------------------------- #
def test_idempotent():
    log_mod = _reload()
    log_mod.init_logging()
    first_cnt = len(logging.root.handlers)
    log_mod.init_logging()
    assert len(logging.root.handlers) == first_cnt


# --------------------------------------------------------------------------- #
# 4) uvicorn access logger muted                                              #
# --------------------------------------------------------------------------- #
def test_uvicorn_access_muted():
    log_mod = _reload()
    log_mod.init_logging()
    assert logging.getLogger("uvicorn.access").propagate is False


# --------------------------------------------------------------------------- #
# 5) structured extra fields (JSON mode)                                      #
# --------------------------------------------------------------------------- #
def test_structured_extra(capsys: pytest.CaptureFixture[str]) -> None:
    log_mod = _reload()
    log_mod.init_logging(json=True)
    import logging

    logging.getLogger("svc").info("with-extra", extra={"request_id": "abc"})
    out: str = capsys.readouterr().out
    assert "with-extra" in out


# --------------------------------------------------------------------------- #
# 6) file handler writes to disk (optional)                                   #
# --------------------------------------------------------------------------- #
def test_file_logging(tmp_path: Path):
    log_mod = _reload()
    logfile = tmp_path / "app.log"
    log_mod.init_logging(level="INFO", logfile=str(logfile))

    logging.getLogger().info("to-file")
    assert logfile.exists() and "to-file" in logfile.read_text()


# --------------------------------------------------------------------------- #
# 7) core.logging import smoke test                                           #
# --------------------------------------------------------------------------- #


def test_core_logging_import_smoke():
    assert hasattr(src.core.logging, "init_logging")
