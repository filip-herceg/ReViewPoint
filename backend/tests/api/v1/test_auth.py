"""
Tests for JWT creation and validation utilities in backend.core.security.
"""

import pytest
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import security
from src.core.config import settings
from src.models.user import User


def test_create_and_verify_access_token() -> None:
    data = {"sub": "user123", "role": "admin"}
    token = security.create_access_token(data)
    assert isinstance(token, str)
    payload = security.verify_access_token(token)
    assert payload["sub"] == "user123"
    assert payload["role"] == "admin"
    assert "exp" in payload


def test_verify_access_token_invalid() -> None:
    # Tamper with token
    data = {"sub": "user123"}
    token = security.create_access_token(data)
    tampered = token + "x"
    with pytest.raises(JWTError):
        security.verify_access_token(tampered)


def test_verify_access_token_expired(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch settings to expire immediately
    monkeypatch.setattr(settings, "jwt_expire_minutes", -1)
    token = security.create_access_token({"sub": "expired"})
    # Decode, set exp to past, re-encode
    import time

    from jose import jwt

    payload = jwt.decode(
        token,
        str(settings.jwt_secret_key),
        algorithms=[settings.jwt_algorithm],
        options={"verify_exp": False},
    )
    payload["exp"] = int(time.time()) - 60
    expired_token = jwt.encode(
        payload, str(settings.jwt_secret_key), algorithm=settings.jwt_algorithm
    )
    with pytest.raises(JWTError):
        security.verify_access_token(expired_token)
    # Restore default expiry
    monkeypatch.setattr(settings, "jwt_expire_minutes", 30)


def test_create_access_token_logs(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level("DEBUG")
    data = {"sub": "logtest"}
    token = security.create_access_token(data)
    assert any("JWT access token created" in r.message for r in caplog.records)
    security.verify_access_token(token)
    assert any(
        "JWT access token successfully verified" in r.message for r in caplog.records
    )


def test_verify_access_token_logs_failure(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("WARNING")
    with pytest.raises(JWTError):
        security.verify_access_token("invalid.token")
    assert any(
        "validation failed" in r.message or "Unexpected error" in r.message
        for r in caplog.records
    )


def test_create_access_token_missing_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "jwt_secret_key", None)
    with pytest.raises(ValueError):
        security.create_access_token({"sub": "user"})
    monkeypatch.setattr(settings, "jwt_secret_key", "testsecret")


def test_create_access_token_jwt_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Simulate JWTError by monkeypatching jwt.encode
    def bad_encode(*args: object, **kwargs: object) -> str:
        from jose import JWTError

        raise JWTError("fail")

    monkeypatch.setattr(security.jwt, "encode", bad_encode)
    with pytest.raises(Exception):
        security.create_access_token({"sub": "user"})


def test_verify_access_token_missing_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "auth_enabled", True)
    monkeypatch.setattr(settings, "jwt_secret_key", None)
    from jose import jwt

    token = jwt.encode({"sub": "user"}, "dummy", algorithm="HS256")
    with pytest.raises(ValueError):
        security.verify_access_token(token)
    monkeypatch.setattr(settings, "jwt_secret_key", "testsecret")


def test_verify_access_token_type_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Simulate jwt.decode returning a non-dict
    def bad_decode(*args: object, **kwargs: object) -> object:
        return "notadict"

    monkeypatch.setattr(security.jwt, "decode", bad_decode)
    token = security.create_access_token({"sub": "user"})
    with pytest.raises(TypeError):
        security.verify_access_token(token)


def test_verify_access_token_unexpected_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Simulate unexpected error in jwt.decode
    def raise_error(*args: object, **kwargs: object) -> object:
        raise RuntimeError("boom")

    monkeypatch.setattr(security.jwt, "decode", raise_error)
    token = security.create_access_token({"sub": "user"})
    with pytest.raises(RuntimeError):
        security.verify_access_token(token)


@pytest.mark.asyncio
async def test_protected_endpoint_accessible_when_auth_disabled(
    monkeypatch: pytest.MonkeyPatch, async_session: AsyncSession
) -> None:
    monkeypatch.setattr(settings, "auth_enabled", False)
    from src.api.deps import get_current_user

    user = await get_current_user(token="irrelevant", session=async_session)
    assert isinstance(user, User)
    assert user.email == "dev@example.com"
    assert user.is_active
    monkeypatch.setattr(settings, "auth_enabled", True)


@pytest.mark.asyncio
async def test_get_current_user_logs_warning_when_auth_disabled(
    monkeypatch: pytest.MonkeyPatch,
    async_session: AsyncSession,
    loguru_list_sink: list[str],
) -> None:
    monkeypatch.setattr(settings, "auth_enabled", False)
    from src.api.deps import get_current_user

    await get_current_user(token="irrelevant", session=async_session)
    logs = "\n".join(loguru_list_sink)
    assert "Authentication is DISABLED! Returning development admin user." in logs
    monkeypatch.setattr(settings, "auth_enabled", True)
