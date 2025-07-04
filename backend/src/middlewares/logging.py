"""FastAPI middleware for HTTP request/response logging.

This middleware adds a unique request ID to each request and logs details about
requests and responses including timing information. It also attaches the
request ID to logs and response headers for correlation.

Example Usage:
    ```python
    from fastapi import FastAPI
    from middlewares.logging import RequestLoggingMiddleware

    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)
    ```
"""

import time
import uuid
from collections.abc import Awaitable, Callable, Sequence
from contextvars import ContextVar, Token
from typing import (
    Final,
    cast,
)

from fastapi import Request, Response
from loguru import Logger, logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Define sensitive fields as a module-level constant for clarity and efficiency
SENSITIVE_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "password",
        "token",
        "access_token",
        "refresh_token",
    }
)

# Thread-local request ID storage
request_id_var: Final[ContextVar[str | None]] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    """Get the current request ID from the context variable."""
    return request_id_var.get()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests with unique request IDs."""

    exclude_paths: Sequence[str]
    logger: Logger
    header_name: str

    def __init__(
        self,
        app: ASGIApp,
        *,
        exclude_paths: Sequence[str] | None = None,
        logger_instance: Logger | None = None,
        header_name: str = "X-Request-ID",
    ) -> None:
        """Initialize the middleware.

        Parameters
        ----------
        app : ASGIApp
            The ASGI application.
        exclude_paths : Sequence[str], optional
            List of paths to exclude from logging, by default None
        logger_instance : Logger, optional
            Custom logger to use, by default None (will use 'middleware.request')
        header_name : str, optional
            Name of the header to use for the request ID, by default "X-Request-ID"

        Raises
        ------
        Exception
            If logger_instance is not a Logger or None.
        """
        super().__init__(app)
        self.exclude_paths: Sequence[str] = (
            exclude_paths if exclude_paths is not None else ["/health", "/metrics"]
        )
        if logger_instance is not None:
            self.logger = logger_instance
        else:
            self.logger = cast(Logger, logger.bind(component="middleware.request"))
        self.header_name: str = header_name

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        Process a request and add logging and request ID tracking.

        Parameters
        ----------
        request : Request
            The incoming request
        call_next : Callable[[Request], Awaitable[Response]]
            The next middleware or route handler

        Returns
        -------
        Response
            The response with added X-Request-ID header

        Raises
        ------
        Exception
            Any exception raised during request processing is logged and re-raised.
        """
        # Skip excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Generate or extract request ID
        request_id: str = request.headers.get(self.header_name, str(uuid.uuid4()))
        # Set the request ID in the context variable for this request/response cycle
        token: Token = request_id_var.set(request_id)

        # Prepare request details for logging
        start_time: float = time.time()
        # Filter sensitive fields from query params
        filtered_query: list[tuple[str, str]] = [
            (k, "[FILTERED]") if k.lower() in SENSITIVE_FIELDS else (k, v)
            for k, v in request.query_params.multi_items()
        ]
        filtered_query_str: str = "&".join(f"{k}={v}" for k, v in filtered_query)
        log_extra: dict[str, str] = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": filtered_query_str,
        }

        self.logger.bind(**log_extra).info(
            f"Request {request.method} {request.url.path} | query: {filtered_query_str}"
        )
        try:
            # Process the request
            response: Response = await call_next(request)

            # Calculate request processing time
            process_time: float = time.time() - start_time
            process_time_ms: int = round(process_time * 1000)

            # Log the response
            self.logger.bind(
                **log_extra,
                status_code=response.status_code,
                process_time_ms=process_time_ms,
            ).info(
                f"Response {request.method} {request.url.path} completed with status {response.status_code} in {process_time_ms}ms | query: {filtered_query_str}"
            )

            # Attach request ID to response headers
            response.headers[self.header_name] = request_id
            return response

        except Exception as exc:
            # Log exceptions with request context
            process_time: float = time.time() - start_time
            process_time_ms: int = round(process_time * 1000)

            self.logger.bind(
                **log_extra,
                error=str(exc),
                process_time_ms=process_time_ms,
            ).exception(
                f"Error processing request {request.method} {request.url.path}: {exc}"
            )
            raise
        finally:
            # Reset the context variable
            request_id_var.reset(token)
