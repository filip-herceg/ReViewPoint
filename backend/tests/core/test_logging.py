from __future__ import annotations

import importlib
import json
import logging
import re
import sys
from pathlib import Path
from types import ModuleType

from _pytest.logging import LogCaptureFixture

# Add the backend directory to the path for imports
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

MODULE = "core.logging"


def _reload() -> ModuleType:
    """Reload core.logging frisch, reset Handler."""
    if MODULE in sys.modules:
        importlib.reload(sys.modules[MODULE])
    return importlib.import_module(MODULE)


# --------------------------------------------------------------------------- #
# 1) root level & basic format                                                #
# --------------------------------------------------------------------------- #


def test_root_level_and_format(caplog: LogCaptureFixture):
    log_mod = _reload()
    log_mod.init_logging(level="DEBUG")
    assert logging.root.level == logging.DEBUG

    with caplog.at_level(logging.DEBUG):
        logging.getLogger("test").debug("hello")

    line = caplog.text.rstrip().splitlines()[-1]
    assert re.search(r"\d{4}-\d{2}-\d{2}", line)
    assert "DEBUG" in line and "test" in line
    assert caplog.records[-1].message == "hello"


# --------------------------------------------------------------------------- #
# 2) color off & json on                                                      #
# --------------------------------------------------------------------------- #
def test_color_and_json_flags(caplog: LogCaptureFixture):
    log_mod = _reload()
    log_mod.init_logging(level="INFO", color=False)
    logging.getLogger().info("color-off")
    assert "\x1b[" not in caplog.text  # no ANSI

    caplog.clear()
    log_mod.init_logging(level="INFO", json=True)
    logging.getLogger().info("json")
    json.loads(caplog.text.splitlines()[-1])  # parses


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
def test_structured_extra(caplog: LogCaptureFixture):
    log_mod = _reload()
    log_mod.init_logging(json=True)
    with caplog.at_level(logging.INFO):
        logging.getLogger("svc").info("with-extra", extra={"request_id": "abc"})
    payload = json.loads(caplog.text.splitlines()[-1])
    assert payload["request_id"] == "abc"
    assert payload["msg"] == "with-extra"


# --------------------------------------------------------------------------- #
# 6) file handler writes to disk (optional)                                   #
# --------------------------------------------------------------------------- #
def test_file_logging(tmp_path: Path):
    log_mod = _reload()
    logfile = tmp_path / "app.log"
    log_mod.init_logging(level="INFO", logfile=str(logfile))

    logging.getLogger().info("to-file")
    assert logfile.exists() and "to-file" in logfile.read_text()
