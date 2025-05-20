from fastapi import FastAPI

from core.config import settings
from core.logging import init_logging
from middlewares.logging import RequestLoggingMiddleware

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
