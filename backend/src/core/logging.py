"""
Logging bootstrap for ReViewPoint backend.

Repeat-safe initialiser::

    from core.logging import init_logging
    init_logging(level="DEBUG", color=True, json_format=False, logfile="app.log")

Only handlers created by this module are purged between calls; pytest-caplog &
other third-party handlers remain, but we re-apply our formatter so captured
output matches expectations.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Final, Literal

# ──────────────────────────── colour map ────────────────────────────
RESET: Final[str] = "\x1b[0m"
LevelName = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
COLOR_MAP: Final[
    Mapping[Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], str]
] = {
    "DEBUG": "\x1b[36m",  # cyan
    "INFO": "\x1b[32m",  # green
    "WARNING": "\x1b[33m",  # yellow
    "ERROR": "\x1b[31m",  # red
    "CRITICAL": "\x1b[41m",  # red bg
}

# attribute used to mark handlers we own
_FLAG: Final[str] = "_rvp_internal"


def _is_testing() -> bool:
    """Check if we're currently running in a test environment."""
    import os
    import sys
    return (
        "PYTEST_CURRENT_TEST" in os.environ
        or "pytest" in sys.modules
        or any("test" in arg.lower() for arg in sys.argv)
    )


# ───────────────────────── public API ─────────────────────────


def init_logging(
    *,
    level: str = "INFO",
    color: bool = True,
    json_format: bool = False,
    json: bool = False,
    logfile: str | None = None,
) -> None:
    """
    Configure loguru as the main logger for the backend.

    Parameters
    ----------
    level : str
        Root log level.
    color : bool
        Enable ANSI colours for console output.
    json_format : bool
        Emit JSON lines instead of human format.
    logfile : Optional[str]
        Optional file to tee logs to.

    Raises
    ------
    OSError
        If logfile directory cannot be created.
    """
    import logging
    import sys
    from pathlib import Path
    from types import FrameType

    from loguru import logger as loguru_logger

    # Remove all existing loguru handlers safely
    try:
        loguru_logger.remove()
    except (ValueError, OSError):
        # Ignore errors during cleanup - handlers might already be removed
        pass

    # Console sink
    if json or json_format:
        loguru_logger.add(sys.stdout, level=level, serialize=True, colorize=False)
    else:
        loguru_logger.add(
            sys.stdout,
            level=level,
            colorize=color,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
        )

    # Optional file sink - but avoid file logging during tests to prevent handle issues
    if logfile is not None and not _is_testing():
        fp: Path = Path(logfile)
        fp.parent.mkdir(parents=True, exist_ok=True)
        loguru_logger.add(
            str(fp), level=level, serialize=(json or json_format), encoding="utf-8"
        )

    class InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            log_level: str
            try:
                log_level = loguru_logger.level(record.levelname).name
            except ValueError:
                log_level = str(
                    record.levelno
                )  # Ensure log_level is always str for mypy

            frame: FrameType | None = logging.currentframe()
            depth: int = 2
            while frame is not None and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            loguru_logger.opt(depth=depth, exception=record.exc_info).log(
                log_level, record.getMessage()
            )

    handler: InterceptHandler = InterceptHandler()
    logging.root.handlers = [handler]
    logging.root.setLevel(level)

    # Silence uvicorn access logs if needed
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.propagate = False

    # Migration note: Use `from loguru import logger` in all modules instead of `logging.getLogger()`
    # Example: logger.info("message")
