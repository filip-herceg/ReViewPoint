from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger

from src.api.v1.auth import router as auth_router
from src.api.v1.health import router as health_router
from src.core.config import settings
from src.core.events import on_shutdown, on_startup
from src.core.logging import init_logging
from src.middlewares.logging import RequestLoggingMiddleware


def create_app() -> FastAPI:
    app = FastAPI(
        title="ReViewPoint Core API",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )
    # Initialize logging system
    init_logging(level=settings.log_level)
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    # Register authentication router
    app.include_router(auth_router, prefix="/api/v1")
    # Register health check endpoint
    app.include_router(health_router, prefix="/api/v1")

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        if isinstance(exc, HTTPException):
            # Let FastAPI handle HTTPExceptions (like 404, 422, etc.)
            raise exc
        logger.exception(
            f"Unhandled exception for {request.method} {request.url.path}: {exc}"
        )
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "feedback": "An unexpected error occurred. Please try again later.",
            },
        )

    return app


app = create_app()

# Register event handlers
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)
