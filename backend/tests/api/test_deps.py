"""
Tests for src/api/deps.py (get_current_user dependency).
Covers all code paths, including edge and error cases.
"""

from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import deps
from src.core.config import settings
from src.models.user import User


@pytest.mark.asyncio
async def test_get_current_user_returns_dev_user_when_auth_disabled(
    monkeypatch: pytest.MonkeyPatch, async_session: AsyncSession
) -> None:
    monkeypatch.setattr(settings, "auth_enabled", False)
    user = await deps.get_current_user(token="irrelevant", session=async_session)
    assert isinstance(user, User)
    assert user.email == "dev@example.com"
    assert user.is_active
    monkeypatch.setattr(settings, "auth_enabled", True)


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(
    monkeypatch: pytest.MonkeyPatch, async_session: AsyncSession
) -> None:
    monkeypatch.setattr(settings, "auth_enabled", True)

    def fake_verify_access_token(token: str) -> dict[str, str]:
        return {}

    monkeypatch.setattr(deps, "verify_access_token", fake_verify_access_token)
    with pytest.raises(HTTPException) as exc:
        await deps.get_current_user(token="bad", session=async_session)
    assert exc.value.status_code == 401
    assert "Invalid token" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(
    monkeypatch: pytest.MonkeyPatch, async_session: AsyncSession
) -> None:
    monkeypatch.setattr(settings, "auth_enabled", True)

    def fake_verify_access_token(token: str) -> dict[str, int]:
        return {"sub": 123}

    monkeypatch.setattr(deps, "verify_access_token", fake_verify_access_token)
    monkeypatch.setattr(deps, "get_user_by_id", AsyncMock(return_value=None))
    with pytest.raises(HTTPException) as exc:
        await deps.get_current_user(token="token", session=async_session)
    assert exc.value.status_code == 401
    assert "User not found" in str(exc.value.detail)
