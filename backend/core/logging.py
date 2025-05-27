"""Logging bootstrap for ReViewPoint backend.

Repeat-safe initialiser::

    from backend.core.logging import init_logging
    init_logging(level="DEBUG", color=True, json_format=False, logfile="app.log")

Only handlers created by this module are purged between calls; pytest-caplog &
other third-party handlers remain, but we re-apply our formatter so captured
output matches expectations.
"""

from __future__ import annotations

import json as _json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# ──────────────────────────── colour map ────────────────────────────
RESET = "\x1b[0m"
COLOR_MAP = {
    "DEBUG": "\x1b[36m",  # cyan
    "INFO": "\x1b[32m",  # green
    "WARNING": "\x1b[33m",  # yellow
    "ERROR": "\x1b[31m",  # red
    "CRITICAL": "\x1b[41m",  # red bg
}

# attribute used to mark handlers we own
_FLAG = "_rvp_internal"


class ColorFormatter(logging.Formatter):
    """Human-readable single-line formatter with optional ANSI colours."""

    def __init__(self, *, color: bool = True) -> None:
        super().__init__(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self._color = color

    def format(self, record: logging.LogRecord) -> str:
        text = super().format(record)
        if self._color:
            return f"{COLOR_MAP.get(record.levelname, '')}{text}{RESET}"
        return text


class JsonFormatter(logging.Formatter):
    """Minimal JSON Lines formatter."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(timespec="seconds"),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }
        # merge extras (exclude built-ins)
        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in logging.LogRecord.__dict__ and k not in payload
        }
        payload.update(extras)
        return _json.dumps(payload, default=str)


# ───────────────────────── helper ─────────────────────────


def _purge_our_handlers(root: logging.Logger) -> None:
    """Remove handlers previously attached by this module."""
    for h in list(root.handlers):
        if getattr(h, _FLAG, False):
            root.removeHandler(h)
            h.close()


# ───────────────────────── public API ─────────────────────────


def init_logging(
    *,
    level: str | int = "INFO",
    color: bool = True,
    json_format: bool = False,
    json: bool = False,
    logfile: str | Path | None = None,
) -> None:
    """Configure the root logger.

    Parameters
    ----------
    level : str | int
        Root log level.
    color : bool
        Enable ANSI colours for console output.
    json_format : bool
        Emit JSON lines instead of human format.
    logfile : str | Path | None
        Optional file to tee logs to.
    """

    root = logging.getLogger()

    _purge_our_handlers(root)
    root.setLevel(level)

    use_json = json or json_format
    formatter: logging.Formatter = (
        JsonFormatter() if use_json else ColorFormatter(color=color)
    )

    # console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.setLevel(level)
    console._rvp_internal = True  # type: ignore[attr-defined]
    root.addHandler(console)

    # optional file handler
    if logfile is not None:
        fp = Path(logfile)
        fp.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(fp, encoding="utf-8")
        fh.setFormatter(formatter)
        fh.setLevel(level)
        fh._rvp_internal = True  # type: ignore[attr-defined]
        root.addHandler(fh)

    # ensure third-party handlers (e.g. pytest caplog) use the same formatter
    for h in root.handlers:
        if not getattr(h, _FLAG, False):
            h.setFormatter(formatter)

    logging.getLogger("uvicorn.access").propagate = False
