"""
Helpers for advanced file URL revocation (token blacklist for local, file_id blacklist for S3).
Persistent file-based storage for demo; replace with DB/Redis for production.
"""

import json
import threading
from pathlib import Path

from loguru import logger

_REVOCATION_LOCK = threading.Lock()
_LOCAL_BLACKLIST_PATH = Path("revoked_tokens.json")
_S3_BLACKLIST_PATH = Path("revoked_s3_files.json")


class FileRevocationError(Exception):
    """Custom error for file revocation operations."""


def revoke_local_token(token: str) -> None:
    """Add a token to the local file access blacklist."""
    try:
        with _REVOCATION_LOCK:
            tokens = set()
            if _LOCAL_BLACKLIST_PATH.exists():
                tokens = set(json.loads(_LOCAL_BLACKLIST_PATH.read_text()))
            tokens.add(token)
            _LOCAL_BLACKLIST_PATH.write_text(json.dumps(list(tokens)))
        logger.info(f"Revoked local token: {token}")
    except Exception as e:
        logger.exception(f"Failed to revoke local token: {token} - {e}")
        raise FileRevocationError(f"Failed to revoke local token: {e}") from e


def is_local_token_revoked(token: str) -> bool:
    """Check if a local file access token is revoked."""
    try:
        with _REVOCATION_LOCK:
            if not _LOCAL_BLACKLIST_PATH.exists():
                logger.debug(
                    f"Local blacklist file does not exist. Token not revoked: {token}"
                )
                return False
            tokens = set(json.loads(_LOCAL_BLACKLIST_PATH.read_text()))
            revoked = token in tokens
            logger.info(f"Checked local token revocation: {token} - revoked={revoked}")
            return revoked
    except Exception as e:
        logger.exception(f"Failed to check local token revocation: {token} - {e}")
        raise FileRevocationError(f"Failed to check local token revocation: {e}") from e


def revoke_s3_file(file_id: str) -> None:
    """Add a file_id to the S3 revocation list."""
    try:
        with _REVOCATION_LOCK:
            ids = set()
            if _S3_BLACKLIST_PATH.exists():
                ids = set(json.loads(_S3_BLACKLIST_PATH.read_text()))
            ids.add(file_id)
            _S3_BLACKLIST_PATH.write_text(json.dumps(list(ids)))
        logger.info(f"Revoked S3 file_id: {file_id}")
    except Exception as e:
        logger.exception(f"Failed to revoke S3 file_id: {file_id} - {e}")
        raise FileRevocationError(f"Failed to revoke S3 file_id: {e}") from e


def is_s3_file_revoked(file_id: str) -> bool:
    """Check if a file_id is revoked for S3 URLs."""
    try:
        with _REVOCATION_LOCK:
            if not _S3_BLACKLIST_PATH.exists():
                logger.debug(
                    f"S3 blacklist file does not exist. file_id not revoked: {file_id}"
                )
                return False
            ids = set(json.loads(_S3_BLACKLIST_PATH.read_text()))
            revoked = file_id in ids
            logger.info(f"Checked S3 file_id revocation: {file_id} - revoked={revoked}")
            return revoked
    except Exception as e:
        logger.exception(f"Failed to check S3 file_id revocation: {file_id} - {e}")
        raise FileRevocationError(f"Failed to check S3 file_id revocation: {e}") from e
