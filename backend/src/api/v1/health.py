import platform
import sys
import time
from typing import Any

from fastapi import APIRouter, Response, status

from src.core.database import engine
from src.core.events import db_healthcheck

router = APIRouter()

APP_START_TIME = time.time()


def get_pool_stats() -> dict[str, Any]:
    stats: dict[str, Any] = {}
    pool = getattr(engine, "pool", None)
    if pool:
        for attr in ["size", "checkedin", "checkedout", "overflow", "awaiting"]:
            val = getattr(pool, attr, None)
            if callable(val):
                try:
                    stats[attr] = val()
                except Exception:
                    stats[attr] = None
            else:
                stats[attr] = val
    return stats


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(response: Response) -> dict[str, Any]:
    start = time.monotonic()
    db_ok = True
    db_error: str | None = None
    try:
        await db_healthcheck()
    except Exception as exc:
        db_ok = False
        db_error = str(exc)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    duration = time.monotonic() - start
    response.headers["X-Health-Response-Time"] = f"{duration:.4f}s"
    uptime = time.time() - APP_START_TIME
    pool_stats = get_pool_stats()
    # Check dependency versions at runtime for monkeypatching compatibility
    fastapi_mod = sys.modules.get("fastapi")
    sqlalchemy_mod = sys.modules.get("sqlalchemy")
    versions = {
        "python": platform.python_version(),
        "fastapi": getattr(fastapi_mod, "__version__", None) if fastapi_mod else None,
        "sqlalchemy": (
            getattr(sqlalchemy_mod, "__version__", None) if sqlalchemy_mod else None
        ),
    }
    health: dict[str, Any] = {
        "status": "ok" if db_ok else "error",
        "db": {"ok": db_ok, "error": db_error, "pool": pool_stats},
        "uptime": uptime,
        "response_time": duration,
        "versions": versions,
    }
    if not db_ok:
        health["detail"] = db_error
    return health


@router.get("/metrics", status_code=status.HTTP_200_OK)
def metrics() -> Response:
    pool_stats = get_pool_stats()
    uptime = time.time() - APP_START_TIME
    lines = [
        f"app_uptime_seconds {uptime}",
        f"db_pool_size {pool_stats.get('size', 0)}",
        f"db_pool_checkedin {pool_stats.get('checkedin', 0)}",
        f"db_pool_checkedout {pool_stats.get('checkedout', 0)}",
        f"db_pool_overflow {pool_stats.get('overflow', 0)}",
        f"db_pool_awaiting {pool_stats.get('awaiting', 0)}",
    ]
    return Response("\n".join(lines), media_type="text/plain")
