from collections.abc import Callable
from typing import Any

from fastapi import HTTPException
from loguru import logger


def http_error(
    status_code: int,
    detail: str,
    logger_func: Callable[[str], None] = logger.error,
    extra: dict[str, Any] | None = None,
    exc: Exception | None = None,
) -> None:
    if extra:
        try:
            logger_func(detail, extra=extra)
        except TypeError:
            logger_func(f"{detail} | {extra}")
    else:
        logger_func(detail)
    raise HTTPException(status_code=status_code, detail=detail) from exc
