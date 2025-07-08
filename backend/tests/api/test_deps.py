from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Final, Callable as TypingCallable, Awaitable as TypingAwaitable
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.user import UserService
from src.utils.rate_limit import AsyncRateLimiter
from tests.test_templates import AuthUnitTestTemplate


class TestGetCurrentUser(AuthUnitTestTemplate):
    @pytest.mark.asyncio
    async def test_get_current_user_returns_dev_user_when_auth_disabled(
        self, async_session: AsyncSession
    ) -> None:
        """
        Test that get_current_user returns the dev user when auth is disabled.
        Verifies:
            - User is instance of User
            - Email is 'dev@example.com'
            - User is active
        """
        from src.api import deps
        from src.core.config import get_settings

        settings = get_settings()
        self.patch_setting(settings, "auth_enabled", False)
        user_result = await deps.get_current_user(token="irrelevant", session=async_session)
        assert isinstance(user_result, User)
        user: Final[User] = user_result
        assert user.email == "dev@example.com"
        assert user.is_active
        self.patch_setting(settings, "auth_enabled", True)

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(
        self, async_session: AsyncSession
    ) -> None:
        """
        Test that get_current_user raises HTTPException for invalid token.
        Expects:
            - HTTP 401 with 'Invalid token' message
        """
        from src.api import deps
        from src.core.config import get_settings

        settings = get_settings()
        self.patch_setting(settings, "auth_enabled", True)

        def fake_verify_access_token(token: str) -> dict[str, object]:
            return {}

        self.patch_dep("src.api.deps.verify_access_token", fake_verify_access_token)

        async def call() -> None:
            await deps.get_current_user(token="bad", session=async_session)

        await self.assert_async_http_exception(call, 401, "Invalid token")

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(
        self, async_session: AsyncSession
    ) -> None:
        """
        Test that get_current_user raises HTTPException when user is not found.
        Expects:
            - HTTP 401 with 'User not found' message
        """
        from src.api import deps
        from src.core.config import get_settings

        settings = get_settings()
        self.patch_setting(settings, "auth_enabled", True)

        def fake_verify_access_token(token: str) -> dict[str, object]:
            return {"sub": 123}

        self.patch_dep("src.api.deps.verify_access_token", fake_verify_access_token)
        self.patch_dep("src.api.deps.get_user_by_id", AsyncMock(return_value=None))

        async def call() -> None:
            await deps.get_current_user(token="token", session=async_session)

        await self.assert_async_http_exception(call, 401, "User not found")

    def test_get_user_service_returns_user_module(self) -> None:
        """
        Test that get_user_service returns a UserService instance with required methods.
        """
        from src.api import deps

        user_service: Final[UserService] = deps.get_user_service()
        assert hasattr(user_service, "register_user")
        assert hasattr(user_service, "authenticate_user")

    def test_get_blacklist_token_returns_callable(self) -> None:
        """
        Test that get_blacklist_token returns a callable Awaitable.
        """
        from src.api import deps

        blacklist_token: TypingCallable[..., TypingAwaitable[None]] = deps.get_blacklist_token()
        assert callable(blacklist_token)

    def test_get_user_action_limiter_returns_limiter(self) -> None:
        """
        Test that get_user_action_limiter returns a callable.
        """
        from src.api import deps
        from collections.abc import Awaitable, Callable

        limiter: Callable[..., Awaitable[None]] = deps.get_user_action_limiter()
        assert callable(limiter)

    def test_get_validate_email_returns_callable(self) -> None:
        """
        Test that get_validate_email returns a callable that validates emails.
        """
        from src.api import deps

        validate_email: TypingCallable[[str], bool] = deps.get_validate_email()
        assert callable(validate_email)
        result: bool = validate_email("user@example.com")
        assert isinstance(result, bool)

    def test_get_password_validation_error_returns_callable(self) -> None:
        """
        Test that get_password_validation_error returns a callable that returns str or None.
        """
        from src.api import deps

        get_password_validation_error: TypingCallable[[str], str | None] = deps.get_password_validation_error()
        assert callable(get_password_validation_error)
        result: str | None = get_password_validation_error("password123")
        assert result is None or isinstance(result, str)

    def test_get_async_refresh_access_token_returns_callable(self) -> None:
        """
        Test that get_async_refresh_access_token returns a callable Awaitable.
        """
        from src.api import deps

        async_refresh_access_token: TypingCallable[[AsyncSession, str], TypingAwaitable[object]] = deps.get_async_refresh_access_token()
        assert callable(async_refresh_access_token)
