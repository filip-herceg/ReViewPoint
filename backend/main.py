from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from backend.core.config import settings
from backend.core.logging import init_logging
from backend.middlewares.logging import RequestLoggingMiddleware

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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
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
