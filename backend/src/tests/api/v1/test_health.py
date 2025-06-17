from typing import Any

import pytest
from httpx import AsyncClient
from starlette.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.asyncio
async def test_health_success(monkeypatch: Any, async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_db_failure(monkeypatch: Any, async_client: AsyncClient) -> None:
    async def mock_get_db_status() -> dict[str, str]:
        return {"status": "down", "detail": "Database unavailable"}

    monkeypatch.setattr("app.dependencies.get_db_status", mock_get_db_status)
    response = await async_client.get("/health")
    assert response.status_code == HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["detail"] == "Database unavailable"


@pytest.mark.asyncio
async def test_health_timing(monkeypatch: Any, async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.status_code == HTTP_200_OK
    assert "duration" in response.json()


# Fix for assignment of None to module (lines 148, 149):
# If you have code like:
# some_module = None
# Replace with:
# del some_module
# Or restore the original module if monkeypatching.
