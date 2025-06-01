"""
JWT creation and validation utilities for authentication.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from loguru import logger

from core.config import settings

# Add current dir to path for stubs
# NOTE: Removed sys.path modification as it is not essential for production.

__all__ = ["create_access_token", "verify_access_token"]


def create_access_token(data: dict[str, Any]) -> str:
    """
    Create a JWT access token with the given data payload.
    Uses config-driven secret, expiry, and algorithm.
    Never log or expose the token.
    """
    try:
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
        to_encode["exp"] = expire
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
    """
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
        logger.debug(
            "JWT access token successfully verified (claims: {})",
            {k: v for k, v in payload.items() if k != "exp"},
        )
        if not isinstance(payload, dict):
            raise TypeError("Decoded JWT payload is not a dictionary")
        return payload
    except JWTError as e:
        logger.warning("JWT access token validation failed: {}", str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error during JWT validation: {}", str(e))
        raise
    raise RuntimeError("Failed to verify access token")
