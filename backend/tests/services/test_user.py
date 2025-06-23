from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.user import User
from src.services import user as user_service


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


@pytest.mark.asyncio
async def test_authenticate_user_success(monkeypatch: pytest.MonkeyPatch) -> None:
    session: Any = AsyncMock()
    dummy: DummyUser = DummyUser()
    session.execute = AsyncMock(return_value=DummyResult(dummy))
    monkeypatch.setattr(user_service, "verify_password", lambda pw, hpw: True)
    monkeypatch.setattr(user_service, "create_access_token", lambda payload: "token")
    monkeypatch.setattr(user_service, "settings", MagicMock(auth_enabled=True))
    with patch("src.repositories.user.update_last_login", new_callable=AsyncMock):
        token = await user_service.authenticate_user(session, dummy.email, "pw")
    assert token == "token"


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session: Any = AsyncMock()
    dummy: DummyUser = DummyUser()
    session.execute = AsyncMock(return_value=DummyResult(dummy))
    monkeypatch.setattr(user_service, "verify_password", lambda pw, hpw: False)
    monkeypatch.setattr(user_service, "settings", MagicMock(auth_enabled=True))
    with patch("src.repositories.user.update_last_login", new_callable=AsyncMock):
        with pytest.raises(user_service.ValidationError):
            await user_service.authenticate_user(session, dummy.email, "badpw")


@pytest.mark.asyncio
async def test_authenticate_user_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    session: Any = AsyncMock()
    session.execute = AsyncMock(return_value=DummyResult(None))
    monkeypatch.setattr(user_service, "settings", MagicMock(auth_enabled=True))
    with patch("src.repositories.user.update_last_login", new_callable=AsyncMock):
        with pytest.raises(user_service.UserNotFoundError):
            await user_service.authenticate_user(session, "nope@example.com", "pw")


@pytest.mark.asyncio
async def test_authenticate_user_auth_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    session: Any = AsyncMock()
    monkeypatch.setattr(user_service, "settings", MagicMock(auth_enabled=False))
    monkeypatch.setattr(user_service, "create_access_token", lambda payload: "devtoken")
    token = await user_service.authenticate_user(session, "any@example.com", "pw")
    assert token == "devtoken"


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


def test_is_authenticated_active(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(user_service, "settings", MagicMock(auth_enabled=True))
    user: User = make_real_user(is_active=True, is_deleted=False)
    assert user_service.is_authenticated(user)


def test_is_authenticated_inactive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(user_service, "settings", MagicMock(auth_enabled=True))
    user: User = make_real_user(is_active=False, is_deleted=False)
    assert not user_service.is_authenticated(user)


def test_is_authenticated_deleted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(user_service, "settings", MagicMock(auth_enabled=True))
    user: User = make_real_user(is_active=True, is_deleted=True)
    assert not user_service.is_authenticated(user)


def test_is_authenticated_auth_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(user_service, "settings", MagicMock(auth_enabled=False))
    user: User = make_real_user(is_active=False, is_deleted=True)
    assert user_service.is_authenticated(user)


def test_refresh_access_token_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        user_service, "verify_access_token", lambda t: {"sub": "1", "email": "e"}
    )
    monkeypatch.setattr(user_service, "create_access_token", lambda payload: "newtoken")
    assert user_service.refresh_access_token(1, "sometoken") == "newtoken"


def test_refresh_access_token_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    def bad_verify(token: str) -> None:
        raise Exception("bad token")

    monkeypatch.setattr(user_service, "verify_access_token", bad_verify)
    with pytest.raises(user_service.ValidationError):
        user_service.refresh_access_token(1, "badtoken")


def test_verify_email_token_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(user_service, "verify_access_token", lambda t: {"email": "e"})
    assert user_service.verify_email_token("tok") == {"email": "e"}


def test_verify_email_token_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    def bad_verify(token: str) -> None:
        raise Exception("bad token")

    monkeypatch.setattr(user_service, "verify_access_token", bad_verify)
    with pytest.raises(user_service.ValidationError):
        user_service.verify_email_token("badtok")


def test_get_password_reset_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        user_service, "create_access_token", lambda payload: "resettoken"
    )
    monkeypatch.setattr(user_service, "settings", MagicMock(environment="dev"))
    assert user_service.get_password_reset_token("e@x.com") == "resettoken"


def test_validate_password_strength_ascii() -> None:
    user_service.validate_password_strength("GoodPass123!")


def test_validate_password_strength_whitespace() -> None:
    with pytest.raises(user_service.ValidationError):
        user_service.validate_password_strength("bad pass")


def test_validate_password_strength_non_ascii() -> None:
    with pytest.raises(user_service.ValidationError):
        user_service.validate_password_strength("pässword")


def test_validate_password_strength_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        user_service, "get_password_validation_error", lambda pw: "fail"
    )
    with pytest.raises(user_service.ValidationError):
        user_service.validate_password_strength("bad")


@pytest.mark.asyncio
async def test_get_user_by_username_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    dummy = DummyUser()
    session.execute = AsyncMock(return_value=DummyResult(dummy))
    monkeypatch.setattr(user_service, "validate_email", lambda e: True)
    user = await user_service.get_user_by_username(session, "test@example.com")
    assert user is dummy


@pytest.mark.asyncio
async def test_get_user_by_username_invalid_email(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = AsyncMock()
    monkeypatch.setattr(user_service, "validate_email", lambda e: False)
    with pytest.raises(user_service.ValidationError):
        await user_service.get_user_by_username(session, "bademail")


@pytest.mark.asyncio
async def test_get_user_by_username_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    session.execute = AsyncMock(return_value=DummyResult(None))
    monkeypatch.setattr(user_service, "validate_email", lambda e: True)
    user = await user_service.get_user_by_username(session, "notfound@example.com")
    assert user is None


@pytest.mark.asyncio
async def test_user_exists_true(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    monkeypatch.setattr(user_service, "validate_email", lambda e: True)
    monkeypatch.setattr(
        user_service.user_repo, "is_email_unique", AsyncMock(return_value=False)
    )
    assert await user_service.user_exists(session, "e@x.com") is True


@pytest.mark.asyncio
async def test_user_exists_false(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    monkeypatch.setattr(user_service, "validate_email", lambda e: True)
    monkeypatch.setattr(
        user_service.user_repo, "is_email_unique", AsyncMock(return_value=True)
    )
    assert await user_service.user_exists(session, "e@x.com") is False


@pytest.mark.asyncio
async def test_user_exists_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    monkeypatch.setattr(user_service, "validate_email", lambda e: False)
    with pytest.raises(user_service.ValidationError):
        await user_service.user_exists(session, "bad")


@pytest.mark.asyncio
async def test_assign_role_and_check(monkeypatch: pytest.MonkeyPatch) -> None:
    user_id = 1
    role = "admin"
    assert await user_service.assign_role(user_id, role) is True
    assert await user_service.check_user_role(user_id, role) is True
    assert await user_service.check_user_role(user_id, "user") is False


@pytest.mark.asyncio
async def test_assign_role_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(user_service.ValidationError):
        await user_service.assign_role(1, "notarole")


def test_revoke_refresh_token() -> None:
    # Just call, should not raise
    user_service.revoke_refresh_token(1, "token")


@pytest.mark.asyncio
async def test_delete_user_account_soft(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    monkeypatch.setattr(
        user_service.user_repo, "soft_delete_user", AsyncMock(return_value=True)
    )
    monkeypatch.setattr(user_service.user_repo, "audit_log_user_change", AsyncMock())
    result = await user_service.delete_user_account(session, 1, anonymize=False)
    assert result is True


@pytest.mark.asyncio
async def test_delete_user_account_anonymize(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    monkeypatch.setattr(
        user_service.user_repo, "anonymize_user", AsyncMock(return_value=True)
    )
    monkeypatch.setattr(user_service.user_repo, "audit_log_user_change", AsyncMock())
    result = await user_service.delete_user_account(session, 1, anonymize=True)
    assert result is True


@pytest.mark.asyncio
async def test_deactivate_user(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    monkeypatch.setattr(
        user_service.user_repo, "deactivate_user", AsyncMock(return_value=True)
    )
    monkeypatch.setattr(user_service.user_repo, "audit_log_user_change", AsyncMock())
    result = await user_service.deactivate_user(session, 1)
    assert result is True


@pytest.mark.asyncio
async def test_reactivate_user(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    monkeypatch.setattr(
        user_service.user_repo, "reactivate_user", AsyncMock(return_value=True)
    )
    monkeypatch.setattr(user_service.user_repo, "audit_log_user_change", AsyncMock())
    result = await user_service.reactivate_user(session, 1)
    assert result is True


@pytest.mark.asyncio
async def test_set_user_preferences(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    dummy = DummyUser()
    session.commit = AsyncMock()
    monkeypatch.setattr(user_service, "get_user_by_id", AsyncMock(return_value=dummy))
    prefs = {"theme": "dark", "locale": "en"}
    result = await user_service.set_user_preferences(session, 1, prefs)
    assert result.theme == "dark"
    assert result.locale == "en"


@pytest.mark.asyncio
async def test_set_user_preferences_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    session.commit = AsyncMock()
    monkeypatch.setattr(user_service, "get_user_by_id", AsyncMock(return_value=None))
    with pytest.raises(user_service.UserNotFoundError):
        await user_service.set_user_preferences(session, 1, {})
