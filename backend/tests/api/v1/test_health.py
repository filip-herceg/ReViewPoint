from typing import Any

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from src.main import app

pytestmark = pytest.mark.asyncio

transport = ASGITransport(app=app)


async def test_health_ok(monkeypatch: Any) -> None:
    async def ok_check() -> None:
        return None

    monkeypatch.setattr("src.core.events.db_healthcheck", ok_check)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/health")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "ok"


async def test_health_db_error(monkeypatch: Any) -> None:
    async def fail_check() -> None:
        raise RuntimeError("db error simulated")

    monkeypatch.setattr("src.api.v1.health.db_healthcheck", fail_check)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/health")
    assert resp.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    data = resp.json()
    assert data["status"] == "error"
    assert "db error simulated" in data["detail"]


# Advanced health and metrics tests (from test_health_advanced.py)
async def test_health_ok_fields(monkeypatch: Any) -> None:
    async def ok_check() -> None:
        return None

    monkeypatch.setattr("src.core.events.db_healthcheck", ok_check)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/health")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["status"] == "ok"
    assert "db" in data
    assert "pool" in data["db"]
    assert "uptime" in data
    assert "versions" in data
    assert "python" in data["versions"]
    assert "response_time" in data
    assert float(data["response_time"]) >= 0
    assert resp.headers["X-Health-Response-Time"]


async def test_health_db_error_fields(monkeypatch: Any) -> None:
    async def fail_check() -> None:
        raise RuntimeError("db error simulated")

    monkeypatch.setattr("src.api.v1.health.db_healthcheck", fail_check)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/health")
    assert resp.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    data = resp.json()
    assert data["status"] == "error"
    assert "db" in data
    assert data["db"]["ok"] is False
    assert "db error simulated" in data["db"]["error"]
    assert "pool" in data["db"]
    assert "uptime" in data
    assert "versions" in data
    assert "response_time" in data
    assert resp.headers["X-Health-Response-Time"]


async def test_metrics_endpoint() -> None:
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/metrics")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["content-type"].startswith("text/plain")
    body = resp.text
    assert "app_uptime_seconds" in body
    assert "db_pool_size" in body
    assert "db_pool_checkedin" in body
    assert "db_pool_checkedout" in body
    assert "db_pool_overflow" in body
    assert "db_pool_awaiting" in body


async def test_health_slow_db(monkeypatch: Any) -> None:
    import asyncio

    async def slow_check() -> None:
        await asyncio.sleep(0.1)

    monkeypatch.setattr("src.api.v1.health.db_healthcheck", slow_check)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/health")
    assert resp.status_code == status.HTTP_200_OK
    assert float(resp.json()["response_time"]) > 0.05


async def test_health_missing_pool_stats(monkeypatch: Any) -> None:
    from src.core import database

    orig_engine = database.engine

    class NoPool:
        pass

    database.engine = type("E", (), {"pool": None})()
    monkeypatch.setattr("src.core.database.engine", database.engine)

    async def ok_check() -> None:
        return None

    monkeypatch.setattr("src.core.events.db_healthcheck", ok_check)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/api/v1/health")
        assert resp.status_code == status.HTTP_200_OK
    finally:
        database.engine = orig_engine


async def test_metrics_missing_pool_stats(monkeypatch: Any) -> None:
    from src.core import database

    orig_engine = database.engine
    database.engine = type("E", (), {"pool": None})()
    monkeypatch.setattr("src.core.database.engine", database.engine)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/metrics")
    assert resp.status_code == status.HTTP_200_OK
    database.engine = orig_engine


async def test_health_missing_dependency_versions(monkeypatch: Any) -> None:
    import sys

    fastapi_orig = sys.modules.get("fastapi")
    sqlalchemy_orig = sys.modules.get("sqlalchemy")
    if "fastapi" in sys.modules:
        del sys.modules["fastapi"]
    if "sqlalchemy" in sys.modules:
        del sys.modules["sqlalchemy"]

    async def ok_check() -> None:
        return None

    monkeypatch.setattr("src.core.events.db_healthcheck", ok_check)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/api/v1/health")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["versions"]["fastapi"] is None
        assert data["versions"]["sqlalchemy"] is None
    finally:
        if fastapi_orig is not None:
            sys.modules["fastapi"] = fastapi_orig
        if sqlalchemy_orig is not None:
            sys.modules["sqlalchemy"] = sqlalchemy_orig
