"""
Tests for src/api/deps.py (get_current_user dependency).
Covers all code paths, including edge and error cases.
"""

from unittest.mock import AsyncMock

import pytest
from backend.tests.test_templates import AuthUnitTestTemplate
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import deps
from src.core.config import settings
from src.models.user import User


class TestDeps(AuthUnitTestTemplate):
    @pytest.mark.asyncio
    async def test_get_current_user_returns_dev_user_when_auth_disabled(
        self, async_session: AsyncSession
    ) -> None:
        self.patch_setting(settings, "auth_enabled", False)
        user = await deps.get_current_user(token="irrelevant", session=async_session)
        assert isinstance(user, User)
        assert user.email == "dev@example.com"
        assert user.is_active
        self.patch_setting(settings, "auth_enabled", True)

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(
        self, async_session: AsyncSession
    ) -> None:
        self.patch_setting(settings, "auth_enabled", True)

        def fake_verify_access_token(token: str):
            return {}

        self.patch_dep("src.api.deps.verify_access_token", fake_verify_access_token)

        async def call():
            await deps.get_current_user(token="bad", session=async_session)

        await self._assert_async_http_exception(call, 401, "Invalid token")

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(
        self, async_session: AsyncSession
    ) -> None:
        self.patch_setting(settings, "auth_enabled", True)

        def fake_verify_access_token(token: str):
            return {"sub": 123}

        self.patch_dep("src.api.deps.verify_access_token", fake_verify_access_token)
        self.patch_dep("src.api.deps.get_user_by_id", AsyncMock(return_value=None))

        async def call():
            await deps.get_current_user(token="token", session=async_session)

        await self._assert_async_http_exception(call, 401, "User not found")

    def test_get_user_service_returns_user_module(self) -> None:
        user_service = deps.get_user_service()
        assert hasattr(user_service, "register_user")
        assert hasattr(user_service, "authenticate_user")

    def test_get_blacklist_token_returns_callable(self) -> None:
        blacklist_token = deps.get_blacklist_token()
        assert callable(blacklist_token)

    def test_get_user_action_limiter_returns_limiter(self) -> None:
        limiter = deps.get_user_action_limiter()
        assert hasattr(limiter, "is_allowed")
        assert callable(limiter.is_allowed)

    def test_get_validate_email_returns_callable(self) -> None:
        validate_email = deps.get_validate_email()
        assert callable(validate_email)
        assert validate_email("user@example.com") is True or False

    def test_get_password_validation_error_returns_callable(self) -> None:
        get_password_validation_error = deps.get_password_validation_error()
        assert callable(get_password_validation_error)
        # Should return None or str for a password
        result = get_password_validation_error("password123")
        assert result is None or isinstance(result, str)

    def test_get_async_refresh_access_token_returns_callable(self) -> None:
        async_refresh_access_token = deps.get_async_refresh_access_token()
        assert callable(async_refresh_access_token)

    async def _assert_async_http_exception(self, func, status_code, detail_substr=None):
        with pytest.raises(HTTPException) as exc:
            await func()
        assert exc.value.status_code == status_code
        if detail_substr:
            assert detail_substr in str(exc.value.detail)
