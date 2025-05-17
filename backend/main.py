from fastapi import FastAPI

from core.config import settings
from core.logging import init_logging

app = FastAPI(
    title="ReViewPoint Core API",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)


init_logging(level=settings.log_level)
