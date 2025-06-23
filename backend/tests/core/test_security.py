from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
from jose import jwt

from src.core.config import settings
from src.core.security import create_access_token


def test_jwt_token_creation() -> None:
    """Test that the JWT token creation works correctly with the right secret key."""
    data = {"sub": "1", "email": "test@example.com"}
    token = create_access_token(data=data)
    decoded = jwt.decode(
        token,
        cast(str, settings.jwt_secret_key),
        algorithms=[settings.jwt_algorithm],
    )
    assert decoded["sub"] == "1"
    assert decoded["email"] == "test@example.com"
    assert "exp" in decoded
    assert "iat" in decoded


@pytest.mark.jwt
def test_manual_jwt_token() -> None:
    """Test that a manually created JWT token can be decoded and contains expected claims."""
    payload = {
        "sub": "42",
        "email": "testuser@example.com",
        "exp": int((datetime.now(UTC) + timedelta(minutes=30)).timestamp()),
        "iat": int(datetime.now(UTC).timestamp()),
        "jti": "test-jwt-id-123456789",
    }
    token = jwt.encode(
        payload,
        cast(str, settings.jwt_secret_key),
        algorithm=settings.jwt_algorithm,
    )
    decoded = jwt.decode(
        token,
        cast(str, settings.jwt_secret_key),
        algorithms=[settings.jwt_algorithm],
    )
    assert decoded["sub"] == "42"
    assert decoded["email"] == "testuser@example.com"
    assert decoded["jti"] == "test-jwt-id-123456789"
    assert "exp" in decoded
    assert "iat" in decoded
