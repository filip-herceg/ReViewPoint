"""
Tests for JWT creation and validation utilities in backend.core.security.
"""

import pytest
from jose import JWTError

from src.core import security
from src.core.config import settings


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
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={"verify_exp": False},
    )
    payload["exp"] = int(time.time()) - 60
    expired_token = jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
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
