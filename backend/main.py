from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from services.logger import init_logger, log
from middlewares.logging import LoggingMiddleware
from config import settings
from api.routes import router as api_router

app = FastAPI(
    title="ReViewPoint Core API",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

init_logger(env=settings.env)
log.info("🚀 ReViewPoint API server starting...")

# Middleware aktivieren
app.add_middleware(LoggingMiddleware)

# Router registrieren
app.include_router(api_router)


# Startup-/Shutdown-Events
@app.on_event("startup")
async def on_startup():
    log.info("🔧 Startup event triggered")


@app.on_event("shutdown")
async def on_shutdown():
    log.info("🧹 Shutdown event triggered")


# Exception-Handling
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.exception(f"💥 Unhandled exception at {request.url.path}")
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    log.warning(f"⚠️ Validation failed at {request.url.path}: {exc}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


# Healthcheck
@app.get("/health", tags=["meta"])
def healthcheck():
    log.debug("🔍 Healthcheck endpoint called")
    return {"status": "ok", "environment": settings.env}
