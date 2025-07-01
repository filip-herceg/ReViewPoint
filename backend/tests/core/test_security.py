from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
from jose import jwt

from src.core.security import create_access_token
from tests.test_templates import SecurityUnitTestTemplate


class TestSecurity(SecurityUnitTestTemplate):
    def test_jwt_token_creation(self):
        data = {"sub": "1", "email": "test@example.com"}
        token = create_access_token(data=data)
        self.assert_jwt_claims(
            token=token,
            secret=cast(str, settings.jwt_secret_key),
            algorithm=settings.jwt_algorithm,
            expected_claims={"sub": "1", "email": "test@example.com"},
        )

    @pytest.mark.jwt
    def test_manual_jwt_token(self):
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
        self.assert_jwt_claims(
            token=token,
            secret=cast(str, settings.jwt_secret_key),
            algorithm=settings.jwt_algorithm,
            expected_claims={
                "sub": "42",
                "email": "testuser@example.com",
                "jti": "test-jwt-id-123456789",
            },
        )

    def test_jwt_expired(self):
        payload = {
            "sub": "expired",
            "exp": int((datetime.now(UTC) - timedelta(seconds=1)).timestamp()),
            "iat": int((datetime.now(UTC) - timedelta(minutes=1)).timestamp()),
        }
        token = jwt.encode(
            payload,
            cast(str, settings.jwt_secret_key),
            algorithm=settings.jwt_algorithm,
        )
        self.assert_jwt_expired(
            token=token,
            secret=cast(str, settings.jwt_secret_key),
            algorithm=settings.jwt_algorithm,
        )

    def test_jwt_invalid_signature(self):
        data = {"sub": "1", "email": "test@example.com"}
        token = create_access_token(data=data)
        self.assert_jwt_invalid(
            token=token,
            secret="not_the_real_secret",
            algorithm=settings.jwt_algorithm,
        )

    def test_patch_jwt_secret(self):
        # Patch the secret and check that a valid token now fails
        data = {"sub": "1", "email": "test@example.com"}
        token = create_access_token(data=data)
        self.patch_jwt_secret("not_the_real_secret")
        self.assert_jwt_invalid(
            token=token,
            secret="not_the_real_secret",
            algorithm=settings.jwt_algorithm,
        )
