"""
Password hashing and verification utilities using passlib's bcrypt.
"""

from loguru import logger
from passlib.context import CryptContext

# bcrypt context for password hashing
from src.core.config import settings  # Adjust import path as needed

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=getattr(settings, "BCRYPT_ROUNDS", 12),  # Configurable rounds
    bcrypt__ident=getattr(settings, "BCRYPT_IDENT", "2b"),  # Configurable identifier
)


def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    Args:
        password (str): The plain password to hash.
    Returns:
        str: The bcrypt hash of the password.
    """
    # Never log or expose the plain password
    logger.debug("Hashing password (input not logged)")
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain password against a given bcrypt hash.
    Args:
        plain (str): The plain password to verify.
        hashed (str): The bcrypt hash to verify against.
    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    # Never log or expose the plain password
    logger.debug("Verifying password (input not logged)")
    return pwd_context.verify(plain, hashed)
