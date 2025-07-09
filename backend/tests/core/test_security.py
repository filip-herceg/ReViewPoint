from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from typing import Final, cast

import pytest
from jose import jwt

from src.core.config import get_settings
from src.core.security import create_access_token
from tests.test_templates import SecurityUnitTestTemplate


class TestSecurity(SecurityUnitTestTemplate):
    # Test data as typed constants
    _TEST_USER_ID: Final[str] = "1"
    _TEST_EMAIL: Final[str] = "test@example.com"
    _TEST_USER_ID_2: Final[str] = "42"
    _TEST_EMAIL_2: Final[str] = "testuser@example.com"
    _TEST_JTI: Final[str] = "test-jwt-id-123456789"
    _EXPIRED_USER_ID: Final[str] = "expired"
    _FAKE_SECRET: Final[str] = "not_the_real_secret"
    _TOKEN_EXPIRY_MINUTES: Final[int] = 30
    _TEST_PASSWORD: Final[str] = "TestPassword123!"

    def test_jwt_token_creation(self) -> None:
        """Test JWT token creation with basic user data."""
        settings = get_settings()
        data: Mapping[str, str] = {"sub": self._TEST_USER_ID, "email": self._TEST_EMAIL}
        token: str = create_access_token(data=data)
        self.assert_jwt_claims(
            token=token,
            secret=cast(str, settings.jwt_secret_key),
            algorithm=settings.jwt_algorithm,
            expected_claims={"sub": self._TEST_USER_ID, "email": self._TEST_EMAIL},
        )

    @pytest.mark.jwt
    def test_manual_jwt_token(self) -> None:
        """Test manual JWT token creation with full payload."""
        settings = get_settings()
        current_time: datetime = datetime.now(UTC)
        expiry_time: datetime = current_time + timedelta(
            minutes=self._TOKEN_EXPIRY_MINUTES
        )

        payload: dict[str, str | int] = {
            "sub": self._TEST_USER_ID_2,
            "email": self._TEST_EMAIL_2,
            "exp": int(expiry_time.timestamp()),
            "iat": int(current_time.timestamp()),
            "jti": self._TEST_JTI,
        }
        token: str = jwt.encode(
            payload,
            cast(str, settings.jwt_secret_key),
            algorithm=settings.jwt_algorithm,
        )
        self.assert_jwt_claims(
            token=token,
            secret=cast(str, settings.jwt_secret_key),
            algorithm=settings.jwt_algorithm,
            expected_claims={
                "sub": self._TEST_USER_ID_2,
                "email": self._TEST_EMAIL_2,
                "jti": self._TEST_JTI,
            },
        )

    def test_jwt_expired(self) -> None:
        """Test JWT token expiration handling."""
        settings = get_settings()
        current_time: datetime = datetime.now(UTC)
        expired_time: datetime = current_time - timedelta(seconds=1)
        issued_time: datetime = current_time - timedelta(minutes=1)

        payload: dict[str, str | int] = {
            "sub": self._EXPIRED_USER_ID,
            "exp": int(expired_time.timestamp()),
            "iat": int(issued_time.timestamp()),
        }
        token: str = jwt.encode(
            payload,
            cast(str, settings.jwt_secret_key),
            algorithm=settings.jwt_algorithm,
        )
        self.assert_jwt_expired(
            token=token,
            secret=cast(str, settings.jwt_secret_key),
            algorithm=settings.jwt_algorithm,
        )

    def test_jwt_invalid_signature(self) -> None:
        """Test JWT token with invalid signature."""
        settings = get_settings()
        data: Mapping[str, str] = {"sub": self._TEST_USER_ID, "email": self._TEST_EMAIL}
        token: str = create_access_token(data=data)
        self.assert_jwt_invalid(
            token=token,
            secret=self._FAKE_SECRET,
            algorithm=settings.jwt_algorithm,
        )

    def test_patch_jwt_secret(self) -> None:
        """Test patching JWT secret and verifying token becomes invalid."""
        settings = get_settings()
        # Create a token with the original secret
        data: Mapping[str, str] = {"sub": self._TEST_USER_ID, "email": self._TEST_EMAIL}
        token: str = create_access_token(data=data)

        # Patch the secret and check that the valid token now fails
        self.patch_jwt_secret(self._FAKE_SECRET)
        self.assert_jwt_invalid(
            token=token,
            secret=self._FAKE_SECRET,
            algorithm=settings.jwt_algorithm,
        )
