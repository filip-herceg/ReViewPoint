"""
JWT creation and validation utilities for authentication.
"""

import uuid
from collections.abc import Mapping, MutableMapping, Sequence
from datetime import UTC, datetime, timedelta
from typing import (
    Optional,
    TypedDict,
    cast,
)

from jose import JWTError, jwt
from loguru import logger

from src.core.config import get_settings

# Add current dir to path for stubs
# NOTE: Removed sys.path modification as it is not essential for production.


__all__: Sequence[str] = (
    "create_access_token",
    "verify_access_token",
    "decode_access_token",
    "create_refresh_token",
)


class JWTPayload(TypedDict, total=False):
    sub: str
    role: str
    is_authenticated: bool
    exp: int
    iat: int
    jti: str
    # Add other claims as needed


def create_access_token(data: Mapping[str, str | int | bool]) -> str:
    """
    Create a JWT access token with the given data payload.
    Uses config-driven secret, expiry, and algorithm.
    Never log or expose the token.
    Adds a unique jti for blacklisting support.

    Raises:
        ValueError: If the JWT secret key is not configured.
        JWTError: If JWT encoding fails.
        RuntimeError: If token creation fails for unknown reasons.
    """
    to_encode: MutableMapping[str, str | int | bool | datetime] = dict(data)
    settings = get_settings()
    expire: datetime = datetime.now(UTC) + timedelta(
        minutes=settings.jwt_expire_minutes
    )
    to_encode["exp"] = expire
    to_encode["iat"] = int(datetime.now(UTC).timestamp())
    to_encode["jti"] = str(uuid.uuid4())
    if not settings.jwt_secret_key:
        logger.error("JWT secret key is not configured. Cannot create access token.")
        raise ValueError("JWT secret key is not configured.")
    
    try:
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


def verify_access_token(token: str) -> JWTPayload:
    """
    Validate a JWT access token and return the decoded payload.
    If authentication is disabled, return a default admin payload.

    Raises:
        JWTError: If the token is invalid or cannot be decoded.
        ValueError: If the JWT secret key is not configured.
        TypeError: If the decoded payload is not a dictionary.
        RuntimeError: If verification fails for unknown reasons.
    """
    settings = get_settings()
    if not settings.auth_enabled:
        logger.warning(
            "Authentication is DISABLED! Bypassing token verification and returning default admin payload."
        )
        now: datetime = datetime.now(UTC)
        return JWTPayload(
            sub="dev-user",
            role="admin",
            is_authenticated=True,
            exp=int((now + timedelta(hours=24)).timestamp()),
        )

    # Early validation of token format to catch obviously malformed tokens
    # JWT tokens should have 3 parts separated by dots
    if not token or not isinstance(token, str) or token.count(".") != 2:
        logger.warning("JWT access token validation failed: Malformed token format")
        raise JWTError("Invalid token format")

    if not settings.jwt_secret_key:
        logger.error("JWT secret key is not configured. Cannot verify access token.")
        raise ValueError("JWT secret key is not configured.")
    try:
        payload: dict[str, object] = jwt.decode(
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
        # Cast to JWTPayload for type safety
        return cast(JWTPayload, payload)
    except JWTError as e:
        logger.warning("JWT access token validation failed: {}", str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error during JWT validation: {}", str(e))
        raise
    raise RuntimeError("Failed to verify access token")


def decode_access_token(token: str) -> JWTPayload:
    """
    Alias for verify_access_token for backward compatibility.
    Decode and validate a JWT access token and return the payload.
    
    Args:
        token: The JWT token to decode and validate
        
    Returns:
        JWTPayload: The decoded and validated token payload
        
    Raises:
        JWTError: If the token is invalid or cannot be decoded.
        ValueError: If the JWT secret key is not configured.
        TypeError: If the decoded payload is not a dictionary.
        RuntimeError: If verification fails for unknown reasons.
    """
    return verify_access_token(token)


def create_refresh_token(data: Mapping[str, str | int | bool]) -> str:
    """
    Create a JWT refresh token with the given data payload.
    Uses config-driven secret, expiry, and algorithm.
    Refresh tokens typically have a longer expiry than access tokens.
    Adds a unique jti for blacklisting support.

    Raises:
        ValueError: If the JWT secret key is not configured.
        JWTError: If JWT encoding fails.
        RuntimeError: If token creation fails for unknown reasons.
    """
    settings = get_settings()
    to_encode: MutableMapping[str, str | int | bool | datetime] = dict(data)
    expire: datetime = datetime.now(UTC) + timedelta(days=7)
    to_encode["exp"] = expire
    to_encode["iat"] = int(datetime.now(UTC).timestamp())
    to_encode["jti"] = str(uuid.uuid4())
    if not settings.jwt_secret_key:
        logger.error("JWT secret key is not configured. Cannot create refresh token.")
        raise ValueError("JWT secret key is not configured.")
    try:
        token: str = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
        logger.debug(
            "JWT refresh token created (claims: {})",
            {k: v for k, v in to_encode.items() if k != "exp"},
        )
        return str(token)
    except ValueError as e:
        logger.error("ValueError during JWT refresh token creation: {}", str(e))
        raise
    except JWTError as e:
        logger.error("JWTError during JWT refresh token creation: {}", str(e))
        raise
    raise RuntimeError("Failed to create refresh token")


def verify_refresh_token(token: str) -> JWTPayload:
    """
    Validate a JWT refresh token and return the decoded payload.
    Uses the same secret and algorithm as create_refresh_token.

    Raises:
        JWTError: If the token is invalid or cannot be decoded.
        ValueError: If the JWT secret key is not configured or required claims are missing/expired.
        TypeError: If the decoded payload is not a dictionary.
    """
    settings = get_settings()
    if not settings.jwt_secret_key:
        logger.error("JWT secret key is not configured. Cannot verify refresh token.")
        raise ValueError("JWT secret key is not configured.")
    try:
        payload: dict[str, object] = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if not isinstance(payload, dict):
            raise TypeError("Decoded JWT payload is not a dictionary")
        # Ensure required claims are present
        if not ("sub" in payload and "jti" in payload and "exp" in payload):
            raise ValueError("Refresh token missing required claims (sub, jti, exp)")
        # Optionally: check exp is in the future
        exp_val: int = (
            int(payload["exp"])
            if isinstance(payload["exp"], int)
            else int(str(payload["exp"]))
        )
        if exp_val < int(datetime.now(UTC).timestamp()):
            raise ValueError("Refresh token is expired")
        return cast(JWTPayload, payload)
    except JWTError as e:
        logger.error("JWT refresh token verification failed: %s", str(e))
        raise ValueError("Invalid or expired refresh token") from e
    except Exception as e:
        logger.error("JWT refresh token verification failed: %s", str(e))
        raise ValueError("Invalid or expired refresh token") from e
