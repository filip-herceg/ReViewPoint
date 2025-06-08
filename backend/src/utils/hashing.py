"""
Password hashing and verification utilities using passlib's bcrypt.
"""

from loguru import logger
from passlib.context import CryptContext

# bcrypt context for password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Standard security level
    bcrypt__ident="2b",  # Use modern bcrypt variant
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
