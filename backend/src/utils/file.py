import asyncio
import base64
import bz2
import gzip
import hashlib
import hmac
import lzma
import os
import time
import urllib.parse
import zlib
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

import aioboto3
from botocore.exceptions import ClientError
from loguru import logger
from pydantic import BaseModel, Field

# If using src as PYTHONPATH
from src.core.config import settings
from src.core.secure_bytes import decrypt_bytes, encrypt_bytes

from .file_revocation import is_local_token_revoked

__all__ = [
    "FileStorage",
    "FileMetadata",
    "FileStorageError",
    "FileNotFoundError",
    "FileIntegrityError",
    "FileAccessLevel",
]


class FileAccessLevel(str, Enum):
    """Defines access levels for file URLs."""

    PRIVATE = "private"
    PUBLIC = "public"


# --- Error Types ---
class FileStorageError(Exception):
    """Base exception for file storage errors."""


class FileNotFoundError(FileStorageError):
    """Raised when a file is not found in storage."""


class FileIntegrityError(FileStorageError):
    """Raised when file integrity validation fails."""


# --- File Metadata Model ---
class FileMetadata(BaseModel):
    """Metadata describing a stored file."""

    file_id: str
    filename: str
    content_type: str
    size: int
    user_id: int | None = None
    checksum: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    storage_backend: str | None = None
    access_level: FileAccessLevel = FileAccessLevel.PRIVATE
    extra: dict[str, Any] = Field(default_factory=dict)


# --- File Storage Interface ---
class FileStorage(ABC):
    """
    Abstract base class for file storage backends.
    Provides a unified async interface for storing, retrieving, and managing files.
    """

    @abstractmethod
    async def store(
        self, file: bytes, filename: str, metadata: dict[str, Any]
    ) -> FileMetadata:
        """
        Store a file and return its metadata.
        :param file: File content as bytes.
        :param filename: Original filename.
        :param metadata: Additional metadata (user, tags, etc).
        :return: FileMetadata
        """
        raise NotImplementedError

    @abstractmethod
    async def retrieve(self, file_id: str) -> bytes:
        """
        Retrieve file content by file_id.
        :param file_id: Unique file identifier.
        :return: File content as bytes.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, file_id: str) -> None:
        """
        Delete a file by file_id.
        :param file_id: Unique file identifier.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_metadata(self, file_id: str) -> FileMetadata:
        """
        Get file metadata by file_id.
        :param file_id: Unique file identifier.
        :return: FileMetadata
        """
        raise NotImplementedError

    @abstractmethod
    async def generate_url(
        self, file_id: str, expires_in: int | None = None, public: bool = False
    ) -> str:
        """
        Generate a URL for accessing the file.
        :param file_id: Unique file identifier.
        :param expires_in: Expiry in seconds (optional).
        :param public: If True, generate a public URL.
        :return: URL as string.
        """
        raise NotImplementedError

    @abstractmethod
    async def validate_integrity(self, file_id: str) -> bool:
        """
        Validate file integrity (e.g., checksum).
        :param file_id: Unique file identifier.
        :return: True if valid, False otherwise.
        """
        raise NotImplementedError


def _get_hash(data: bytes, algo: str | None = None) -> str:
    """Compute hash of data using the configured or given algorithm."""
    import hashlib

    algo_str = str(algo or getattr(settings, "file_hash_algorithm", "sha256"))
    try:
        h = hashlib.new(algo_str)
    except Exception as e:
        logger.error(
            f"Unknown hash algorithm '{algo_str}': {e}. Falling back to sha256."
        )
        h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


# --- Local file access token helper ---
def _generate_file_token(
    file_id: str, user_id: str | None, expires_in: int = 3600
) -> str:
    """
    Generate a signed token for file access (HMAC, includes file_id, user_id, expiry).
    """
    secret = getattr(settings, "jwt_secret_key", "changeme")
    expiry = int(time.time()) + expires_in
    payload = f"{file_id}:{user_id or ''}:{expiry}"
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(
        f"{payload}:{base64.urlsafe_b64encode(sig).decode()}".encode()
    ).decode()
    return token


def _compress_data(
    data: bytes, algo: str | None, min_size: int = 0, level: int = 6
) -> tuple[bytes, str | None, int | None]:
    if not algo or len(data) < min_size:
        return data, None, None
    if algo == "gzip":
        return gzip.compress(data, compresslevel=level), "gzip", level
    if algo == "bz2":
        return bz2.compress(data, compresslevel=level), "bz2", level
    if algo == "lzma":
        return lzma.compress(data, preset=level), "lzma", level
    if algo == "zlib":
        return zlib.compress(data, level=level), "zlib", level
    return data, None, None


def _decompress_data(data: bytes, algo: str | None) -> bytes:
    if not algo:
        return data
    try:
        if algo == "gzip":
            return gzip.decompress(data)
        if algo == "bz2":
            return bz2.decompress(data)
        if algo == "lzma":
            return lzma.decompress(data)
        if algo == "zlib":
            return zlib.decompress(data)
        return data
    except Exception as e:
        logger.error(f"Decompression failed (algo={algo}): {e}")
        raise FileStorageError(
            f"Decompression failed for algorithm '{algo}': {e}"
        ) from e


CHUNK_SIZE = 1024 * 1024  # 1MB


def _stream_compress_to_file(
    data: bytes, algo: str, level: int, out_path: Path
) -> None:
    if algo == "gzip":
        import gzip

        with gzip.open(out_path, "wb", compresslevel=level) as f:
            for i in range(0, len(data), CHUNK_SIZE):
                f.write(data[i : i + CHUNK_SIZE])
    elif algo == "bz2":
        import bz2

        with bz2.BZ2File(out_path, "wb", compresslevel=level) as f:
            for i in range(0, len(data), CHUNK_SIZE):
                f.write(data[i : i + CHUNK_SIZE])
    elif algo == "lzma":
        import lzma

        with lzma.open(out_path, "wb", preset=level) as f:
            for i in range(0, len(data), CHUNK_SIZE):
                f.write(data[i : i + CHUNK_SIZE])
    elif algo == "zlib":
        import zlib

        with open(out_path, "wb") as f:
            cobj = zlib.compressobj(level)
            for i in range(0, len(data), CHUNK_SIZE):
                f.write(cobj.compress(data[i : i + CHUNK_SIZE]))
            f.write(cobj.flush())
    else:
        out_path.write_bytes(data)


def _stream_decompress_from_file(in_path: Path, algo: str) -> bytes:
    if algo == "gzip":
        import gzip

        with gzip.open(in_path, "rb") as f:
            return f.read()
    elif algo == "bz2":
        import bz2

        with bz2.BZ2File(in_path, "rb") as f:
            return f.read()
    elif algo == "lzma":
        import lzma

        with lzma.open(in_path, "rb") as f:
            return f.read()
    elif algo == "zlib":
        import zlib

        with open(in_path, "rb") as f:
            d = f.read()
            return zlib.decompress(d)
    else:
        return in_path.read_bytes()


class LocalFileStorage(FileStorage):
    """
    Local filesystem storage provider with atomic writes, compression, metadata sidecar, async locking, and more.
    """

    _locks: dict[str, asyncio.Lock] = {}

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = Path(base_dir or settings.upload_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.file_permissions = settings.file_permissions
        self.use_sidecar = settings.file_metadata_sidecar
        self.compression = settings.file_compression
        self.max_size = settings.file_max_size_mb * 1024 * 1024

    def _get_lock(self, file_id: str) -> asyncio.Lock:
        if file_id not in self._locks:
            self._locks[file_id] = asyncio.Lock()
        return self._locks[file_id]

    def _sanitize_filename(self, name: str) -> str:
        # Remove path separators and dangerous chars
        return os.path.basename(name).replace("..", "_")

    async def store(
        self, file: bytes, filename: str, metadata: dict[str, Any]
    ) -> FileMetadata:
        import aiofiles  # type: ignore

        user_id = metadata.get("user_id")
        if user_id is None:
            user_id = 0
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        subdir = self.base_dir / str(user_id) / date_str
        subdir.mkdir(parents=True, exist_ok=True)
        ext = Path(filename).suffix
        unique_id = str(uuid4())
        safe_name = self._sanitize_filename(f"{unique_id}{ext}")
        file_path = subdir / safe_name
        temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
        # Enforce file size limit
        if len(file) > self.max_size:
            logger.error(
                f"File too large: {
                    len(file)} bytes (limit {
                    self.max_size})",
                extra={"user_id": user_id, "file_id": unique_id, "action": "store"},
            )
            raise FileStorageError("File exceeds maximum allowed size")
        # Compression
        content_type = metadata.get("content_type", "application/octet-stream")
        compression_algo = self.compression if self.compression is not None else ""
        if _should_skip_compression(filename, content_type):
            compression_used = None
            level_used = None
        else:
            min_size = getattr(settings, "file_compression_min_size", 1024)
            level = getattr(settings, "file_compression_level", 6)
            use_stream = self.compression and len(file) > 1024 * 1024
            if use_stream:
                temp_path = Path(temp_path)
                _stream_compress_to_file(file, compression_algo, level, temp_path)
                async with aiofiles.open(temp_path, "rb") as f:
                    file = await f.read()
                temp_path.unlink(missing_ok=True)
                compression_used = self.compression
                level_used = level
            else:
                file, compression_used, level_used = _compress_data(
                    file, self.compression, min_size, level
                )
        # Encrypt file (placeholder)
        encrypted = encrypt_bytes(file)
        # Atomic async write to temp file
        lock = self._get_lock(unique_id)
        async with lock:
            try:
                async with aiofiles.open(temp_path, "wb") as f:
                    await f.write(encrypted)
                os.chmod(temp_path, self.file_permissions)
                os.replace(temp_path, file_path)  # atomic move
            except Exception as e:
                logger.exception(
                    f"Failed to store file {file_path}: {e}",
                    extra={"user_id": user_id, "file_id": unique_id, "action": "store"},
                )
                raise FileStorageError(f"Failed to store file: {e}") from e
        # Compute checksum
        checksum = _get_hash(file)
        size = len(file)
        logger.info(
            f"Stored file: {file_path} (user={user_id}, size={size}, checksum={checksum}, algo={
                settings.file_hash_algorithm})",
            extra={"user_id": user_id, "file_id": unique_id, "action": "store"},
        )
        # Metadata sidecar
        meta = FileMetadata(
            file_id=unique_id,
            filename=filename,
            content_type=metadata.get("content_type", "application/octet-stream"),
            size=size,
            user_id=int(user_id),
            checksum=checksum,
            created_at=now,
            updated_at=now,
            storage_backend="local",
            extra={
                "path": str(file_path),
                "hash_algorithm": settings.file_hash_algorithm,
                "compression": compression_used,
                "compression_level": level_used,
            },
        )
        if self.use_sidecar:
            sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
            async with aiofiles.open(sidecar_path, "w") as f:
                await f.write(meta.model_dump_json())
        return meta

    async def retrieve(self, file_id: str) -> bytes:
        import aiofiles

        file_path = self._find_file_path(file_id)
        if not file_path or not file_path.exists():
            logger.warning(
                f"File not found: {file_id}",
                extra={"file_id": file_id, "action": "retrieve"},
            )
            raise FileNotFoundError(f"File not found: {file_id}")
        lock = self._get_lock(file_id)
        try:
            async with lock:
                async with aiofiles.open(file_path, "rb") as f:
                    encrypted = await f.read()
                data = decrypt_bytes(encrypted)
                # Always check for compression in metadata if sidecar is used
                compression_used = self.compression
                if self.use_sidecar:
                    sidecar_path = file_path.with_suffix(
                        file_path.suffix + ".meta.json"
                    )
                    if sidecar_path.exists():
                        import aiofiles

                        async with aiofiles.open(sidecar_path) as f:
                            meta = FileMetadata.model_validate_json(await f.read())
                        compression_used = meta.extra.get(
                            "compression", self.compression
                        )
                use_stream = compression_used and file_path.stat().st_size > 1024 * 1024
                if use_stream:
                    # Write encrypted to temp, decrypt, then decompress from
                    # temp
                    temp_path = file_path.with_suffix(file_path.suffix + ".decrypted")
                    async with aiofiles.open(temp_path, "wb") as f:
                        await f.write(data)
                    if compression_used:
                        data = _stream_decompress_from_file(temp_path, compression_used)
                    else:
                        data = temp_path.read_bytes()
                    temp_path.unlink(missing_ok=True)
                else:
                    data = _decompress_data(data, compression_used)
        except FileStorageError as e:
            logger.error(
                f"Decompression error for file {file_id}: {e}",
                extra={"file_id": file_id, "action": "retrieve"},
            )
            raise
        except Exception as e:
            logger.exception(
                f"Failed to retrieve file {file_id}: {e}",
                extra={"file_id": file_id, "action": "retrieve"},
            )
            raise FileStorageError(f"Failed to retrieve file: {e}") from e
        if getattr(settings, "file_integrity_autovalidate", False):
            try:
                await self.validate_integrity(file_id, data=data)
            except FileIntegrityError as e:
                logger.error(
                    f"Integrity check failed on retrieve for {file_id}: {e}",
                    extra={"file_id": file_id, "action": "retrieve"},
                )
                # Quarantine if configured
                qdir = getattr(settings, "file_integrity_quarantine_dir", None)
                if qdir:
                    import shutil

                    qpath = Path(qdir) / file_path.name
                    shutil.move(str(file_path), str(qpath))
                    logger.warning(
                        f"File {file_id} moved to quarantine: {qpath}",
                        extra={"file_id": file_id, "action": "quarantine"},
                    )
                raise
        logger.info(
            f"Retrieved file: {file_path}",
            extra={"file_id": file_id, "action": "retrieve"},
        )
        return data

    async def delete(self, file_id: str) -> None:
        file_path = self._find_file_path(file_id)
        if not file_path or not file_path.exists():
            logger.warning(
                f"File not found for delete: {file_id}",
                extra={"file_id": file_id, "action": "delete"},
            )
            raise FileNotFoundError(f"File not found: {file_id}")
        lock = self._get_lock(file_id)
        async with lock:
            try:
                file_path.unlink()
                if self.use_sidecar:
                    sidecar_path = file_path.with_suffix(
                        file_path.suffix + ".meta.json"
                    )
                    if sidecar_path.exists():
                        sidecar_path.unlink()
                logger.info(
                    f"Deleted file: {file_path}",
                    extra={"file_id": file_id, "action": "delete"},
                )
            except Exception as e:
                logger.exception(
                    f"Failed to delete file {file_id}: {e}",
                    extra={"file_id": file_id, "action": "delete"},
                )
                raise FileStorageError(f"Failed to delete file: {e}") from e

    async def get_metadata(self, file_id: str) -> FileMetadata:
        file_path = self._find_file_path(file_id)
        if not file_path or not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_id}")
        if self.use_sidecar:
            sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
            if sidecar_path.exists():
                import aiofiles

                async with aiofiles.open(sidecar_path) as f:
                    data = await f.read()
                return FileMetadata.model_validate_json(data)
        stat = file_path.stat()
        try:
            user_id = int(file_path.parent.parent.name)
            date_str = file_path.parent.name
            created_at = datetime.strptime(date_str, "%Y%m%d")
        except Exception:
            user_id = None
            created_at = None
        return FileMetadata(
            file_id=file_id,
            filename=file_path.name,
            content_type="application/octet-stream",
            size=stat.st_size,
            user_id=user_id,
            checksum=None,  # Not stored on disk; use validate_integrity
            created_at=created_at,
            updated_at=datetime.fromtimestamp(stat.st_mtime),
            storage_backend="local",
            extra={"path": str(file_path)},
        )

    async def generate_url(
        self,
        file_id: str,
        expires_in: int | None = None,
        public: bool = False,
        user_id: str | None = None,
    ) -> str:
        """
        Generate a secure, app-served URL for a file.
        If not public, appends a signed token for access control.
        Ensures proper escaping.
        """
        max_expiry = getattr(settings, "file_url_max_expiry", 86400)
        actual_expiry = min(expires_in or 3600, max_expiry)
        safe_id = urllib.parse.quote(str(file_id), safe="")
        url_path = f"/files/{safe_id}"
        base = getattr(settings, "file_url_base", None)
        url = f"{base.rstrip('/')}" + url_path if base else url_path
        if not public:
            token = _generate_file_token(file_id, user_id, actual_expiry)
            url += f"?token={urllib.parse.quote(token)}"
        # Check if file_id is revoked (for future: token revocation is checked
        # at endpoint)
        if is_local_token_revoked(file_id):
            logger.warning(
                f"Attempt to generate URL for revoked local file_id/token: {file_id}",
                extra={
                    "file_id": file_id,
                    "user_id": user_id,
                    "action": "generate_url",
                },
            )
            raise FileStorageError("This file or token has been revoked.")
        logger.info(
            f"Generated URL for file {file_id}: {url} (public={public}, expiry={actual_expiry}, user_id={user_id})",
            extra={"file_id": file_id, "user_id": user_id, "action": "generate_url"},
        )
        return url

    async def validate_integrity(self, file_id: str, data: bytes | None = None) -> bool:
        import aiofiles

        file_path = self._find_file_path(file_id)
        if not file_path or not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_id}")
        lock = self._get_lock(file_id)
        async with lock:
            if data is None:
                async with aiofiles.open(file_path, "rb") as f:
                    encrypted = await f.read()
                data = decrypt_bytes(encrypted)
                if self.compression == "gzip":
                    data = gzip.decompress(data)
            checksum = _get_hash(data)
            # Compare with sidecar if available
            if self.use_sidecar:
                sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
                if sidecar_path.exists():
                    async with aiofiles.open(sidecar_path) as f:
                        meta = FileMetadata.model_validate_json(await f.read())
                    if meta.checksum and meta.checksum != checksum:
                        logger.error(
                            f"Checksum mismatch for {file_id}: expected {meta.checksum}, got {checksum}",
                            extra={"file_id": file_id, "action": "validate_integrity"},
                        )
                        raise FileIntegrityError(
                            f"Checksum mismatch: expected {meta.checksum}, got {checksum}"
                        )
            logger.info(
                f"Validated integrity for file {file_id}: {checksum} (algo={settings.file_hash_algorithm})",
                extra={"file_id": file_id, "action": "validate_integrity"},
            )
            return True

    def _find_file_path(self, file_id: str) -> Path | None:
        for dirpath, _, filenames in os.walk(self.base_dir):
            for fname in filenames:
                if fname.startswith(file_id) and not fname.endswith(".meta.json"):
                    return Path(dirpath) / fname
        return None


try:
    from botocore.exceptions import (
        EndpointConnectionError,
        NoCredentialsError,
    )
except ImportError:
    NoCredentialsError = EndpointConnectionError = (
        Exception  # fallback for type checkers
    )


class S3FileStorage(FileStorage):
    """
    S3-compatible async file storage provider using aioboto3.
    Features:
      - Presigned URLs, server-side encryption (SSE/KMS), retry logic with backoff, logging
      - Stores SHA256 checksum and custom metadata in S3 object metadata
      - Validates integrity on retrieval
      - Uses multipart upload for files >5MB
    """

    def __init__(self) -> None:
        self.bucket: str = settings.s3_bucket or ""
        self.prefix: str = (settings.s3_prefix or "").rstrip("/")
        self.acl: str = settings.s3_acl or "private"
        self.sse: str | None = getattr(settings, "s3_server_side_encryption", None)
        self.sse_kms_key_id: str | None = getattr(settings, "s3_kms_key_id", None)
        self.region: str | None = getattr(settings, "s3_region", None)
        self.endpoint_url: str | None = getattr(settings, "s3_endpoint_url", None)
        self.access_key: str | None = getattr(settings, "s3_access_key_id", None)
        self.secret_key: str | None = getattr(settings, "s3_secret_access_key", None)
        if not self.bucket:
            raise RuntimeError("S3 bucket not configured")

    def _object_key(self, file_id: str, filename: str = "") -> str:
        fname = filename or "file"
        key = (
            f"{self.prefix}/{file_id}_{fname}" if self.prefix else f"{file_id}_{fname}"
        )
        return key

    def _get_session(self) -> aioboto3.Session:
        return aioboto3.Session()

    async def _retry(
        self, func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any
    ) -> Any:
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                return await func(*args, **kwargs)
            except (ClientError, NoCredentialsError, EndpointConnectionError) as e:
                logger.warning(
                    f"S3 operation failed (attempt {attempt + 1}): {e}",
                    extra={"action": "s3_retry", "attempt": attempt + 1},
                )
                if attempt == max_attempts - 1:
                    raise FileStorageError(f"S3 operation failed: {e}") from e

    async def store(
        self, file: bytes, filename: str, metadata: dict[str, Any]
    ) -> FileMetadata:
        session = self._get_session()
        file_id = str(uuid4())
        key = self._object_key(file_id, filename)
        checksum = _get_hash(file)
        user_id = metadata.get("user_id")
        # Compression
        content_type = metadata.get("content_type", "application/octet-stream")
        if _should_skip_compression(filename, content_type):
            compression_used = None
            level_used = None
        else:
            min_size = getattr(settings, "file_compression_min_size", 1024)
            level = getattr(settings, "file_compression_level", 6)
            file, compression_used, level_used = _compress_data(
                file, getattr(settings, "file_compression", None), min_size, level
            )
        extra_args = {
            "ACL": self.acl,
            "Metadata": {
                "checksum": checksum,
                "user_id": str(user_id or ""),
                "orig_filename": filename,
                "hash_algorithm": getattr(settings, "file_hash_algorithm", "sha256"),
                "compression": compression_used or "",
                "compression_level": str(level_used or ""),
            },
        }
        if self.sse:
            extra_args["ServerSideEncryption"] = self.sse
        if self.sse_kms_key_id:
            extra_args["SSEKMSKeyId"] = self.sse_kms_key_id
        content_type = metadata.get("content_type", "application/octet-stream")

        async def _upload() -> None:
            async with session.client(
                "s3",
                region_name=self.region,
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            ) as s3:
                if len(file) > 5 * 1024 * 1024:
                    # Multipart upload
                    mp = await s3.create_multipart_upload(
                        Bucket=self.bucket,
                        Key=key,
                        ContentType=content_type,
                        **extra_args,
                    )
                    upload_id = mp["UploadId"]
                    try:
                        part = await s3.upload_part(
                            Bucket=self.bucket,
                            Key=key,
                            PartNumber=1,
                            UploadId=upload_id,
                            Body=file,
                        )
                        await s3.complete_multipart_upload(
                            Bucket=self.bucket,
                            Key=key,
                            UploadId=upload_id,
                            MultipartUpload={
                                "Parts": [{"ETag": part["ETag"], "PartNumber": 1}]
                            },
                        )
                    except Exception as e:
                        await s3.abort_multipart_upload(
                            Bucket=self.bucket, Key=key, UploadId=upload_id
                        )
                        logger.exception(
                            f"Multipart upload failed for S3 file: {key} (user_id={user_id}): {e}",
                            extra={
                                "file_id": key,
                                "user_id": user_id,
                                "action": "store",
                            },
                        )
                        raise FileStorageError(f"Multipart upload failed: {e}") from e
                else:
                    await s3.put_object(
                        Bucket=self.bucket,
                        Key=key,
                        Body=file,
                        ContentType=content_type,
                        **extra_args,
                    )
            logger.info(
                f"Stored file in S3: {key} (bucket={
                    self.bucket}, user_id={user_id})",
                extra={"file_id": key, "user_id": user_id, "action": "store"},
            )

        await self._retry(_upload)
        now = datetime.now()
        return FileMetadata(
            file_id=key,
            filename=filename,
            content_type=content_type,
            size=len(file),
            user_id=user_id,
            checksum=checksum,
            created_at=now,
            updated_at=now,
            storage_backend="s3",
            extra={
                "bucket": self.bucket,
                "key": key,
                "hash_algorithm": getattr(settings, "file_hash_algorithm", "sha256"),
                "compression": compression_used,
                "compression_level": level_used,
            },
        )

    async def retrieve(self, file_id: str) -> bytes:
        session = self._get_session()

        async def _get() -> bytes:
            async with session.client(
                "s3",
                region_name=self.region,
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            ) as s3:
                try:
                    resp = await s3.get_object(Bucket=self.bucket, Key=file_id)
                except Exception as e:
                    logger.warning(
                        f"S3 file not found or get_object failed: {file_id} - {e}",
                        extra={"file_id": file_id, "action": "retrieve"},
                    )
                    raise FileNotFoundError(f"S3 file not found: {file_id}") from e
                data = await resp["Body"].read()
                meta = resp.get("Metadata", {})
                compression_used = meta.get("compression")
                data = _decompress_data(data, compression_used)
                checksum = meta.get("checksum")
                algo = meta.get(
                    "hash_algorithm", getattr(settings, "file_hash_algorithm", "sha256")
                )
                actual = _get_hash(data, algo)
                if getattr(settings, "file_integrity_autovalidate", False):
                    if checksum and actual != checksum:
                        logger.error(
                            f"Checksum mismatch for {file_id}: expected {checksum}, got {actual}",
                            extra={"file_id": file_id, "action": "validate_integrity"},
                        )
                        qdir = getattr(settings, "file_integrity_quarantine_dir", None)
                        if qdir:
                            logger.warning(
                                f"File {file_id} failed integrity and should be quarantined (manual step): {qdir}",
                                extra={"file_id": file_id, "action": "quarantine"},
                            )
                        raise FileIntegrityError(
                            f"Checksum mismatch: expected {checksum}, got {actual}"
                        )
                logger.info(
                    f"Retrieved file from S3: {file_id}",
                    extra={"file_id": file_id, "action": "retrieve"},
                )
                return data

        try:
            result = await self._retry(_get)
            assert isinstance(result, bytes)
            return result
        except FileStorageError as e:
            logger.error(
                f"Decompression error for S3 file {file_id}: {e}",
                extra={"file_id": file_id, "action": "retrieve"},
            )
            raise


def _should_skip_compression(filename: str, content_type: str) -> bool:
    """Return True if the file should not be compressed (already compressed or binary)."""
    compressed_exts = {
        ".zip",
        ".gz",
        ".bz2",
        ".xz",
        ".lzma",
        ".rar",
        ".7z",
        ".tar",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".mp4",
        ".mp3",
        ".avi",
        ".mov",
        ".pdf",
        ".webp",
        ".ogg",
        ".mkv",
    }
    compressed_types = {
        "application/zip",
        "application/gzip",
        "application/x-bzip2",
        "application/x-xz",
        "application/x-lzma",
        "application/x-rar-compressed",
        "application/x-7z-compressed",
        "application/x-tar",
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "video/mp4",
        "video/x-matroska",
        "video/ogg",
        "audio/ogg",
        "audio/mpeg",
        "video/quicktime",
        "application/pdf",
    }
    ext = Path(filename).suffix.lower()
    if ext in compressed_exts:
        return True
    if content_type and content_type.lower() in compressed_types:
        return True
    return False
