"""
JWT creation and validation utilities for authentication.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from loguru import logger

from src.core.config import settings

# Add current dir to path for stubs
# NOTE: Removed sys.path modification as it is not essential for production.

__all__ = ["create_access_token", "verify_access_token"]


def create_access_token(data: dict[str, Any]) -> str:
    """
    Create a JWT access token with the given data payload.
    Uses config-driven secret, expiry, and algorithm.
    Never log or expose the token.
    Adds a unique jti for blacklisting support.
    """
    try:
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
        to_encode["exp"] = expire
        # Add a unique JWT ID (jti) for blacklisting
        to_encode["jti"] = str(uuid.uuid4())
        if not settings.jwt_secret_key:
            logger.error(
                "JWT secret key is not configured. Cannot create access token."
            )
            raise ValueError("JWT secret key is not configured.")
        token: str = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
        logger.debug(
            "JWT access token created (claims: {})",
            {k: v for k, v in to_encode.items() if k != "exp"},
        )
        return str(token)
    except ValueError as e:
        logger.error("ValueError during JWT access token creation: {}", str(e))
        raise
    except JWTError as e:
        logger.error("JWTError during JWT access token creation: {}", str(e))
        raise
    raise RuntimeError("Failed to create access token")


def verify_access_token(token: str) -> dict[str, Any]:
    """
    Validate a JWT access token and return the decoded payload.
    If authentication is disabled, return a default admin payload.
    """
    if not settings.auth_enabled:
        logger.warning(
            "Authentication is DISABLED! Bypassing token verification and returning default admin payload."
        )
        from datetime import UTC, datetime, timedelta

        now = datetime.now(UTC)
        return {
            "sub": "dev-user",
            "role": "admin",
            "is_authenticated": True,
            "exp": int((now + timedelta(hours=24)).timestamp()),
        }

    # Early validation of token format to catch obviously malformed tokens
    # JWT tokens should have 3 parts separated by dots
    if not token or not isinstance(token, str) or token.count(".") != 2:
        logger.warning("JWT access token validation failed: Malformed token format")
        raise JWTError("Invalid token format")

    try:
        if not settings.jwt_secret_key:
            logger.error(
                "JWT secret key is not configured. Cannot verify access token."
            )
            raise ValueError("JWT secret key is not configured.")
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if not isinstance(payload, dict):
            raise TypeError("Decoded JWT payload is not a dictionary")
        logger.debug(
            "JWT access token successfully verified (claims: {})",
            {k: v for k, v in payload.items() if k != "exp"},
        )
        return payload
    except JWTError as e:
        logger.warning("JWT access token validation failed: {}", str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error during JWT validation: {}", str(e))
        raise
    raise RuntimeError("Failed to verify access token")
