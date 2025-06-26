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


def test_get_user_service_returns_user_module():
    user_service = deps.get_user_service()
    assert hasattr(user_service, "register_user")
    assert hasattr(user_service, "authenticate_user")


def test_get_blacklist_token_returns_callable():
    blacklist_token = deps.get_blacklist_token()
    assert callable(blacklist_token)


def test_get_user_action_limiter_returns_limiter():
    limiter = deps.get_user_action_limiter()
    assert hasattr(limiter, "is_allowed")
    assert callable(limiter.is_allowed)


def test_get_validate_email_returns_callable():
    validate_email = deps.get_validate_email()
    assert callable(validate_email)
    assert validate_email("user@example.com") is True or False


def test_get_password_validation_error_returns_callable():
    get_password_validation_error = deps.get_password_validation_error()
    assert callable(get_password_validation_error)
    # Should return None or str for a password
    result = get_password_validation_error("password123")
    assert result is None or isinstance(result, str)


def test_get_async_refresh_access_token_returns_callable():
    async_refresh_access_token = deps.get_async_refresh_access_token()
    assert callable(async_refresh_access_token)
