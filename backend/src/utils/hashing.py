"""
Password hashing and verification utilities using passlib's bcrypt.
"""

from typing import Final, Literal, Protocol

from loguru import logger
from passlib.context import CryptContext

# bcrypt context for password hashing
from src.core.config import get_settings


# --- Advanced typing for settings ---
class SettingsProtocol(Protocol):
    BCRYPT_ROUNDS: int
    BCRYPT_IDENT: str


# --- Constants ---
SCHEME_BCRYPT: Final[Literal["bcrypt"]] = "bcrypt"
SCHEMES: Final[tuple[Literal["bcrypt"], ...]] = (SCHEME_BCRYPT,)
DEPRECATED_POLICY: Final[Literal["auto"]] = "auto"


def _get_pwd_context() -> CryptContext:
    """
    Get password context with current settings.
    Returns:
        CryptContext: The password hashing context.
    Raises:
        AttributeError: If settings do not have required attributes.
    """
    settings: SettingsProtocol = get_settings()  # type: ignore[assignment]
    # If get_settings() does not conform, a runtime error will occur, which is desired for strict typing.
    schemes: tuple[Literal["bcrypt"], ...] = SCHEMES
    deprecated: Literal["auto"] = DEPRECATED_POLICY
    bcrypt_rounds: int = getattr(settings, "BCRYPT_ROUNDS", 12)
    bcrypt_ident: str = getattr(settings, "BCRYPT_IDENT", "2b")
    return CryptContext(
        schemes=schemes,
        deprecated=deprecated,
        bcrypt__rounds=bcrypt_rounds,  # Configurable rounds
        bcrypt__ident=bcrypt_ident,  # Configurable identifier
    )


def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    Args:
        password (str): The plain password to hash.
    Returns:
        str: The bcrypt hash of the password.
    Raises:
        ValueError: If password is not hashable.
    """
    # Never log or expose the plain password
    logger.debug("Hashing password (input not logged)")
    pwd_context: CryptContext = _get_pwd_context()
    hash_result: str = pwd_context.hash(password)
    return hash_result


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain password against a given bcrypt hash.
    Args:
        plain (str): The plain password to verify.
        hashed (str): The bcrypt hash to verify against.
    Returns:
        bool: True if the password matches the hash, False otherwise.
    Raises:
        ValueError: If verification fails due to invalid hash or input.
    """
    # Never log or expose the plain password
    logger.debug("Verifying password (input not logged)")
    pwd_context: CryptContext = _get_pwd_context()
    result: bool = pwd_context.verify(plain, hashed)
    return result
