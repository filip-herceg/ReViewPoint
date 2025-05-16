from fastapi import FastAPI
from services.logger import init_logger, log
from config import settings
from api.routes import router as api_router

app = FastAPI(
    title="ReViewPoint Core API",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

init_logger()
log.info("🚀 ReViewPoint API server starting...")

app.include_router(api_router)


@app.get("/health", tags=["meta"])
def healthcheck():
    log.debug("🔍 Healthcheck endpoint called")
    return {"status": "ok", "environment": settings.env}
