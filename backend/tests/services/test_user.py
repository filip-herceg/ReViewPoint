from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.user import User
from src.services import user as user_service
from tests.test_templates import AuthUnitTestTemplate


class DummyUser:
    def __init__(
        self,
        is_active: bool = True,
        is_deleted: bool = False,
        id: int = 1,
        email: str = "test@example.com",
        hashed_password: str = "hashed",
    ) -> None:
        self.is_active = is_active
        self.is_deleted = is_deleted
        self.id = id
        self.email = email
        self.hashed_password = hashed_password


class DummyResult:
    def __init__(self, user: Any) -> None:
        self._user = user

    def scalar_one_or_none(self) -> Any:
        return self._user


class TestAuthenticateUser(AuthUnitTestTemplate):
    @pytest.mark.asyncio
    async def test_success(self):
        session = AsyncMock()
        dummy = DummyUser()
        session.execute = AsyncMock(return_value=DummyResult(dummy))
        self.patch_dep("src.services.user.verify_password", lambda pw, hpw: True)
        self.patch_dep("src.services.user.create_access_token", lambda payload: "token")
        self.patch_dep(
            "src.services.user.create_refresh_token", lambda payload: "refresh"
        )
        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=True))
        with patch("src.repositories.user.update_last_login", new_callable=AsyncMock):
            tokens = await user_service.authenticate_user(session, dummy.email, "pw")
        access_token, refresh_token = tokens
        assert access_token == "token"
        assert refresh_token == "refresh"

    @pytest.mark.asyncio
    async def test_wrong_password(self):
        session = AsyncMock()
        dummy = DummyUser()
        session.execute = AsyncMock(return_value=DummyResult(dummy))
        self.patch_dep("src.services.user.verify_password", lambda pw, hpw: False)
        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=True))
        with patch("src.repositories.user.update_last_login", new_callable=AsyncMock):
            with pytest.raises(Exception):
                await user_service.authenticate_user(session, dummy.email, "pw")

    @pytest.mark.asyncio
    async def test_user_not_found(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=DummyResult(None))
        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=True))
        with patch("src.repositories.user.update_last_login", new_callable=AsyncMock):
            with pytest.raises(Exception):
                await user_service.authenticate_user(
                    session, "notfound@example.com", "pw"
                )

    @pytest.mark.asyncio
    async def test_inactive_or_deleted_user(self):
        session = AsyncMock()
        dummy = DummyUser(is_active=False)
        session.execute = AsyncMock(return_value=DummyResult(dummy))
        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=True))
        with patch("src.repositories.user.update_last_login", new_callable=AsyncMock):
            with pytest.raises(Exception):
                await user_service.authenticate_user(session, dummy.email, "pw")
        dummy2 = DummyUser(is_deleted=True)
        session.execute = AsyncMock(return_value=DummyResult(dummy2))
        with patch("src.repositories.user.update_last_login", new_callable=AsyncMock):
            with pytest.raises(Exception):
                await user_service.authenticate_user(session, dummy2.email, "pw")

    @pytest.mark.asyncio
    async def test_auth_disabled(self):
        session = AsyncMock()
        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=False))
        self.patch_dep("src.services.user.create_access_token", lambda payload: "token")
        self.patch_dep(
            "src.services.user.create_refresh_token", lambda payload: "refresh"
        )
        tokens = await user_service.authenticate_user(session, "dev@example.com", "pw")
        access_token, refresh_token = tokens
        assert access_token == "token"
        assert refresh_token == "refresh"


def make_real_user(is_active: bool, is_deleted: bool) -> User:
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


class TestIsAuthenticated(AuthUnitTestTemplate):
    def test_active(self):
        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=True))
        user = make_real_user(is_active=True, is_deleted=False)
        assert user_service.is_authenticated(user)

    def test_inactive(self):
        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=True))
        user = make_real_user(is_active=False, is_deleted=False)
        assert not user_service.is_authenticated(user)

    def test_deleted(self):
        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=True))
        user = make_real_user(is_active=True, is_deleted=True)
        assert not user_service.is_authenticated(user)

    def test_auth_disabled(self):
        self.patch_setting(user_service, "settings", MagicMock(auth_enabled=False))
        user = make_real_user(is_active=False, is_deleted=True)
        assert user_service.is_authenticated(user)


class TestRefreshAccessToken(AuthUnitTestTemplate):
    def test_valid(self):
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

    def test_invalid(self):
        def bad_verify(token: str):
            raise Exception("bad token")

        self.patch_dep("src.services.user.verify_access_token", bad_verify)
        self.assert_http_exception(
            lambda: user_service.refresh_access_token(1, "badtoken"), 422
        )


class TestPasswordStrength(AuthUnitTestTemplate):
    @pytest.mark.asyncio
    async def test_ascii(self):
        user_service.validate_password_strength("GoodPass123!")

    @pytest.mark.asyncio
    async def test_whitespace(self):
        with pytest.raises(user_service.ValidationError):
            user_service.validate_password_strength("bad pass")

    @pytest.mark.asyncio
    async def test_non_ascii(self):
        with pytest.raises(user_service.ValidationError):
            user_service.validate_password_strength("pässword")

    @pytest.mark.asyncio
    async def test_error(self):
        with pytest.raises(user_service.ValidationError):
            self.patch_dep(
                "src.services.user.get_password_validation_error", lambda pw: "fail"
            )
            user_service.validate_password_strength("bad")


class TestVerifyEmailToken(AuthUnitTestTemplate):
    @pytest.mark.asyncio
    async def test_valid(self):
        self.patch_dep(
            "src.services.user.verify_access_token", lambda t: {"email": "e"}
        )
        assert user_service.verify_email_token("tok") == {"email": "e"}

    @pytest.mark.asyncio
    async def test_invalid(self):
        def bad_verify(token: str):
            raise Exception("bad token")

        with pytest.raises(user_service.ValidationError):
            self.patch_dep("src.services.user.verify_access_token", bad_verify)
            user_service.verify_email_token("badtok")


class TestPasswordResetToken(AuthUnitTestTemplate):
    @pytest.mark.asyncio
    async def test_get_token(self):
        self.patch_dep(
            "src.services.user.create_access_token", lambda payload: "resettoken"
        )
        self.patch_setting(user_service, "settings", MagicMock(environment="dev"))
        assert user_service.get_password_reset_token("e@x.com") == "resettoken"


class TestGetUserByUsername(AuthUnitTestTemplate):
    @pytest.mark.asyncio
    async def test_valid(self):
        session = AsyncMock()
        dummy = DummyUser()
        session.execute = AsyncMock(return_value=DummyResult(dummy))
        self.patch_dep("src.services.user.validate_email", lambda e: True)
        user = await user_service.get_user_by_username(session, "test@example.com")
        assert user is dummy

    @pytest.mark.asyncio
    async def test_invalid_email(self):
        session = AsyncMock()
        self.patch_dep("src.services.user.validate_email", lambda e: False)
        with pytest.raises(user_service.ValidationError):
            await user_service.get_user_by_username(session, "bademail")

    @pytest.mark.asyncio
    async def test_not_found(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=DummyResult(None))
        self.patch_dep("src.services.user.validate_email", lambda e: True)
        user = await user_service.get_user_by_username(session, "notfound@example.com")
        assert user is None


class TestUserExists(AuthUnitTestTemplate):
    @pytest.mark.asyncio
    async def test_true(self):
        session = AsyncMock()
        self.patch_dep("src.services.user.validate_email", lambda e: True)
        self.patch_async_dep(
            "src.repositories.user.is_email_unique", AsyncMock(return_value=False)
        )
        assert await user_service.user_exists(session, "e@x.com") is True

    @pytest.mark.asyncio
    async def test_false(self):
        session = AsyncMock()
        self.patch_dep("src.services.user.validate_email", lambda e: True)
        self.patch_async_dep(
            "src.repositories.user.is_email_unique", AsyncMock(return_value=True)
        )
        assert await user_service.user_exists(session, "e@x.com") is False

    @pytest.mark.asyncio
    async def test_invalid(self):
        session = AsyncMock()
        self.patch_dep("src.services.user.validate_email", lambda e: False)
        await self.assert_async_http_exception(
            lambda: user_service.user_exists(session, "bad"), 422
        )


class TestAssignRoleAndCheck(AuthUnitTestTemplate):
    @pytest.mark.asyncio
    async def test_assign_and_check(self):
        user_id = 1
        role = "admin"
        assert await user_service.assign_role(user_id, role) is True
        assert await user_service.check_user_role(user_id, role) is True
        assert await user_service.check_user_role(user_id, "user") is False

    @pytest.mark.asyncio
    async def test_assign_invalid(self):
        with pytest.raises(user_service.ValidationError):
            await user_service.assign_role(1, "notarole")


class TestDeleteAndReactivateUser(AuthUnitTestTemplate):
    @pytest.mark.asyncio
    async def test_delete_soft(self):
        session = AsyncMock()
        self.patch_async_dep(
            "src.repositories.user.soft_delete_user", AsyncMock(return_value=True)
        )
        self.patch_async_dep("src.repositories.user.audit_log_user_change", AsyncMock())
        result = await user_service.delete_user_account(session, 1, anonymize=False)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_anonymize(self):
        session = AsyncMock()
        self.patch_async_dep(
            "src.repositories.user.anonymize_user", AsyncMock(return_value=True)
        )
        self.patch_async_dep("src.repositories.user.audit_log_user_change", AsyncMock())
        result = await user_service.delete_user_account(session, 1, anonymize=True)
        assert result is True

    @pytest.mark.asyncio
    async def test_deactivate(self):
        session = AsyncMock()
        self.patch_async_dep(
            "src.repositories.user.deactivate_user", AsyncMock(return_value=True)
        )
        self.patch_async_dep("src.repositories.user.audit_log_user_change", AsyncMock())
        result = await user_service.deactivate_user(session, 1)
        assert result is True

    @pytest.mark.asyncio
    async def test_reactivate(self):
        session = AsyncMock()
        self.patch_async_dep(
            "src.repositories.user.reactivate_user", AsyncMock(return_value=True)
        )
        self.patch_async_dep("src.repositories.user.audit_log_user_change", AsyncMock())
        result = await user_service.reactivate_user(session, 1)
        assert result is True


class TestSetUserPreferences(AuthUnitTestTemplate):
    @pytest.mark.asyncio
    async def test_set(self):
        session = AsyncMock()
        dummy = DummyUser()
        session.commit = AsyncMock()
        self.patch_async_dep(
            "src.services.user.get_user_by_id", AsyncMock(return_value=dummy)
        )
        prefs = {"theme": "dark", "locale": "en"}
        result = await user_service.set_user_preferences(session, 1, prefs)
        assert result.theme == "dark"
        assert result.locale == "en"

    @pytest.mark.asyncio
    async def test_not_found(self):
        session = AsyncMock()
        session.commit = AsyncMock()
        self.patch_async_dep(
            "src.services.user.get_user_by_id", AsyncMock(return_value=None)
        )
        with pytest.raises(user_service.UserNotFoundError):
            await user_service.set_user_preferences(session, 1, {})


class TestAsyncRefreshAccessToken(AuthUnitTestTemplate):
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "error_case,patches,expected_exception,expected_msg",
        [
            (
                "jwt_decode_error",
                [
                    patch(
                        "src.services.user.jwt.decode",
                        side_effect=Exception("fail"),
                    )
                ],
                user_service.RefreshTokenError,
                "JWT decode failed: fail",
            ),
            (
                "missing_user_id",
                [patch("src.services.user.jwt.decode", return_value={})],
                user_service.RefreshTokenError,
                "Invalid token format: missing user_id.",
            ),
            (
                "rate_limited",
                [
                    patch("src.services.user.jwt.decode", return_value={"user_id": 1}),
                    patch(
                        "src.services.user.user_action_limiter",
                        new_callable=AsyncMock,
                        return_value=False,
                    ),
                ],
                user_service.RefreshTokenRateLimitError,
                "Too many token refresh attempts.",
            ),
            (
                "blacklisted",
                [
                    patch("src.services.user.jwt.decode", return_value={"user_id": 1}),
                    patch(
                        "src.services.user.user_action_limiter",
                        new_callable=AsyncMock,
                        return_value=True,
                    ),
                    patch(
                        "src.services.user.is_token_blacklisted",
                        new_callable=AsyncMock,
                        return_value=True,
                    ),
                ],
                user_service.RefreshTokenBlacklistedError,
                "Refresh token is blacklisted.",
            ),
            (
                "unexpected_error",
                [
                    patch("src.services.user.jwt.decode", return_value={"user_id": 1}),
                    patch(
                        "src.services.user.user_action_limiter",
                        new_callable=AsyncMock,
                        return_value=True,
                    ),
                    patch(
                        "src.services.user.is_token_blacklisted",
                        new_callable=AsyncMock,
                        return_value=False,
                    ),
                    patch(
                        "src.services.user.refresh_access_token",
                        side_effect=Exception("fail"),
                    ),
                ],
                user_service.RefreshTokenError,
                "Unexpected error: fail",
            ),
        ],
    )
    async def test_errors(self, error_case, patches, expected_exception, expected_msg):
        session = AsyncMock()
        token = "sometoken"
        jwt_secret = "secret"
        jwt_algorithm = "HS256"
        from src.models.user import User

        real_user = User(
            email="real@example.com",
            hashed_password="hashed",
            is_active=True,
            is_deleted=False,
            name=None,
            bio=None,
            avatar_url=None,
            preferences=None,
        )
        with patch(
            "src.services.user.get_user_by_id", new=AsyncMock(return_value=real_user)
        ):
            # Apply all patches
            with patches[0]:
                if len(patches) > 1:
                    with patches[1]:
                        if len(patches) > 2:
                            with patches[2]:
                                if len(patches) > 3:
                                    with patches[3]:
                                        with pytest.raises(expected_exception) as exc:
                                            await user_service.async_refresh_access_token(
                                                session,
                                                token,
                                                jwt_secret,
                                                jwt_algorithm,
                                            )
                                        assert expected_msg in str(exc.value)
                                else:
                                    with pytest.raises(expected_exception) as exc:
                                        await user_service.async_refresh_access_token(
                                            session, token, jwt_secret, jwt_algorithm
                                        )
                                    assert expected_msg in str(exc.value)
                        else:
                            with pytest.raises(expected_exception) as exc:
                                await user_service.async_refresh_access_token(
                                    session, token, jwt_secret, jwt_algorithm
                                )
                            assert expected_msg in str(exc.value)
                else:
                    with pytest.raises(expected_exception) as exc:
                        await user_service.async_refresh_access_token(
                            session, token, jwt_secret, jwt_algorithm
                        )
                    assert expected_msg in str(exc.value)

    @pytest.mark.asyncio
    async def test_success(self):
        session = AsyncMock()
        token = "sometoken"
        jwt_secret = "secret"
        jwt_algorithm = "HS256"
        payload = {"user_id": 1, "jti": "jti123"}
        from src.models.user import User

        real_user = User(
            email="real@example.com",
            hashed_password="hashed",
            is_active=True,
            is_deleted=False,
            name=None,
            bio=None,
            avatar_url=None,
            preferences=None,
        )
        self.patch_dep("src.services.user.jwt.decode", lambda *a, **kw: payload)
        self.patch_async_dep(
            "src.services.user.user_action_limiter", AsyncMock(return_value=True)
        )
        self.patch_async_dep(
            "src.services.user.is_token_blacklisted", AsyncMock(return_value=False)
        )
        self.patch_dep(
            "src.services.user.refresh_access_token", lambda user_id, token: "newtoken"
        )
        self.patch_dep(
            "src.core.security.verify_refresh_token",
            lambda t: {"sub": "1", "email": "e"},
        )
        with patch(
            "src.services.user.get_user_by_id", new=AsyncMock(return_value=real_user)
        ):
            result = await user_service.async_refresh_access_token(
                session, token, jwt_secret, jwt_algorithm
            )
        assert result == "newtoken"
