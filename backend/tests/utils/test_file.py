import os
import tempfile
import types
from datetime import datetime
from pathlib import Path
from unittest import mock
from typing import Any, Awaitable, Callable, cast

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.utils import file as file_utils
from src.utils.file import (
    FileAccessLevel,
    FileIntegrityError,
    FileMetadata,
    FileNotFoundError,
    FileStorageError,
    LocalFileStorage,
    S3FileStorage,
    _compress_data,
    _decompress_data,
    _generate_file_token,
    _get_hash,
    _should_skip_compression,
    _stream_compress_to_file,
    _stream_decompress_from_file,
)


def compress_side_effect(d: bytes) -> tuple[bytes, None, None]:
    return (d, None, None)


class DummySettings:
    upload_dir = tempfile.mkdtemp()
    file_permissions = 0o600
    file_metadata_sidecar = True
    file_compression = "gzip"
    file_max_size_mb = 1
    file_hash_algorithm = "sha256"
    file_compression_min_size = 1
    file_compression_level = 6
    file_url_max_expiry = 86400
    file_url_base = None
    jwt_secret_key = "testsecret"
    file_integrity_autovalidate = False
    file_integrity_quarantine_dir = tempfile.mkdtemp()


# Patch settings for tests
file_utils.settings = DummySettings()  # type: ignore


@pytest.mark.asyncio
class TestLocalFileStorage:
    @pytest.fixture(autouse=True)
    def setup_storage(self, tmp_path: Path) -> None:
        self.storage = LocalFileStorage(base_dir=tmp_path)
        self.tmp_path = tmp_path

    @pytest.mark.asyncio
    async def test_store_and_retrieve(self) -> None:
        data = b"hello world"
        meta = await self.storage.store(
            data, "test.txt", {"user_id": 1, "content_type": "text/plain"}
        )
        assert meta.filename == "test.txt"
        assert meta.size > 0
        retrieved = await self.storage.retrieve(meta.file_id)
        assert retrieved == data

    @pytest.mark.asyncio
    async def test_store_too_large(self) -> None:
        data = b"x" * (self.storage.max_size + 1)
        with pytest.raises(FileStorageError):
            await self.storage.store(data, "big.txt", {"user_id": 1})

    @pytest.mark.asyncio
    async def test_delete(self) -> None:
        data = b"bye"
        meta = await self.storage.store(data, "bye.txt", {"user_id": 2})
        await self.storage.delete(meta.file_id)
        with pytest.raises(FileNotFoundError):
            await self.storage.retrieve(meta.file_id)

    @pytest.mark.asyncio
    async def test_get_metadata(self) -> None:
        data = b"meta"
        meta = await self.storage.store(data, "meta.txt", {"user_id": 3})
        meta2 = await self.storage.get_metadata(meta.file_id)
        assert meta2.file_id == meta.file_id
        assert meta2.filename == "meta.txt"
        assert meta2.size == meta.size

    @pytest.mark.asyncio
    async def test_generate_url_private_and_public(self) -> None:
        data = b"urltest"
        meta = await self.storage.store(data, "url.txt", {"user_id": 4})
        url = await self.storage.generate_url(
            meta.file_id, expires_in=100, public=False, user_id="4"
        )
        assert url.startswith("/files/")
        assert "token=" in url
        url2 = await self.storage.generate_url(
            meta.file_id, expires_in=100, public=True
        )
        assert url2.startswith("/files/")
        assert "token=" not in url2

    @pytest.mark.asyncio
    async def test_validate_integrity(self) -> None:
        data = b"integrity"
        meta = await self.storage.store(
            data, "integrity.txt", {"user_id": 5, "original_data": data}
        )
        assert await self.storage.validate_integrity(meta.file_id)

    @pytest.mark.asyncio
    async def test_retrieve_nonexistent(self) -> None:
        with pytest.raises(FileNotFoundError):
            await self.storage.retrieve("nonexistent")

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self) -> None:
        with pytest.raises(FileNotFoundError):
            await self.storage.delete("nonexistent")

    @pytest.mark.asyncio
    async def test_get_metadata_nonexistent(self) -> None:
        with pytest.raises(FileNotFoundError):
            await self.storage.get_metadata("nonexistent")

    @pytest.mark.asyncio
    async def test_integrity_fail(self) -> None:
        data = b"failintegrity"
        meta = await self.storage.store(data, "fail.txt", {"user_id": 6})
        # Corrupt the file
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        file_path.write_bytes(b"corrupted")
        with pytest.raises(FileIntegrityError):
            await self.storage.validate_integrity(meta.file_id)

    @pytest.mark.asyncio
    async def test_sidecar_metadata(self) -> None:
        data = b"sidecar"
        meta = await self.storage.store(data, "sidecar.txt", {"user_id": 7})
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        sidecar = file_path.with_suffix(file_path.suffix + ".meta.json")
        assert sidecar.exists()

    @pytest.mark.asyncio
    async def test_compression_and_decompression(self) -> None:
        data = b"A" * 2048
        meta = await self.storage.store(data, "compress.txt", {"user_id": 8})
        retrieved = await self.storage.retrieve(meta.file_id)
        assert retrieved == data

    @pytest.mark.asyncio
    async def test_stream_compress_and_decompress(self) -> None:
        data = b"B" * (1 * 1024 * 1024)  # 1MB, within max_size
        meta = await self.storage.store(
            data, "stream.txt", {"user_id": 9, "original_data": data}
        )
        retrieved = await self.storage.retrieve(meta.file_id)
        assert retrieved == data

    @pytest.mark.asyncio
    async def test_should_skip_compression(self) -> None:
        assert _should_skip_compression("file.jpg", "image/jpeg")
        assert not _should_skip_compression("file.txt", "text/plain")

    @pytest.mark.asyncio
    async def test_generate_file_token(self) -> None:
        token = _generate_file_token("fileid", "userid", 60)
        assert isinstance(token, str)

    @pytest.mark.asyncio
    async def test_get_hash(self) -> None:
        h = _get_hash(b"abc", "sha256")
        assert isinstance(h, str)
        h2 = _get_hash(b"abc", "md5")
        assert isinstance(h2, str)

    @pytest.mark.asyncio
    async def test_get_hash_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Patch logger to capture error
        errors = []

        def fake_error(msg: str, **kwargs: object) -> None:
            errors.append(msg)

        monkeypatch.setattr(file_utils.logger, "error", fake_error)
        # Should fallback to sha256 if algo is invalid
        data = b"abc"
        result = _get_hash(data, algo="notarealhash")
        assert isinstance(result, str)
        assert len(result) == 64  # sha256 hex length
        assert errors and "Unknown hash algorithm" in errors[0]

    @pytest.mark.asyncio
    async def test_compress_and_decompress_data(self) -> None:
        data = b"C" * 2048
        for algo in ["gzip", "bz2", "lzma", "zlib"]:
            compressed, used, level = _compress_data(data, algo, min_size=1, level=6)
            assert used == algo
            decompressed = _decompress_data(compressed, algo)
            assert decompressed == data
        # No compression
        out, used, level = _compress_data(data, None)
        assert out == data
        assert used is None
        assert level is None
        # Decompress with None
        assert _decompress_data(data, None) == data

    @pytest.mark.asyncio
    async def test_stream_compress_to_file_and_decompress(self) -> None:
        data = b"D" * (2 * 1024 * 1024)
        for algo in ["gzip", "bz2", "lzma", "zlib"]:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = Path(tmpdir) / f"test.{algo}"
                _stream_compress_to_file(data, algo, 6, out_path)
                decompressed = _stream_decompress_from_file(out_path, algo)
                assert decompressed == data
        # No compression
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "test.raw"
            _stream_compress_to_file(data, "none", 6, out_path)
            assert out_path.read_bytes() == data

    @pytest.mark.asyncio
    async def test_find_file_path(self) -> None:
        data = b"findme"
        meta = await self.storage.store(data, "findme.txt", {"user_id": 10})
        path = self.storage._find_file_path(meta.file_id)
        assert path is not None

    @pytest.mark.asyncio
    async def test_file_access_level_enum(self) -> None:
        assert FileAccessLevel.PRIVATE == "private"
        assert FileAccessLevel.PUBLIC == "public"

    @pytest.mark.asyncio
    async def test_file_metadata_model(self) -> None:
        now = datetime.now()
        meta = FileMetadata(
            file_id="id1",
            filename="f.txt",
            content_type="text/plain",
            size=123,
            user_id=1,
            checksum="abc",
            created_at=now,
            updated_at=now,
            storage_backend="local",
            access_level=FileAccessLevel.PRIVATE,
            extra={"foo": "bar"},
        )
        assert meta.file_id == "id1"
        assert meta.filename == "f.txt"
        assert meta.content_type == "text/plain"
        assert meta.size == 123
        assert meta.user_id == 1
        assert meta.checksum == "abc"
        assert meta.created_at == now
        assert meta.updated_at == now
        assert meta.storage_backend == "local"
        assert meta.access_level == FileAccessLevel.PRIVATE
        assert meta.extra["foo"] == "bar"

    @pytest.mark.asyncio
    async def test_file_storage_error_types(self) -> None:
        assert issubclass(FileStorageError, Exception)
        assert issubclass(FileNotFoundError, FileStorageError)
        assert issubclass(FileIntegrityError, FileStorageError)

    @pytest.mark.asyncio
    async def test_store_with_no_user_id(self) -> None:
        data = b"no user id"
        meta = await self.storage.store(data, "nouser.txt", {})
        assert meta.user_id == 0

    @pytest.mark.asyncio
    async def test_store_with_various_extensions(self) -> None:
        for ext in [".txt", ".jpg", ".tar.gz", ".weird"]:
            data = b"data" + ext.encode()
            meta = await self.storage.store(data, f"file{ext}", {"user_id": 11})
            assert meta.filename.endswith(ext)

    @pytest.mark.asyncio
    async def test_store_and_retrieve_with_sidecar_disabled(self) -> None:
        self.storage.use_sidecar = False
        data = b"sidecar off"
        meta = await self.storage.store(data, "nosidecar.txt", {"user_id": 12})
        retrieved = await self.storage.retrieve(meta.file_id)
        assert retrieved == data
        self.storage.use_sidecar = True

    @pytest.mark.asyncio
    async def test_generate_url_max_expiry(self) -> None:
        data = b"expiry"
        meta = await self.storage.store(data, "expiry.txt", {"user_id": 13})
        url = await self.storage.generate_url(
            meta.file_id, expires_in=999999, public=False, user_id="13"
        )
        assert "token=" in url

    @pytest.mark.asyncio
    async def test_generate_url_revoked(self, monkeypatch: MonkeyPatch) -> None:
        data = b"revoked"
        meta = await self.storage.store(data, "revoked.txt", {"user_id": 14})
        monkeypatch.setattr(file_utils, "is_local_token_revoked", lambda file_id: True)
        with pytest.raises(FileStorageError):
            await self.storage.generate_url(meta.file_id, public=False, user_id="14")
        monkeypatch.setattr(file_utils, "is_local_token_revoked", lambda file_id: False)

    @pytest.mark.asyncio
    async def test_find_file_path_returns_none(self) -> None:
        assert self.storage._find_file_path("notarealfileid") is None

    @pytest.mark.asyncio
    async def test_sanitize_filename(self) -> None:
        bad_name = "../../evil.txt"
        sanitized = self.storage._sanitize_filename(bad_name)
        assert ".." not in sanitized
        assert os.path.basename(sanitized) == sanitized

    @pytest.mark.asyncio
    async def test_stream_decompress_from_file_no_algo(self) -> None:
        data = b"plain data"
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "plain.txt"
            out_path.write_bytes(data)
            result = _stream_decompress_from_file(out_path, "none")
            assert result == data

    @pytest.mark.asyncio
    async def test_decompress_data_invalid_algo(self) -> None:
        data = b"not compressed"
        with pytest.raises(FileStorageError):
            _decompress_data(data, "invalid_algo")

    @pytest.mark.asyncio
    async def test_stream_compress_to_file_invalid_algo(self) -> None:
        data = b"data"
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "invalid"
            _stream_compress_to_file(data, "invalid_algo", 6, out_path)
            assert out_path.read_bytes() == data

    @pytest.mark.asyncio
    async def test_stream_decompress_from_file_invalid_algo(self) -> None:
        data = b"data"
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "invalid"
            out_path.write_bytes(data)
            result = _stream_decompress_from_file(out_path, "invalid_algo")
            assert result == data

    @pytest.mark.asyncio
    async def test_file_metadata_extra_fields(self) -> None:
        now = datetime.now()
        meta = FileMetadata(
            file_id="id2",
            filename="f2.txt",
            content_type="text/plain",
            size=456,
            user_id=2,
            checksum="def",
            created_at=now,
            updated_at=now,
            storage_backend="local",
            access_level=FileAccessLevel.PUBLIC,
            extra={"bar": "baz", "num": 123},
        )
        assert meta.extra["bar"] == "baz"
        assert meta.extra["num"] == 123

    @pytest.mark.asyncio
    async def test_file_metadata_default_values(self) -> None:
        meta = FileMetadata(
            file_id="id3",
            filename="f3.txt",
            content_type="text/plain",
            size=789,
        )
        assert meta.access_level == FileAccessLevel.PRIVATE
        assert isinstance(meta.extra, dict)

    @pytest.mark.asyncio
    async def test_file_access_level_enum_str(self) -> None:
        assert FileAccessLevel.PRIVATE.value == "private"
        assert FileAccessLevel.PUBLIC.value == "public"

    @pytest.mark.asyncio
    async def test_file_storage_error_str(self) -> None:
        err = FileStorageError("errormsg")
        assert str(err) == "errormsg"
        err2 = FileNotFoundError("notfound")
        assert str(err2) == "notfound"
        err3 = FileIntegrityError("badintegrity")
        assert str(err3) == "badintegrity"

    @pytest.mark.asyncio
    async def test_store_os_errors(self, monkeypatch: MonkeyPatch) -> None:
        data = b"failme"
        # Patch aiofiles.open to work, but os.chmod to fail
        await self.storage.store(b"ok", "ok.txt", {"user_id": 1})
        monkeypatch.setattr(
            os,
            "chmod",
            lambda *a, **kw: (_ for _ in ()).throw(PermissionError("fail chmod")),
        )
        with pytest.raises(FileStorageError) as excinfo:
            await self.storage.store(data, "failchmod.txt", {"user_id": 1})
        assert "Failed to store file" in str(excinfo.value)

        # Patch os.replace to fail
        def fail_replace(*a: object, **kw: object) -> None:
            raise OSError("fail replace")

        monkeypatch.setattr(os, "replace", fail_replace)
        with pytest.raises(FileStorageError) as excinfo:
            await self.storage.store(data, "failreplace.txt", {"user_id": 1})
        assert "Failed to store file" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_retrieve_decompression_failure(self, monkeypatch: MonkeyPatch) -> None:
        data = b"faildecompress"
        meta = await self.storage.store(data, "fail.gz", {"user_id": 1})
        # Patch _decompress_data to raise FileStorageError
        monkeypatch.setattr(
            file_utils,
            "_decompress_data",
            lambda d, c: (_ for _ in ()).throw(
                file_utils.FileStorageError("decomp fail")
            ),
        )
        # Patch settings to trigger decompression
        file_utils.settings.file_compression = "gzip"
        with pytest.raises(file_utils.FileStorageError) as excinfo:
            await self.storage.retrieve(meta.file_id)
        assert "decomp fail" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_integrity_quarantine(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
        # Store a file
        data = b"quarantine_test"
        self.storage.use_sidecar = False
        meta = await self.storage.store(data, "quarantine.txt", {"user_id": 1})
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        # Decrypt, decompress, tamper, recompress, re-encrypt
        import gzip

        from src.core.secure_bytes import decrypt_bytes, encrypt_bytes

        encrypted = file_path.read_bytes()
        decrypted = decrypt_bytes(encrypted)
        decompressed = gzip.decompress(decrypted)
        tampered = decompressed + b"tamper"
        recompressed = gzip.compress(tampered)
        file_path.write_bytes(encrypt_bytes(recompressed))
        # Enable integrity autovalidate and set quarantine dir
        file_utils.settings.file_integrity_autovalidate = True
        quarantine_dir = tmp_path / "quarantine"
        quarantine_dir.mkdir()
        file_utils.settings.file_integrity_quarantine_dir = str(quarantine_dir)
        # Patch logger to ensure warning is called
        called = {}

        def fake_warning(msg: str, *args: object, **kwargs: object) -> object:
            called["warned"] = True
            return file_utils.logger.opt(depth=1).info(msg)

        monkeypatch.setattr(file_utils.logger, "warning", fake_warning)
        # Attempt to retrieve, should move to quarantine and raise error
        with pytest.raises(FileIntegrityError):
            await self.storage.retrieve(meta.file_id)
        # File should be in quarantine and logger should be called
        assert file_path is not None
        assert (quarantine_dir / file_path.name).exists()
        assert called.get("warned")
        # Reset settings
        file_utils.settings.file_integrity_autovalidate = False
        self.storage.use_sidecar = True
        file_utils.settings.file_integrity_quarantine_dir = tempfile.mkdtemp()

    @pytest.mark.asyncio
    async def test_integrity_quarantine_no_dir(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
        # Store a file
        data = b"quarantine_test"
        self.storage.use_sidecar = False
        meta = await self.storage.store(data, "quarantine.txt", {"user_id": 1})
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        # Decrypt, decompress, tamper, recompress, re-encrypt
        import gzip

        from src.core.secure_bytes import decrypt_bytes, encrypt_bytes

        encrypted = file_path.read_bytes()
        decrypted = decrypt_bytes(encrypted)
        decompressed = gzip.decompress(decrypted)
        tampered = decompressed + b"tamper"
        recompressed = gzip.compress(tampered)
        file_path.write_bytes(encrypt_bytes(recompressed))
        # Enable integrity autovalidate and UNSET quarantine dir
        file_utils.settings.file_integrity_autovalidate = True
        file_utils.settings.file_integrity_quarantine_dir = None
        # Patch logger to ensure warning is NOT called
        called = {}

        def fake_warning(msg: str, *args: object, **kwargs: object) -> object:
            called["warned"] = True
            return file_utils.logger.opt(depth=1).info(msg)

        monkeypatch.setattr(file_utils.logger, "warning", fake_warning)
        # Attempt to retrieve, should NOT move to quarantine but should raise error
        with pytest.raises(FileIntegrityError):
            await self.storage.retrieve(meta.file_id)
        # File should NOT be in quarantine and logger should NOT be called
        assert not called.get("warned")
        # Reset settings
        file_utils.settings.file_integrity_autovalidate = False
        self.storage.use_sidecar = True
        # Optionally restore quarantine_dir if needed for other tests
        file_utils.settings.file_integrity_quarantine_dir = tempfile.mkdtemp()

    @pytest.mark.asyncio
    async def test_compress_data_unknown_algo(self) -> None:
        data = b"abc"
        out, comp, lvl = _compress_data(data, algo="notarealalgo", min_size=1, level=6)
        assert out == data
        assert comp is None
        assert lvl is None

    @pytest.mark.asyncio
    async def test_store_stream_compression(self) -> None:
        # Make a file just over 1MB
        data = b"a" * (1024 * 1024 + 1)
        self.storage.compression = "gzip"
        old_max = self.storage.max_size
        self.storage.max_size = 2 * 1024 * 1024  # 2MB
        try:
            meta = await self.storage.store(data, "bigfile.txt", {"user_id": 1})
            assert meta.size > 0
            retrieved = await self.storage.retrieve(meta.file_id)
            assert retrieved == data
        finally:
            self.storage.max_size = old_max

    @pytest.mark.asyncio
    async def test_retrieve_stream_decompression_with_sidecar(self) -> None:
        # Store a file >1MB with compression and sidecar enabled
        data = b"Z" * (1024 * 1024 + 100)
        self.storage.compression = "gzip"
        self.storage.use_sidecar = True
        old_max = self.storage.max_size
        self.storage.max_size = 2 * 1024 * 1024
        try:
            meta = await self.storage.store(data, "bigsidecar2.txt", {"user_id": 1})
            # Confirm sidecar exists
            file_path = self.storage._find_file_path(meta.file_id)
            assert file_path is not None
            sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
            assert sidecar_path.exists()
            # Retrieve and check content (should use streaming decompression with sidecar)
            retrieved = await self.storage.retrieve(meta.file_id)
            assert retrieved == data
        finally:
            self.storage.max_size = old_max

    @pytest.mark.asyncio
    async def test_retrieve_stream_decompression_with_sidecar_full_coverage(self) -> None:
        # Use random data to ensure compression does not shrink file below 1MB
        import os

        data = os.urandom(1024 * 1024 + 100)
        self.storage.compression = "gzip"
        self.storage.use_sidecar = True
        old_max = self.storage.max_size
        self.storage.max_size = 2 * 1024 * 1024
        try:
            meta = await self.storage.store(data, "bigsidecar2.txt", {"user_id": 1})
            # Confirm sidecar exists
            file_path = self.storage._find_file_path(meta.file_id)
            assert file_path is not None
            sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
            assert sidecar_path.exists()
            # Retrieve and check content (should use streaming decompression with sidecar)
            retrieved = await self.storage.retrieve(meta.file_id)
            assert retrieved == data
        finally:
            self.storage.max_size = old_max

    @pytest.mark.asyncio
    async def test_retrieve_generic_exception(self, monkeypatch: MonkeyPatch) -> None:
        data = b"errordecomp"
        meta = await self.storage.store(data, "errordecomp.txt", {"user_id": 1})
        # Patch _decompress_data to raise a generic exception (not FileStorageError)
        monkeypatch.setattr(
            file_utils,
            "_decompress_data",
            lambda d, c: (_ for _ in ()).throw(ValueError("fail generic")),
        )
        self.storage.compression = "gzip"
        with pytest.raises(file_utils.FileStorageError) as excinfo:
            await self.storage.retrieve(meta.file_id)
        assert "Failed to retrieve file" in str(excinfo.value)
        self.storage.compression = "gzip"

    @pytest.mark.asyncio
    async def test_delete_removes_sidecar(self) -> None:
        data = b"sidecardel"
        self.storage.use_sidecar = True
        meta = await self.storage.store(data, "sidecardel.txt", {"user_id": 1})
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
        assert sidecar_path.exists()
        await self.storage.delete(meta.file_id)
        assert not sidecar_path.exists()
        self.storage.use_sidecar = True

    @pytest.mark.asyncio
    async def test_delete_raises_filestorageerror(self, monkeypatch: MonkeyPatch) -> None:
        import pathlib

        data = b"delerror"
        meta = await self.storage.store(data, "delerror.txt", {"user_id": 1})
        # Patch Path.unlink globally to raise an OSError
        monkeypatch.setattr(
            pathlib.Path,
            "unlink",
            lambda *a, **kw: (_ for _ in ()).throw(OSError("fail unlink")),
        )
        with pytest.raises(file_utils.FileStorageError) as excinfo:
            await self.storage.delete(meta.file_id)
        assert "Failed to delete file" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_get_metadata_fallback(self) -> None:
        data = b"metafallback"
        self.storage.use_sidecar = False
        meta = await self.storage.store(data, "metafallback.txt", {"user_id": 1})
        file_path = self.storage._find_file_path(meta.file_id)
        # Rename user directory to a non-integer to trigger int() ValueError
        assert file_path is not None
        bad_user_dir = file_path.parent.parent.parent / "baduser"
        file_path.parent.parent.rename(bad_user_dir)
        # Update file_path after user dir rename
        bad_user_dir / file_path.parent.name / file_path.name
        meta2 = await self.storage.get_metadata(meta.file_id)
        assert meta2.user_id is None
        # Now, rename the date directory to a non-date string to trigger date parse fallback
        bad_date_dir = bad_user_dir / "notadate"
        (bad_user_dir / file_path.parent.name).rename(bad_date_dir)
        meta3 = await self.storage.get_metadata(meta.file_id)
        assert meta3.created_at is None
        self.storage.use_sidecar = True

    @pytest.mark.asyncio
    async def test_quarantine_on_integrity_failure(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
        # Store a file
        data = b"quarantine_test"
        self.storage.use_sidecar = False
        meta = await self.storage.store(data, "quarantine.txt", {"user_id": 1})
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        # Decrypt, decompress, tamper, recompress, re-encrypt
        import gzip

        from src.core.secure_bytes import decrypt_bytes, encrypt_bytes

        encrypted = file_path.read_bytes()
        decrypted = decrypt_bytes(encrypted)
        decompressed = gzip.decompress(decrypted)
        tampered = decompressed + b"tamper"
        recompressed = gzip.compress(tampered)
        file_path.write_bytes(encrypt_bytes(recompressed))
        # Enable integrity autovalidate and set quarantine dir
        file_utils.settings.file_integrity_autovalidate = True
        quarantine_dir = tmp_path / "quarantine"
        quarantine_dir.mkdir()
        file_utils.settings.file_integrity_quarantine_dir = str(quarantine_dir)
        # Patch logger to ensure warning is called
        called = {}

        def fake_warning(msg: str, *args: object, **kwargs: object) -> object:
            called["warned"] = True
            return file_utils.logger.opt(depth=1).info(msg)

        monkeypatch.setattr(file_utils.logger, "warning", fake_warning)
        # Attempt to retrieve, should move to quarantine and raise error
        with pytest.raises(FileIntegrityError):
            await self.storage.retrieve(meta.file_id)
        # File should be in quarantine and logger should be called
        assert file_path is not None
        assert (quarantine_dir / file_path.name).exists()
        assert called.get("warned")
        # Reset settings
        file_utils.settings.file_integrity_autovalidate = False
        self.storage.use_sidecar = True
        file_utils.settings.file_integrity_quarantine_dir = tempfile.mkdtemp()

    @pytest.mark.asyncio
    async def test_get_metadata_sidecar_missing_with_sidecar_true(self) -> None:
        data = b"sidecar_missing_meta"
        self.storage.use_sidecar = True
        meta = await self.storage.store(
            data, "sidecar_missing_meta.txt", {"user_id": 99}
        )
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
        # Remove the sidecar if it exists
        if sidecar_path.exists():
            sidecar_path.unlink()
        # Now get_metadata; should skip sidecar logic and use fallback
        meta2 = await self.storage.get_metadata(meta.file_id)
        assert meta2.file_id == meta.file_id
        assert meta2.filename == file_path.name
        assert meta2.user_id == 99
        assert meta2.size == file_path.stat().st_size
        self.storage.use_sidecar = True

    @pytest.mark.asyncio
    async def test_get_metadata_with_sidecar(self) -> None:
        data = b"sidecar_meta"
        self.storage.use_sidecar = True
        meta = await self.storage.store(
            data, "sidecar_meta.txt", {"user_id": 42, "content_type": "text/plain"}
        )
        # Should create a sidecar file
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
        assert sidecar_path.exists()
        # get_metadata should return the same metadata as in the sidecar
        meta2 = await self.storage.get_metadata(meta.file_id)
        assert meta2.file_id == meta.file_id
        assert meta2.filename == meta.filename
        assert meta2.user_id == 42
        assert meta2.content_type == "text/plain"
        from src.core.secure_bytes import decrypt_bytes

        decrypted = decrypt_bytes(file_path.read_bytes())
        assert meta2.size == len(decrypted)
        self.storage.use_sidecar = False

    @pytest.mark.asyncio
    async def test_validate_integrity_errors(self) -> None:
        data = b"integrity_test"
        self.storage.use_sidecar = True
        meta = await self.storage.store(data, "integrity.txt", {"user_id": 1})
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        import gzip

        from src.core.secure_bytes import decrypt_bytes, encrypt_bytes

        # 1. Decrypt, decompress, tamper (flip a byte), recompress, re-encrypt (checksum mismatch)
        encrypted = file_path.read_bytes()
        decrypted = decrypt_bytes(encrypted)
        decompressed = gzip.decompress(decrypted)
        # Flip the first byte to guarantee a change
        tampered = bytes([decompressed[0] ^ 0xFF]) + decompressed[1:]
        assert tampered != decompressed
        recompressed = gzip.compress(tampered)
        file_path.write_bytes(encrypt_bytes(recompressed))
        # Should raise FileIntegrityError (checksum mismatch)
        with pytest.raises(file_utils.FileIntegrityError):
            await self.storage.validate_integrity(meta.file_id)
        # 2. Corrupt file so decryption fails
        self.storage.use_sidecar = False
        file_path.write_bytes(b"not encrypted")
        with pytest.raises(file_utils.FileIntegrityError):
            await self.storage.validate_integrity(meta.file_id)
        # 3. Corrupt file so decompression fails
        # Store a new file for this
        meta2 = await self.storage.store(data, "integrity2.txt", {"user_id": 1})
        file_path2 = self.storage._find_file_path(meta2.file_id)
        assert file_path2 is not None
        encrypted2 = file_path2.read_bytes()
        decrypt_bytes(encrypted2)
        # Write invalid gzip data
        file_path2.write_bytes(encrypt_bytes(b"notgzip"))
        with pytest.raises(file_utils.FileIntegrityError):
            await self.storage.validate_integrity(meta2.file_id)
        self.storage.use_sidecar = True

    @pytest.mark.asyncio
    async def test_streaming_decompression_else_branch(self) -> None:
        # Temporarily increase max size to allow >1MB file
        orig_max = file_utils.settings.file_max_size_mb
        file_utils.settings.file_max_size_mb = 2
        self.storage.max_size = 2 * 1024 * 1024
        import gzip
        import json

        # Use valid gzip-compressed data
        raw_data = b"E" * (1024 * 1024 + 10)
        compressed_data = gzip.compress(raw_data)
        self.storage.use_sidecar = True
        meta = await self.storage.store(
            compressed_data,
            "stream_else.txt",
            {"user_id": 11, "content_type": "text/plain"},
        )
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
        # Remove the 'compression' key from the sidecar
        sidecar_data = json.loads(sidecar_path.read_text())
        sidecar_data["extra"].pop("compression", None)
        sidecar_path.write_text(json.dumps(sidecar_data))
        # Now retrieve, which should hit the else branch (no compression_used)
        retrieved = await self.storage.retrieve(meta.file_id)
        assert retrieved == compressed_data
        self.storage.use_sidecar = False
        # Restore max size
        file_utils.settings.file_max_size_mb = orig_max
        self.storage.max_size = orig_max * 1024 * 1024

    @pytest.mark.asyncio
    async def test_streaming_sidecar_compression_present(self) -> None:
        # Test 1: use_sidecar=True, sidecar exists, 'compression' present, file >1MB
        orig_max = file_utils.settings.file_max_size_mb
        file_utils.settings.file_max_size_mb = 2
        self.storage.max_size = 2 * 1024 * 1024
        import gzip
        import json

        raw_data = b"A" * (1024 * 1024 + 10)
        compressed_data = gzip.compress(raw_data)
        self.storage.use_sidecar = True
        meta = await self.storage.store(
            compressed_data,
            "stream_sidecar_present.txt",
            {"user_id": 100, "content_type": "text/plain"},
        )
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
        # Confirm 'compression' is present in sidecar
        sidecar_data = json.loads(sidecar_path.read_text())
        assert "compression" in sidecar_data["extra"]
        # Retrieve and check content
        retrieved = await self.storage.retrieve(meta.file_id)
        assert retrieved == compressed_data
        self.storage.use_sidecar = False
        file_utils.settings.file_max_size_mb = orig_max
        self.storage.max_size = orig_max * 1024 * 1024

    @pytest.mark.asyncio
    async def test_streaming_sidecar_compression_missing(self) -> None:
        # Test 2: use_sidecar=True, sidecar exists, 'compression' missing, file >1MB
        orig_max = file_utils.settings.file_max_size_mb
        file_utils.settings.file_max_size_mb = 2
        self.storage.max_size = 2 * 1024 * 1024
        import gzip
        import json

        raw_data = b"B" * (1024 * 1024 + 10)
        compressed_data = gzip.compress(raw_data)
        self.storage.use_sidecar = True
        meta = await self.storage.store(
            compressed_data,
            "stream_sidecar_missing.txt",
            {"user_id": 101, "content_type": "text/plain"},
        )
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
        # Remove 'compression' from sidecar
        sidecar_data = json.loads(sidecar_path.read_text())
        sidecar_data["extra"].pop("compression", None)
        sidecar_path.write_text(json.dumps(sidecar_data))
        # Retrieve and check content (should fall back to self.compression)
        retrieved = await self.storage.retrieve(meta.file_id)
        assert retrieved == compressed_data
        self.storage.use_sidecar = False
        file_utils.settings.file_max_size_mb = orig_max
        self.storage.max_size = orig_max * 1024 * 1024

    @pytest.mark.asyncio
    async def test_streaming_sidecar_missing_file(self) -> None:
        # Test 3: use_sidecar=True, sidecar does not exist, file >1MB
        orig_max = file_utils.settings.file_max_size_mb
        file_utils.settings.file_max_size_mb = 2
        self.storage.max_size = 2 * 1024 * 1024
        import gzip

        raw_data = b"C" * (1024 * 1024 + 10)
        compressed_data = gzip.compress(raw_data)
        self.storage.use_sidecar = True
        meta = await self.storage.store(
            compressed_data,
            "stream_sidecar_missing_file.txt",
            {"user_id": 102, "content_type": "text/plain"},
        )
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
        if sidecar_path.exists():
            sidecar_path.unlink()
        # Retrieve and check content (should fall back to self.compression)
        retrieved = await self.storage.retrieve(meta.file_id)
        assert retrieved == compressed_data
        self.storage.use_sidecar = False
        file_utils.settings.file_max_size_mb = orig_max
        self.storage.max_size = orig_max * 1024 * 1024

    @pytest.mark.asyncio
    async def test_get_metadata_fallback_no_sidecar(self) -> None:
        data = b"fallback_meta"
        self.storage.use_sidecar = False
        meta = await self.storage.store(data, "fallback_meta.txt", {"user_id": 21})
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        # Ensure no sidecar exists
        sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
        if sidecar_path.exists():
            sidecar_path.unlink()
        meta2 = await self.storage.get_metadata(meta.file_id)
        assert meta2.file_id == meta.file_id
        assert meta2.filename == file_path.name
        assert meta2.user_id == 21
        assert meta2.size == file_path.stat().st_size
        self.storage.use_sidecar = True

    @pytest.mark.asyncio
    async def test_streaming_no_sidecar(self) -> None:
        # Test 4: use_sidecar=False, file >1MB
        orig_max = file_utils.settings.file_max_size_mb
        file_utils.settings.file_max_size_mb = 2
        self.storage.max_size = 2 * 1024 * 1024
        import gzip

        raw_data = b"D" * (1024 * 1024 + 10)
        compressed_data = gzip.compress(raw_data)
        self.storage.use_sidecar = False
        meta = await self.storage.store(
            compressed_data,
            "stream_no_sidecar.txt",
            {"user_id": 103, "content_type": "text/plain"},
        )
        # Retrieve and check content (should skip sidecar logic)
        retrieved = await self.storage.retrieve(meta.file_id)
        assert retrieved == compressed_data
        file_utils.settings.file_max_size_mb = orig_max
        self.storage.max_size = orig_max * 1024 * 1024

    @pytest.mark.asyncio
    async def test_retrieve_stream_no_compression_with_sidecar(self) -> None:
        # Use random data to ensure file is >1MB, but no compression is set
        import json
        import os

        import aiofiles

        data = os.urandom(1024 * 1024 + 100)
        self.storage.compression = None
        self.storage.use_sidecar = True
        old_max = self.storage.max_size
        self.storage.max_size = 2 * 1024 * 1024
        try:
            meta = await self.storage.store(
                data, "bigsidecar_nocomp.txt", {"user_id": 1}
            )
            file_path = self.storage._find_file_path(meta.file_id)
            assert file_path is not None
            sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
            # Overwrite sidecar to remove compression key and ensure compression_used is falsy
            async with aiofiles.open(sidecar_path, "r+") as f:
                meta_json = await f.read()
                meta_obj = json.loads(meta_json)
                meta_obj["extra"]["compression"] = None  # Explicitly set to None
                await f.seek(0)
                await f.write(json.dumps(meta_obj))
                await f.truncate()
            # Retrieve and check content (should use streaming path, no compression)
            retrieved = await self.storage.retrieve(meta.file_id)
            assert retrieved == data
        finally:
            self.storage.max_size = old_max

    @pytest.mark.asyncio
    async def test_retrieve_stream_no_compression_with_sidecar_missing_key(self) -> None:
        # Use random data to ensure file is >1MB, and remove 'compression' key from sidecar and storage
        import json
        import os

        import aiofiles

        data = os.urandom(1024 * 1024 + 100)
        self.storage.compression = None  # Ensure fallback is None
        self.storage.use_sidecar = True
        old_max = self.storage.max_size
        self.storage.max_size = 2 * 1024 * 1024
        try:
            meta = await self.storage.store(
                data, "bigsidecar_nocomp3.txt", {"user_id": 1}
            )
            file_path = self.storage._find_file_path(meta.file_id)
            assert file_path is not None
            sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
            # Overwrite sidecar to remove 'compression' key entirely
            async with aiofiles.open(sidecar_path, "r+") as f:
                meta_json = await f.read()
                meta_obj = json.loads(meta_json)
                if "compression" in meta_obj["extra"]:
                    del meta_obj["extra"]["compression"]
                await f.seek(0)
                await f.write(json.dumps(meta_obj))
                await f.truncate()
            # Retrieve and check content (should use streaming path, no compression)
            retrieved = await self.storage.retrieve(meta.file_id)
            assert retrieved == data
        finally:
            self.storage.max_size = old_max

    @pytest.mark.asyncio
    async def test_delete_sidecar_missing(self) -> None:
        data = b"sidecar_missing"
        self.storage.use_sidecar = True
        meta = await self.storage.store(data, "sidecar_missing.txt", {"user_id": 1})
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
        # Remove the sidecar if it exists
        if sidecar_path.exists():
            sidecar_path.unlink()
        # Now delete the file; should not raise, should cover the branch where sidecar does not exist
        await self.storage.delete(meta.file_id)
        assert not file_path.exists()
        assert not sidecar_path.exists()
        self.storage.use_sidecar = True

    @pytest.mark.asyncio
    async def test_delete_no_sidecar(self) -> None:
        data = b"no_sidecar"
        self.storage.use_sidecar = False
        meta = await self.storage.store(data, "no_sidecar.txt", {"user_id": 1})
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        sidecar_path = file_path.with_suffix(file_path.suffix + ".meta.json")
        # Ensure sidecar does not exist
        if sidecar_path.exists():
            sidecar_path.unlink()
        # Delete the file; should skip sidecar logic
        await self.storage.delete(meta.file_id)
        assert not file_path.exists()
        self.storage.use_sidecar = True

    @pytest.mark.asyncio
    async def test_validate_integrity_decompression_fileintegrityerror(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        data = b"decomp_fie"
        meta = await self.storage.store(data, "decomp_fie.txt", {"user_id": 99})
        # Patch gzip.decompress to raise FileIntegrityError
        import gzip

        monkeypatch.setattr(
            gzip,
            "decompress",
            lambda d: (_ for _ in ()).throw(
                file_utils.FileIntegrityError("decomp error")
            ),
        )
        with pytest.raises(file_utils.FileIntegrityError) as excinfo:
            await self.storage.validate_integrity(meta.file_id)
        assert "decomp error" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_validate_integrity_decompression_generic_exception(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        data = b"decomp_gen"
        meta = await self.storage.store(data, "decomp_gen.txt", {"user_id": 100})
        # Patch gzip.decompress to raise a generic exception
        import gzip

        monkeypatch.setattr(
            gzip,
            "decompress",
            lambda d: (_ for _ in ()).throw(RuntimeError("generic decompress error")),
        )
        with pytest.raises(file_utils.FileIntegrityError) as excinfo:
            await self.storage.validate_integrity(meta.file_id)
        assert "generic decompress error" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_validate_integrity_generic_exception_in_get_hash(self, monkeypatch: MonkeyPatch) -> None:
        data = b"hasherror"
        meta = await self.storage.store(data, "hasherror.txt", {"user_id": 101})
        # Patch _get_hash to raise a generic exception
        monkeypatch.setattr(
            file_utils,
            "_get_hash",
            lambda d: (_ for _ in ()).throw(RuntimeError("hash error")),
        )
        with pytest.raises(file_utils.FileIntegrityError) as excinfo:
            await self.storage.validate_integrity(meta.file_id)
        assert "hash error" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_validate_integrity_nonexistent(self) -> None:
        with pytest.raises(FileNotFoundError):
            await self.storage.validate_integrity("nonexistent_file_id")

    @pytest.mark.asyncio
    async def test_validate_integrity_invalid_token(self, monkeypatch: MonkeyPatch) -> None:
        data = b"irrelevant-data-to-trigger-encryption" * 10
        meta = await self.storage.store(data, "invalidtoken.txt", {"user_id": 10})
        from cryptography.fernet import InvalidToken

        # Patch the decrypt_bytes used by file_utils (the module under test)
        monkeypatch.setattr(
            file_utils, "decrypt_bytes", lambda d: (_ for _ in ()).throw(InvalidToken())
        )
        file_path = self.storage._find_file_path(meta.file_id)
        assert file_path is not None
        sidecar = file_path.with_suffix(file_path.suffix + ".meta.json")
        if sidecar.exists():
            sidecar.unlink()
        with pytest.raises(
            FileIntegrityError, match="Decryption failed: Invalid token"
        ):
            await self.storage.validate_integrity(meta.file_id)


@pytest.mark.asyncio
class TestableS3FileStorage(S3FileStorage):
    async def delete(self, file_id: str) -> None:
        pass

    async def generate_url(self, file_id: str, *a: object, **kw: object) -> str:
        return "http://example.com"

    async def get_metadata(self, file_id: str) -> file_utils.FileMetadata:
        return file_utils.FileMetadata(
            file_id=file_id,
            filename="dummy.txt",
            content_type="text/plain",
            size=0,
            user_id=None,
            checksum=None,
            created_at=None,
            updated_at=None,
            storage_backend=None,
            access_level=file_utils.FileAccessLevel.PRIVATE,
            extra={},
        )

    async def validate_integrity(self, file_id: str, data: object = None) -> bool:
        return True


S3_SETTINGS = types.SimpleNamespace(
    s3_bucket="test-bucket",
    s3_prefix="test-prefix",
    s3_acl="private",
    s3_server_side_encryption=None,
    s3_kms_key_id=None,
    s3_region=None,
    s3_endpoint_url=None,
    s3_access_key_id=None,
    s3_secret_access_key=None,
    file_compression_min_size=1,
    file_compression_level=6,
    file_compression=None,
    file_hash_algorithm="sha256",
    file_integrity_autovalidate=False,
    file_url_max_expiry=86400,
    file_url_base=None,
    file_integrity_quarantine_dir=None,
)


@pytest.mark.asyncio
class TestS3FileStorage:
    def test_init_missing_bucket(self) -> None:
        incomplete = types.SimpleNamespace(
            s3_bucket=None,
            s3_prefix=None,
            s3_acl=None,
            s3_server_side_encryption=None,
            s3_kms_key_id=None,
            s3_region=None,
            s3_endpoint_url=None,
            s3_access_key_id=None,
            s3_secret_access_key=None,
        )
        with mock.patch("src.utils.file.settings", new=incomplete):
            with pytest.raises(RuntimeError, match="S3 bucket not configured"):
                TestableS3FileStorage()

    @pytest.mark.asyncio
    async def test_retry_raises_on_failure(self) -> None:
        with mock.patch("src.utils.file.settings", new=S3_SETTINGS):
            storage = TestableS3FileStorage()

            async def always_fail(*a: Any, **kw: Any) -> None:
                raise Exception("fail")

            with (
                mock.patch("src.utils.file.ClientError", Exception),
                mock.patch("src.utils.file.NoCredentialsError", Exception),
                mock.patch("src.utils.file.EndpointConnectionError", Exception),
            ):
                with pytest.raises(FileStorageError, match="S3 operation failed"):
                    await storage._retry(cast(Callable[..., Awaitable[Any]], always_fail))

    @pytest.mark.asyncio
    async def test_store_and_retrieve_success(self) -> None:
        with mock.patch("src.utils.file.settings", new=S3_SETTINGS):
            storage = TestableS3FileStorage()
            mock_s3 = mock.AsyncMock()
            mock_session = mock.Mock()
            mock_client = mock.AsyncMock()
            mock_client.__aenter__.return_value = mock_s3
            mock_client.__aexit__.return_value = None
            mock_session.client.return_value = mock_client
            setattr(storage, "_get_session", lambda: mock_session)
            with (
                mock.patch("src.utils.file._get_hash", return_value="abc123"),
                mock.patch(
                    "src.utils.file._compress_data",
                    side_effect=compress_side_effect,
                ),
            ):
                mock_s3.put_object.return_value = mock.AsyncMock()
                meta = await storage.store(
                    b"data", "file.txt", {"user_id": 1, "content_type": "text/plain"}
                )
                assert meta.file_id.endswith("file.txt")
                mock_s3.get_object.return_value = {
                    "Body": mock.AsyncMock(read=mock.AsyncMock(return_value=b"data")),
                    "Metadata": {"checksum": "abc123", "hash_algorithm": "sha256"},
                }
                result = await storage.retrieve(meta.file_id)
                assert result == b"data"

    @pytest.mark.asyncio
    async def test_retrieve_checksum_mismatch(self) -> None:
        patched = types.SimpleNamespace(**S3_SETTINGS.__dict__)
        patched.file_integrity_autovalidate = True
        with mock.patch("src.utils.file.settings", new=patched):
            storage = TestableS3FileStorage()
            mock_s3 = mock.AsyncMock()
            mock_session = mock.Mock()
            mock_client = mock.AsyncMock()
            mock_client.__aenter__.return_value = mock_s3
            mock_client.__aexit__.return_value = None
            mock_session.client.return_value = mock_client
            setattr(storage, "_get_session", lambda: mock_session)
            mock_s3.get_object.return_value = {
                "Body": mock.AsyncMock(read=mock.AsyncMock(return_value=b"data")),
                "Metadata": {"checksum": "wrong", "hash_algorithm": "sha256"},
            }
            with pytest.raises(FileIntegrityError, match="Checksum mismatch"):
                await storage.retrieve("fileid")

    @pytest.mark.asyncio
    async def test_retrieve_not_found(self) -> None:
        with mock.patch("src.utils.file.settings", new=S3_SETTINGS):
            storage = TestableS3FileStorage()
            mock_s3 = mock.AsyncMock()
            mock_session = mock.Mock()
            mock_client = mock.AsyncMock()
            mock_client.__aenter__.return_value = mock_s3
            mock_client.__aexit__.return_value = None
            mock_session.client.return_value = mock_client
            setattr(storage, "_get_session", lambda: mock_session)
            mock_s3.get_object.side_effect = Exception("not found")
            with pytest.raises(FileNotFoundError):
                await storage.retrieve("fileid")
