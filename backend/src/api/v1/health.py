import platform
import sys
import time
from typing import Any

from fastapi import APIRouter, Depends, Response, status

from src.api.deps import get_request_id, require_api_key, require_feature
from src.core.database import engine
from src.core.events import db_healthcheck

router = APIRouter(tags=["Health"])

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


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="""
    Returns the health status of the API and database connection, including uptime and dependency versions.

    **Features:**
    - Checks database connectivity
    - Returns API/server uptime
    - Returns dependency versions (Python, FastAPI, SQLAlchemy)
    - Adds response time in headers

    **Example:**
    ```bash
    curl https://api.reviewpoint.org/api/v1/health
    ```
    """,
    responses={
        200: {
            "description": "API and database are healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "db": {
                            "ok": True,
                            "error": None,
                        },
                        "uptime": 123.45,
                        "response_time": "0.0012s",
                        "versions": {
                            "python": "3.11.0",
                            "fastapi": "0.95.0",
                            "sqlalchemy": "2.0.0",
                        },
                    }
                }
            },
        },
        400: {
            "description": "Validation error.",
            "content": {
                "application/json": {"example": {"detail": "Invalid request."}}
            },
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated."}}
            },
        },
        403: {
            "description": "Forbidden. Not enough permissions.",
            "content": {
                "application/json": {"example": {"detail": "Not enough permissions."}}
            },
        },
        422: {
            "description": "Unprocessable Entity. Invalid input.",
            "content": {"application/json": {"example": {"detail": "Invalid input."}}},
        },
        429: {
            "description": "Too many requests.",
            "content": {
                "application/json": {"example": {"detail": "Rate limit exceeded."}}
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {"example": {"detail": "Unexpected error."}}
            },
        },
        503: {
            "description": "Database unavailable or service unavailable.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "db": {
                            "ok": False,
                            "error": "Database connection failed",
                            "pool": {},
                        },
                        "uptime": 12345.67,
                        "response_time": 0.0023,
                        "versions": {
                            "python": "3.11.8",
                            "fastapi": "0.110.0",
                            "sqlalchemy": "2.0.29",
                        },
                        "detail": "Database connection failed",
                    }
                }
            },
        },
    },
    openapi_extra={
        "x-codeSamples": [
            {
                "lang": "curl",
                "label": "cURL",
                "source": "curl https://api.reviewpoint.org/api/v1/health",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\nurl = 'https://api.reviewpoint.org/api/v1/health'\nresponse = requests.get(url)\nprint(response.json())",
            },
            {
                "lang": "JavaScript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://api.reviewpoint.org/api/v1/health')\n  .then(res => res.json())\n  .then(console.log);",
            },
            {
                "lang": "Go",
                "label": "Go (net/http)",
                "source": 'package main\nimport (\n  "net/http"\n)\nfunc main() {\n  http.Get("https://api.reviewpoint.org/api/v1/health")\n}',
            },
            {
                "lang": "Java",
                "label": "Java (OkHttp)",
                "source": 'OkHttpClient client = new OkHttpClient();\nRequest request = new Request.Builder()\n  .url("https://api.reviewpoint.org/api/v1/health")\n  .get()\n  .build();\nResponse response = client.newCall(request).execute();',
            },
            {
                "lang": "PHP",
                "label": "PHP (cURL)",
                "source": "$ch = curl_init('https://api.reviewpoint.org/api/v1/health');\n$response = curl_exec($ch);\ncurl_close($ch);",
            },
            {
                "lang": "Ruby",
                "label": "Ruby (Net::HTTP)",
                "source": "require 'net/http'\nuri = URI('https://api.reviewpoint.org/api/v1/health')\nres = Net::HTTP.get(uri)\nputs res",
            },
            {
                "lang": "HTTPie",
                "label": "HTTPie",
                "source": "http GET https://api.reviewpoint.org/api/v1/health",
            },
            {
                "lang": "PowerShell",
                "label": "PowerShell",
                "source": "Invoke-RestMethod -Uri 'https://api.reviewpoint.org/api/v1/health' -Method Get",
            },
        ]
    },
)
async def health_check(
    response: Response,
    request_id: str = Depends(get_request_id),
    feature_flag_ok: bool = Depends(require_feature("health:read")),
    _api_key: None = Depends(require_api_key),
) -> dict[str, Any]:
    """
    Returns API and database health status.
    - **response**: FastAPI response object (for headers)
    - **request_id**: Request ID for tracing
    - **feature_flag_ok**: Feature flag enforcement for health endpoint
    Returns a dict with status, db, uptime, response_time, and versions.
    """
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


@router.get(
    "/metrics",
    status_code=status.HTTP_200_OK,
    summary="Prometheus metrics",
    description="""
    Returns Prometheus-style metrics for uptime and database connection pool.

    **Metrics Provided:**
    - `app_uptime_seconds`: API uptime in seconds
    - `db_pool_size`: Database connection pool size
    - `db_pool_checkedin`: Idle connections
    - `db_pool_checkedout`: Active connections
    - `db_pool_overflow`: Overflow connections
    - `db_pool_awaiting`: Awaiting connections

    **Use case:**
    - Monitoring with Prometheus or similar tools
    - Health dashboards
    """,
    responses={
        200: {
            "description": "Prometheus metrics in plain text",
            "content": {
                "text/plain": {
                    "example": "app_uptime_seconds 12345.67\ndb_pool_size 5\ndb_pool_checkedin 5\ndb_pool_checkedout 0\ndb_pool_overflow 0\ndb_pool_awaiting 0"
                }
            },
        },
        400: {
            "description": "Validation error.",
            "content": {
                "application/json": {"example": {"detail": "Invalid request."}}
            },
        },
        401: {
            "description": "Unauthorized. Missing or invalid authentication.",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated."}}
            },
        },
        403: {
            "description": "Forbidden. Not enough permissions.",
            "content": {
                "application/json": {"example": {"detail": "Not enough permissions."}}
            },
        },
        422: {
            "description": "Unprocessable Entity. Invalid input.",
            "content": {"application/json": {"example": {"detail": "Invalid input."}}},
        },
        429: {
            "description": "Too many requests.",
            "content": {
                "application/json": {"example": {"detail": "Rate limit exceeded."}}
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {"example": {"detail": "Unexpected error."}}
            },
        },
        503: {
            "description": "Service unavailable.",
            "content": {
                "application/json": {
                    "example": {"detail": "Service temporarily unavailable."}
                }
            },
        },
    },
    openapi_extra={
        "x-codeSamples": [
            {
                "lang": "curl",
                "label": "cURL",
                "source": "curl https://api.reviewpoint.org/api/v1/metrics",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\nurl = 'https://api.reviewpoint.org/api/v1/metrics'\nresponse = requests.get(url)\nprint(response.text)",
            },
            {
                "lang": "JavaScript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://api.reviewpoint.org/api/v1/metrics')\n  .then(res => res.text())\n  .then(console.log);",
            },
            {
                "lang": "Go",
                "label": "Go (net/http)",
                "source": 'package main\nimport (\n  "net/http"\n)\nfunc main() {\n  http.Get("https://api.reviewpoint.org/api/v1/metrics")\n}',
            },
            {
                "lang": "Java",
                "label": "Java (OkHttp)",
                "source": 'OkHttpClient client = new OkHttpClient();\nRequest request = new Request.Builder()\n  .url("https://api.reviewpoint.org/api/v1/metrics")\n  .get()\n  .build();\nResponse response = client.newCall(request).execute();',
            },
            {
                "lang": "PHP",
                "label": "PHP (cURL)",
                "source": "$ch = curl_init('https://api.reviewpoint.org/api/v1/metrics');\n$response = curl_exec($ch);\ncurl_close($ch);",
            },
            {
                "lang": "Ruby",
                "label": "Ruby (Net::HTTP)",
                "source": "require 'net/http'\nuri = URI('https://api.reviewpoint.org/api/v1/metrics')\nres = Net::HTTP.get(uri)\nputs res",
            },
            {
                "lang": "HTTPie",
                "label": "HTTPie",
                "source": "http GET https://api.reviewpoint.org/api/v1/metrics",
            },
            {
                "lang": "PowerShell",
                "label": "PowerShell",
                "source": "Invoke-RestMethod -Uri 'https://api.reviewpoint.org/api/v1/metrics' -Method Get",
            },
        ]
    },
)
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
