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

from __future__ import annotations

import time
import uuid
from contextvars import ContextVar
from typing import Any

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

# Thread-local request ID storage
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    """Get the current request ID from the context variable."""
    return request_id_var.get()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests with unique request IDs."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        exclude_paths: list[str] | None = None,
        logger_instance: Any = None,
        header_name: str = "X-Request-ID",
    ) -> None:
        """Initialize the middleware.

        Parameters
        ----------
        app : ASGIApp
            The ASGI application.
        exclude_paths : list[str], optional
            List of paths to exclude from logging, by default None
        logger_instance : loguru.Logger, optional
            Custom logger to use, by default None (will use 'middleware.request')
        header_name : str, optional
            Name of the header to use for the request ID, by default "X-Request-ID"
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]
        self.logger: Any = (
            logger_instance
            if logger_instance is not None
            else logger.bind(component="middleware.request")
        )
        self.header_name = header_name

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process a request and add logging and request ID tracking.

        Parameters
        ----------
        request : Request
            The incoming request
        call_next : RequestResponseEndpoint
            The next middleware or route handler

        Returns
        -------
        Response
            The response with added X-Request-ID header
        """
        # Skip excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Generate or extract request ID
        request_id = request.headers.get(self.header_name, str(uuid.uuid4()))
        # Set the request ID in the context variable for this request/response cycle
        token = request_id_var.set(request_id)

        # Prepare request details for logging
        start_time = time.time()
        log_extra = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params),
        }

        self.logger.bind(**log_extra).info(
            f"Request {request.method} {request.url.path}"
        )
        try:
            # Process the request
            response = await call_next(request)

            # Calculate request processing time
            process_time = time.time() - start_time
            process_time_ms = round(process_time * 1000)

            # Log the response
            self.logger.bind(
                **log_extra,
                status_code=response.status_code,
                process_time_ms=process_time_ms,
            ).info(
                f"Response {request.method} {request.url.path} "
                f"completed with status {response.status_code} "
                f"in {process_time_ms}ms"
            )

            # Attach request ID to response headers
            response.headers[self.header_name] = request_id
            return response

        except Exception as exc:
            # Log exceptions with request context
            process_time = time.time() - start_time
            process_time_ms = round(process_time * 1000)

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
