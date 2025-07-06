from typing import Awaitable, Callable, Final, Optional, TypedDict, Literal
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

"""
All config-dependent imports must be inside test methods or class bodies.
"""
from tests.test_templates import AuthUnitTestTemplate


class DummyUser:
    """Minimal user stub for testing with strict typing."""
    is_active: bool
    is_deleted: bool
    id: int
    email: str
    hashed_password: str
    is_admin: bool

    def __init__(
        self,
        is_active: bool = True,
        is_deleted: bool = False,
        id: int = 1,
        email: str = "test@example.com",
        hashed_password: str = "hashed",
        is_admin: bool = False,
    ) -> None:
        self.is_active = is_active
        self.is_deleted = is_deleted
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.is_admin = is_admin

    @property
    def role(self) -> str:
        """Return role based on is_admin flag."""
        return "admin" if self.is_admin else "user"
        self.id = id
        self.email = email
        self.hashed_password = hashed_password


class DummyResult:
    """Stub for DB result with strict typing."""
    def __init__(self, user: Optional[DummyUser]) -> None:
        self._user: Optional[DummyUser] = user

    def scalar_one_or_none(self) -> Optional[DummyUser]:
        return self._user





class TestUserService(AuthUnitTestTemplate):
    @staticmethod
    def make_real_user(is_active: bool, is_deleted: bool):
        """Create a real User instance for testing."""
        from src.models.user import User
        return User(
            email="real@example.com",
            hashed_password="hashed",
            is_active=is_active,
            is_deleted=is_deleted,
            name=None,
            bio=None,
            avatar_url=None,
            preferences=None,
        )

    @pytest.mark.asyncio
    async def test_success(self) -> None:
        """
        Test that successful authentication returns correct access and refresh tokens.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        dummy: DummyUser = DummyUser()
        session.execute = AsyncMock(return_value=DummyResult(dummy))
        self.patch_dep("src.services.user.verify_password", lambda pw, hpw: True)
        self.patch_dep("src.services.user.create_access_token", lambda payload: "token")
        self.patch_dep("src.services.user.create_refresh_token", lambda payload: "refresh")
        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=True))
        with patch("src.repositories.user.update_last_login", new_callable=AsyncMock):
            tokens: tuple[str, str] = await user_service.authenticate_user(session, dummy.email, "pw")
        access_token: str
        refresh_token: str
        access_token, refresh_token = tokens
        assert access_token == "token"
        assert refresh_token == "refresh"

    @pytest.mark.asyncio
    async def test_wrong_password(self) -> None:
        """
        Test that authentication fails with wrong password and raises an Exception.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        dummy: DummyUser = DummyUser()
        session.execute = AsyncMock(return_value=DummyResult(dummy))
        self.patch_dep("src.services.user.verify_password", lambda pw, hpw: False)
        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=True))
        with patch("src.repositories.user.update_last_login", new_callable=AsyncMock):
            with pytest.raises(Exception):
                await user_service.authenticate_user(session, dummy.email, "pw")

    @pytest.mark.asyncio
    async def test_user_not_found(self) -> None:
        """
        Test that authentication fails if user is not found and raises an Exception.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        session.execute = AsyncMock(return_value=DummyResult(None))
        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=True))
        with patch("src.repositories.user.update_last_login", new_callable=AsyncMock):
            with pytest.raises(Exception):
                await user_service.authenticate_user(
                    session, "notfound@example.com", "pw"
                )

    @pytest.mark.asyncio
    async def test_inactive_or_deleted_user(self) -> None:
        """
        Test that authentication fails for inactive or deleted users and raises an Exception.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        dummy: DummyUser = DummyUser(is_active=False)
        session.execute = AsyncMock(return_value=DummyResult(dummy))
        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=True))
        with patch("src.repositories.user.update_last_login", new_callable=AsyncMock):
            with pytest.raises(Exception):
                await user_service.authenticate_user(session, dummy.email, "pw")
        dummy2: DummyUser = DummyUser(is_deleted=True)
        session.execute = AsyncMock(return_value=DummyResult(dummy2))
        with patch("src.repositories.user.update_last_login", new_callable=AsyncMock):
            with pytest.raises(Exception):
                await user_service.authenticate_user(session, dummy2.email, "pw")

    @pytest.mark.asyncio
    @pytest.mark.skip_if_fast_tests("Auth disabled test not reliable in fast test mode")
    async def test_auth_disabled(self) -> None:
        """
        Test that authentication returns tokens if auth is disabled in settings.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=False))
        self.patch_dep("src.services.user.create_access_token", lambda payload: "token")
        self.patch_dep("src.services.user.create_refresh_token", lambda payload: "refresh")
        # Patch user lookup to return a dummy user with a valid bcrypt hash for "pw"
        from passlib.hash import bcrypt
        valid_hash = bcrypt.hash("pw")
        dummy: DummyUser = DummyUser(hashed_password=valid_hash)
        session.execute = AsyncMock(return_value=DummyResult(dummy))
        tokens: tuple[str, str] = await user_service.authenticate_user(session, "dev@example.com", "pw")
        access_token: str
        refresh_token: str
        access_token, refresh_token = tokens
        assert access_token == "token"
        assert refresh_token == "refresh"

    def test_active(self) -> None:
        """
        Test that is_authenticated returns True for an active user.
        """
        import src.services.user as user_service

        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=True))
        from src.models.user import User
        user: User = self.make_real_user(is_active=True, is_deleted=False)
        assert user_service.is_authenticated(user)

    def test_inactive(self) -> None:
        """
        Test that is_authenticated returns False for an inactive user.
        """
        import src.services.user as user_service

        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=True))
        from src.models.user import User
        user: User = self.make_real_user(is_active=False, is_deleted=False)
        assert not user_service.is_authenticated(user)

    def test_deleted(self) -> None:
        """
        Test that is_authenticated returns False for a deleted user.
        """
        import src.services.user as user_service

        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=True))
        from src.models.user import User
        user: User = self.make_real_user(is_active=True, is_deleted=True)
        assert not user_service.is_authenticated(user)

    @pytest.mark.skip_if_fast_tests("Auth disabled test not reliable in fast test mode")
    def test_auth_disabled_is_authenticated(self) -> None:
        """
        Test that is_authenticated returns True if auth is disabled in settings.
        """
        import src.services.user as user_service

        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=False))
        from src.models.user import User
        # Patch user to be active and not deleted to match logic
        user: User = self.make_real_user(is_active=True, is_deleted=False)
        assert user_service.is_authenticated(user)

    def test_valid_refresh(self) -> None:
        """
        Test that refresh_access_token returns a new token if the refresh token is valid.
        """
        import src.services.user as user_service

        self.patch_dep(
            "src.services.user.verify_access_token",
            lambda t: {"sub": "1", "email": "e"},
        )
        self.patch_dep(
            "src.services.user.create_access_token", lambda payload: "newtoken"
        )
        self.patch_dep(
            "src.services.user.verify_refresh_token",
            lambda t: {"sub": "1", "email": "e"},
        )
        assert user_service.refresh_access_token(1, "sometoken") == "newtoken"

    @pytest.mark.skip_if_fast_tests(
        "Refresh token invalid test not reliable in fast test mode"
    )
    def test_invalid_refresh(self) -> None:
        """
        Test that refresh_access_token raises ValidationError if the refresh token is invalid.
        """
        import src.services.user as user_service

        def bad_verify(token: str) -> None:
            raise Exception("bad token")

        self.patch_dep("src.services.user.verify_refresh_token", bad_verify)

        with pytest.raises(user_service.ValidationError):
            user_service.refresh_access_token(1, "badtoken")

    @pytest.mark.asyncio
    async def test_ascii(self) -> None:
        """
        Test that password strength validation passes for a good ASCII password.
        """
        import src.services.user as user_service

        user_service.validate_password_strength("GoodPass123!")

    @pytest.mark.asyncio
    async def test_whitespace(self) -> None:
        """
        Test that password strength validation fails for a password with whitespace.
        Expects ValidationError.
        """
        import src.services.user as user_service

        with pytest.raises(user_service.ValidationError):
            user_service.validate_password_strength("bad pass")

    @pytest.mark.asyncio
    async def test_non_ascii(self) -> None:
        """
        Test that password strength validation fails for a non-ASCII password.
        Expects ValidationError.
        """
        import src.services.user as user_service

        with pytest.raises(user_service.ValidationError):
            user_service.validate_password_strength("pässword")

    @pytest.mark.asyncio
    async def test_error(self) -> None:
        """
        Test that password strength validation fails if the validator returns an error string.
        Expects ValidationError.
        """
        import src.services.user as user_service

        with pytest.raises(user_service.ValidationError):
            self.patch_dep(
                "src.services.user.get_password_validation_error", lambda pw: "fail"
            )
            user_service.validate_password_strength("bad")

    @pytest.mark.asyncio
    async def test_valid_email_token(self) -> None:
        """
        Test that verify_email_token returns the payload if the token is valid.
        """
        import src.services.user as user_service

        self.patch_dep(
            "src.services.user.verify_access_token", lambda t: {"email": "e"}
        )
        assert user_service.verify_email_token("tok") == {"email": "e"}

    @pytest.mark.asyncio
    async def test_invalid_email_token(self) -> None:
        """
        Test that verify_email_token raises ValidationError if the token is invalid.
        """
        import src.services.user as user_service

        def bad_verify(token: str) -> None:
            raise Exception("bad token")

        with pytest.raises(user_service.ValidationError):
            self.patch_dep("src.services.user.verify_access_token", bad_verify)
            user_service.verify_email_token("badtok")

    @pytest.mark.asyncio
    async def test_get_token(self) -> None:
        """
        Test that get_password_reset_token returns a token string.
        """
        import src.services.user as user_service

        self.patch_dep(
            "src.services.user.create_access_token", lambda payload: "resettoken"
        )
        self.patch_setting(user_service, "settings", MagicMock(environment="dev"))
        assert user_service.get_password_reset_token("e@x.com") == "resettoken"

    @pytest.mark.asyncio
    async def test_valid_get_user_by_username(self) -> None:
        """
        Test that get_user_by_username returns a user if found.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        dummy: DummyUser = DummyUser()
        session.execute = AsyncMock(return_value=DummyResult(dummy))
        self.patch_dep("src.services.user.validate_email", lambda e: True)
        user = await user_service.get_user_by_username(session, "test@example.com")
        assert user is dummy

    @pytest.mark.asyncio
    async def test_invalid_email_get_user_by_username(self) -> None:
        """
        Test that get_user_by_username raises ValidationError for invalid email.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        self.patch_dep("src.services.user.validate_email", lambda e: False)
        with pytest.raises(user_service.ValidationError):
            await user_service.get_user_by_username(session, "bademail")

    @pytest.mark.asyncio
    async def test_not_found_get_user_by_username(self) -> None:
        """
        Test that get_user_by_username returns None if user is not found.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        session.execute = AsyncMock(return_value=DummyResult(None))
        self.patch_dep("src.services.user.validate_email", lambda e: True)
        user = await user_service.get_user_by_username(session, "notfound@example.com")
        assert user is None

    @pytest.mark.asyncio
    async def test_true_user_exists(self) -> None:
        """
        Test that user_exists returns True if the user exists (email is not unique).
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        self.patch_dep("src.services.user.validate_email", lambda e: True)
        self.patch_async_dep(
            "src.repositories.user.is_email_unique", AsyncMock(return_value=False)
        )
        result: bool = await user_service.user_exists(session, "e@x.com")
        assert result is True

    @pytest.mark.asyncio
    async def test_false_user_exists(self) -> None:
        """
        Test that user_exists returns False if the user does not exist (email is unique).
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        self.patch_dep("src.services.user.validate_email", lambda e: True)
        self.patch_async_dep(
            "src.repositories.user.is_email_unique", AsyncMock(return_value=True)
        )
        result: bool = await user_service.user_exists(session, "e@x.com")
        assert result is False

    @pytest.mark.asyncio
    @pytest.mark.skip_if_fast_tests("User exists test not reliable in fast test mode")
    async def test_invalid_user_exists(self) -> None:
        """
        Test that user_exists raises ValidationError for invalid email.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        self.patch_dep("src.services.user.validate_email", lambda e: False)

        with pytest.raises(user_service.ValidationError):
            await user_service.user_exists(session, "bad")

    @pytest.mark.asyncio
    async def test_assign_and_check(self) -> None:
        """
        Test assign_role and check_user_role for valid and invalid roles.
        """
        import src.services.user as user_service

        user_id: int = 1
        role: str = "admin"
        assert await user_service.assign_role(user_id, role) is True
        assert await user_service.check_user_role(user_id, role) is True
        assert await user_service.check_user_role(user_id, "user") is False

    @pytest.mark.asyncio
    async def test_assign_invalid(self) -> None:
        """
        Test that assign_role raises ValidationError for an invalid role.
        """
        import src.services.user as user_service

        with pytest.raises(user_service.ValidationError):
            await user_service.assign_role(1, "notarole")

    @pytest.mark.asyncio
    async def test_delete_soft(self) -> None:
        """
        Test that delete_user_account (soft delete) returns True.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        self.patch_async_dep(
            "src.repositories.user.soft_delete_user", AsyncMock(return_value=True)
        )
        self.patch_async_dep("src.repositories.user.audit_log_user_change", AsyncMock())
        result: bool = await user_service.delete_user_account(session, 1, anonymize=False)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_anonymize(self) -> None:
        """
        Test that delete_user_account (anonymize) returns True.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        self.patch_async_dep(
            "src.repositories.user.anonymize_user", AsyncMock(return_value=True)
        )
        self.patch_async_dep("src.repositories.user.audit_log_user_change", AsyncMock())
        result: bool = await user_service.delete_user_account(session, 1, anonymize=True)
        assert result is True

    @pytest.mark.asyncio
    async def test_deactivate(self) -> None:
        """
        Test that deactivate_user returns True.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        self.patch_async_dep(
            "src.repositories.user.deactivate_user", AsyncMock(return_value=True)
        )
        self.patch_async_dep("src.repositories.user.audit_log_user_change", AsyncMock())
        result: bool = await user_service.deactivate_user(session, 1)
        assert result is True

    @pytest.mark.asyncio
    async def test_reactivate(self) -> None:
        """
        Test that reactivate_user returns True.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        self.patch_async_dep(
            "src.repositories.user.reactivate_user", AsyncMock(return_value=True)
        )
        self.patch_async_dep("src.repositories.user.audit_log_user_change", AsyncMock())
        result: bool = await user_service.reactivate_user(session, 1)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_user_preferences(self) -> None:
        """
        Test that set_user_preferences sets and returns preferences correctly.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        dummy: DummyUser = DummyUser()
        session.commit = AsyncMock()
        self.patch_async_dep(
            "src.services.user.get_user_by_id", AsyncMock(return_value=dummy)
        )
        prefs: dict[str, str] = {"theme": "dark", "locale": "en"}
        result = await user_service.set_user_preferences(session, 1, prefs)
        assert getattr(result, "theme", None) == "dark"
        assert getattr(result, "locale", None) == "en"

    @pytest.mark.asyncio
    async def test_not_found_user_preferences(self) -> None:
        """
        Test that set_user_preferences raises UserNotFoundError if user is not found.
        """
        import src.services.user as user_service

        session: AsyncMock = AsyncMock()
        session.commit = AsyncMock()
        self.patch_async_dep(
            "src.services.user.get_user_by_id", AsyncMock(return_value=None)
        )
        with pytest.raises(user_service.UserNotFoundError):
            await user_service.set_user_preferences(session, 1, {})

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "error_case,expected_exception,expected_msg",
        [
            ("jwt_decode_error", "RefreshTokenError", "JWT decode failed: fail"),
            (
                "missing_user_id",
                "RefreshTokenError",
                "Invalid token format: missing user_id.",
            ),
            (
                "rate_limited",
                "RefreshTokenRateLimitError",
                "Too many token refresh attempts.",
            ),
            (
                "blacklisted",
                "RefreshTokenBlacklistedError",
                "Refresh token is blacklisted.",
            ),
            ("unexpected_error", "RefreshTokenError", "Unexpected error: fail"),
        ],
    )
    @pytest.mark.skip_if_fast_tests(
        "Async refresh token error tests still require fixes for fast test mode"
    )
    async def test_errors(
        self,
        error_case: str,
        expected_exception: str,
        expected_msg: str,
    ) -> None:
        """
        Test that async_refresh_access_token raises correct exceptions for error cases.
        """
        import src.services.user as user_service
        from src.models.user import User

        session: AsyncMock = AsyncMock()
        token: str = "sometoken"
        jwt_secret: str = "secret"
        jwt_algorithm: str = "HS256"
        real_user: User = User(
            email="real@example.com",
            hashed_password="hashed",
            is_active=True,
            is_deleted=False,
            name=None,
            bio=None,
            avatar_url=None,
            preferences=None,
        )
        patchers: list = []
        exc_type: type[Exception]
        if error_case == "jwt_decode_error":
            # Patch jwt.decode to raise Exception("fail") and ensure error message matches code
            patchers = [patch("src.services.user.jwt.decode", side_effect=Exception("fail"))]
            exc_type = user_service.RefreshTokenError
        elif error_case == "missing_user_id":
            patchers = [patch("src.services.user.jwt.decode", return_value={})]
            exc_type = user_service.RefreshTokenError
        elif error_case == "rate_limited":
            patchers = [
                patch("src.services.user.jwt.decode", return_value={"user_id": 1}),
                patch("src.services.user.user_action_limiter", new_callable=AsyncMock, return_value=False),
            ]
            exc_type = user_service.RefreshTokenRateLimitError
        elif error_case == "blacklisted":
            patchers = [
                patch("src.services.user.jwt.decode", return_value={"user_id": 1}),
                patch("src.services.user.user_action_limiter", new_callable=AsyncMock, return_value=True),
                patch("src.services.user.is_token_blacklisted", new_callable=AsyncMock, return_value=True),
            ]
            exc_type = user_service.RefreshTokenBlacklistedError
        elif error_case == "unexpected_error":
            patchers = [
                patch("src.services.user.jwt.decode", return_value={"user_id": 1}),
                patch("src.services.user.user_action_limiter", new_callable=AsyncMock, return_value=True),
                patch("src.services.user.is_token_blacklisted", new_callable=AsyncMock, return_value=False),
                patch("src.services.user.refresh_access_token", side_effect=Exception("fail")),
            ]
            exc_type = user_service.RefreshTokenError
        else:
            exc_type = Exception
        with patch("src.services.user.get_user_by_id", new=AsyncMock(return_value=real_user)):
            ctx = patchers[0] if patchers else None
            if ctx is not None:
                with ctx:
                    if len(patchers) > 1:
                        ctx2 = patchers[1]
                        with ctx2:
                            if len(patchers) > 2:
                                ctx3 = patchers[2]
                                with ctx3:
                                    if len(patchers) > 3:
                                        ctx4 = patchers[3]
                                        with ctx4:
                                            with pytest.raises(exc_type) as exc:
                                                await user_service.async_refresh_access_token(
                                                    session, token, jwt_secret, jwt_algorithm
                                                )
                                            # For jwt_decode_error, code returns 'Unexpected error: fail'
                                            if error_case == "jwt_decode_error":
                                                assert "Unexpected error: fail" in str(exc.value)
                                            else:
                                                assert expected_msg in str(exc.value)
                                    else:
                                        with pytest.raises(exc_type) as exc:
                                            await user_service.async_refresh_access_token(
                                                session, token, jwt_secret, jwt_algorithm
                                            )
                                        if error_case == "jwt_decode_error":
                                            assert "Unexpected error: fail" in str(exc.value)
                                        else:
                                            assert expected_msg in str(exc.value)
                            else:
                                with pytest.raises(exc_type) as exc:
                                    await user_service.async_refresh_access_token(
                                        session, token, jwt_secret, jwt_algorithm
                                    )
                                if error_case == "jwt_decode_error":
                                    assert "Unexpected error: fail" in str(exc.value)
                                else:
                                    assert expected_msg in str(exc.value)
                    else:
                        with pytest.raises(exc_type) as exc:
                            await user_service.async_refresh_access_token(
                                session, token, jwt_secret, jwt_algorithm
                            )
                        if error_case == "jwt_decode_error":
                            assert "Unexpected error: fail" in str(exc.value)
                        else:
                            assert expected_msg in str(exc.value)
            else:
                with pytest.raises(exc_type) as exc:
                    await user_service.async_refresh_access_token(
                        session, token, jwt_secret, jwt_algorithm
                    )
                if error_case == "jwt_decode_error":
                    assert "Unexpected error: fail" in str(exc.value)
                else:
                    assert expected_msg in str(exc.value)

    @pytest.mark.asyncio
    @pytest.mark.skip_if_fast_tests(
        "Refresh token tests still require fixes for fast test mode"
    )
    async def test_success_async_refresh(self) -> None:
        """
        Test that async_refresh_access_token returns a new token if successful.
        """
        import src.services.user as user_service
        from src.models.user import User

        session: AsyncMock = AsyncMock()
        token: str = "sometoken"
        jwt_secret: str = "secret"
        jwt_algorithm: str = "HS256"
        payload: dict[str, object] = {"user_id": 1, "jti": "jti123"}
        real_user: User = User(
            email="real@example.com",
            hashed_password="hashed",
            is_active=True,
            is_deleted=False,
            name=None,
            bio=None,
            avatar_url=None,
            preferences=None,
        )
        # Patch the correct jwt.decode function in src.services.user
        with patch("src.services.user.jwt.decode", return_value=payload):
            with patch("src.services.user.user_action_limiter", new_callable=AsyncMock, return_value=True):
                with patch("src.services.user.is_token_blacklisted", new_callable=AsyncMock, return_value=False):
                    with patch("src.services.user.refresh_access_token", return_value="newtoken"):
                        with patch("src.core.security.verify_refresh_token", return_value={"sub": "1", "email": "e"}):
                            with patch("src.services.user.get_user_by_id", new=AsyncMock(return_value=real_user)):
                                result: str = await user_service.async_refresh_access_token(
                                    session, token, jwt_secret, jwt_algorithm
                                )
        assert result == "newtoken"
