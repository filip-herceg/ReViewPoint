from cryptography.fernet import Fernet, InvalidToken
from loguru import logger

from src.core.config import settings

# This should be set securely in production!
FERNET_KEY = getattr(settings, "fernet_key", None)
if not FERNET_KEY:
    logger.warning(
        "Fernet key not set in config; using insecure default. Set REVIEWPOINT_FERNET_KEY!"
    )
    FERNET_KEY = Fernet.generate_key()
fernet = Fernet(FERNET_KEY)


def encrypt_bytes(data: bytes) -> bytes:
    try:
        return fernet.encrypt(data)
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise


def decrypt_bytes(data: bytes) -> bytes:
    try:
        return fernet.decrypt(data)
    except InvalidToken:
        logger.error("Decryption failed: Invalid token")
        raise
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise
