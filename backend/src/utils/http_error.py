from collections.abc import Callable

# TypedDict for extra logging info; extend with known keys for stricter typing
from typing import Final, Literal, TypedDict

from fastapi import HTTPException
from loguru import logger


class ExtraLogInfo(TypedDict, total=False):
    user_id: int
    request_id: str
    action: Literal["login", "logout", "create", "update", "delete"]
    error_code: int
    # Add more known keys and restrict values with Literal or stricter types as needed


DEFAULT_LOGGER_FUNC: Final[Callable[[str], None]] = logger.error  # type: ignore[assignment]


def http_error(
    status_code: int,
    detail: str,
    logger_func: Callable[[str], None] = DEFAULT_LOGGER_FUNC,
    extra: ExtraLogInfo | None = None,
    exc: BaseException | None = None,
) -> None:
    """
    Raises an HTTPException with logging.

    Args:
        status_code (int): HTTP status code to raise.
        detail (str): Error detail message.
        logger_func (Callable[[str], None]): Logging function to use.
        extra (Optional[Mapping[str, object]]): Additional log info.
        exc (Optional[Exception]): Exception to chain.

    Raises:
        HTTPException: Always raised with the given status and detail.
        TypeError: If logger_func signature is incompatible with extra.
    """
    if extra is not None:
        try:
            logger_func(detail, extra=extra)  # type: ignore[call-arg]  # loguru's logger accepts extra
        except TypeError:
            logger_func(f"{detail} | {extra}")
    else:
        logger_func(detail)
    raise HTTPException(status_code=status_code, detail=detail) from exc
