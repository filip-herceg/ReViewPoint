import asyncio
import os
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import pytest
from src.utils import file as file_utils
from src.utils.file import (
    FileAccessLevel, FileMetadata, FileStorageError, FileNotFoundError, FileIntegrityError, LocalFileStorage, _get_hash, _compress_data, _decompress_data, _should_skip_compression, _generate_file_token, _stream_compress_to_file, _stream_decompress_from_file
)

class DummySettings:
    upload_dir = tempfile.mkdtemp()
    file_permissions = 0o600
    file_metadata_sidecar = True
    file_compression = 'gzip'
    file_max_size_mb = 1
    file_hash_algorithm = 'sha256'
    file_compression_min_size = 1
    file_compression_level = 6
    file_url_max_expiry = 86400
    file_url_base = None
    jwt_secret_key = 'testsecret'
    file_integrity_autovalidate = False
    file_integrity_quarantine_dir = tempfile.mkdtemp()

# Patch settings for tests
file_utils.settings = DummySettings()

@pytest.mark.asyncio
class TestLocalFileStorage:
    @pytest.fixture(autouse=True)
    def setup_storage(self, tmp_path):
        self.storage = LocalFileStorage(base_dir=tmp_path)
        self.tmp_path = tmp_path

    @pytest.mark.asyncio
    async def test_store_and_retrieve(self):
        data = b"hello world"
        meta = await self.storage.store(data, "test.txt", {"user_id": 1, "content_type": "text/plain"})
        assert meta.filename == "test.txt"
        assert meta.size > 0
        retrieved = await self.storage.retrieve(meta.file_id)
        assert retrieved == data

    @pytest.mark.asyncio
    async def test_store_too_large(self):
        data = b"x" * (self.storage.max_size + 1)
        with pytest.raises(FileStorageError):
            await self.storage.store(data, "big.txt", {"user_id": 1})

    @pytest.mark.asyncio
    async def test_delete(self):
        data = b"bye"
        meta = await self.storage.store(data, "bye.txt", {"user_id": 2})
        await self.storage.delete(meta.file_id)
        with pytest.raises(FileNotFoundError):
            await self.storage.retrieve(meta.file_id)

    @pytest.mark.asyncio
    async def test_get_metadata(self):
        data = b"meta"
        meta = await self.storage.store(data, "meta.txt", {"user_id": 3})
        meta2 = await self.storage.get_metadata(meta.file_id)
        assert meta2.file_id == meta.file_id
        assert meta2.filename == "meta.txt"
        assert meta2.size == meta.size

    @pytest.mark.asyncio
    async def test_generate_url_private_and_public(self):
        data = b"urltest"
        meta = await self.storage.store(data, "url.txt", {"user_id": 4})
        url = await self.storage.generate_url(meta.file_id, expires_in=100, public=False, user_id="4")
        assert url.startswith("/files/")
        assert "token=" in url
        url2 = await self.storage.generate_url(meta.file_id, expires_in=100, public=True)
        assert url2.startswith("/files/")
        assert "token=" not in url2

    @pytest.mark.asyncio
    async def test_validate_integrity(self):
        data = b"integrity"
        meta = await self.storage.store(data, "integrity.txt", {"user_id": 5, "original_data": data})
        assert await self.storage.validate_integrity(meta.file_id)

    @pytest.mark.asyncio
    async def test_retrieve_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            await self.storage.retrieve("nonexistent")

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            await self.storage.delete("nonexistent")

    @pytest.mark.asyncio
    async def test_get_metadata_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            await self.storage.get_metadata("nonexistent")

    @pytest.mark.asyncio
    async def test_integrity_fail(self):
        data = b"failintegrity"
        meta = await self.storage.store(data, "fail.txt", {"user_id": 6})
        # Corrupt the file
        file_path = self.storage._find_file_path(meta.file_id)
        file_path.write_bytes(b"corrupted")
        with pytest.raises(FileIntegrityError):
            await self.storage.validate_integrity(meta.file_id)

    @pytest.mark.asyncio
    async def test_sidecar_metadata(self):
        data = b"sidecar"
        meta = await self.storage.store(data, "sidecar.txt", {"user_id": 7})
        file_path = self.storage._find_file_path(meta.file_id)
        sidecar = file_path.with_suffix(file_path.suffix + ".meta.json")
        assert sidecar.exists()

    @pytest.mark.asyncio
    async def test_compression_and_decompression(self):
        data = b"A" * 2048
        meta = await self.storage.store(data, "compress.txt", {"user_id": 8})
        retrieved = await self.storage.retrieve(meta.file_id)
        assert retrieved == data

    @pytest.mark.asyncio
    async def test_stream_compress_and_decompress(self):
        data = b"B" * (1 * 1024 * 1024)  # 1MB, within max_size
        meta = await self.storage.store(data, "stream.txt", {"user_id": 9, "original_data": data})
        retrieved = await self.storage.retrieve(meta.file_id)
        assert retrieved == data

    @pytest.mark.asyncio
    async def test_should_skip_compression(self):
        assert _should_skip_compression("file.jpg", "image/jpeg")
        assert not _should_skip_compression("file.txt", "text/plain")

    @pytest.mark.asyncio
    async def test_generate_file_token(self):
        token = _generate_file_token("fileid", "userid", 60)
        assert isinstance(token, str)

    @pytest.mark.asyncio
    async def test_get_hash(self):
        h = _get_hash(b"abc", "sha256")
        assert isinstance(h, str)
        h2 = _get_hash(b"abc", "md5")
        assert isinstance(h2, str)

    @pytest.mark.asyncio
    async def test_compress_and_decompress_data(self):
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
    async def test_stream_compress_to_file_and_decompress(self):
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
    async def test_find_file_path(self):
        data = b"findme"
        meta = await self.storage.store(data, "findme.txt", {"user_id": 10})
        path = self.storage._find_file_path(meta.file_id)
        assert path.exists()

    @pytest.mark.asyncio
    async def test_file_access_level_enum(self):
        assert FileAccessLevel.PRIVATE == "private"
        assert FileAccessLevel.PUBLIC == "public"

    @pytest.mark.asyncio
    async def test_file_metadata_model(self):
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
        assert meta.extra["foo"] == "bar"

    @pytest.mark.asyncio
    async def test_file_storage_error_types(self):
        assert issubclass(FileStorageError, Exception)
        assert issubclass(FileNotFoundError, FileStorageError)
        assert issubclass(FileIntegrityError, FileStorageError)

    @pytest.mark.asyncio
    async def test_store_with_no_user_id(self):
        data = b"no user id"
        meta = await self.storage.store(data, "nouser.txt", {})
        assert meta.user_id == 0

    @pytest.mark.asyncio
    async def test_store_with_various_extensions(self):
        for ext in [".txt", ".jpg", ".tar.gz", ".weird"]:
            data = b"data" + ext.encode()
            meta = await self.storage.store(data, f"file{ext}", {"user_id": 11})
            assert meta.filename.endswith(ext)

    @pytest.mark.asyncio
    async def test_store_and_retrieve_with_sidecar_disabled(self):
        self.storage.use_sidecar = False
        data = b"sidecar off"
        meta = await self.storage.store(data, "nosidecar.txt", {"user_id": 12})
        retrieved = await self.storage.retrieve(meta.file_id)
        assert retrieved == data
        self.storage.use_sidecar = True

    @pytest.mark.asyncio
    async def test_generate_url_max_expiry(self):
        data = b"expiry"
        meta = await self.storage.store(data, "expiry.txt", {"user_id": 13})
        url = await self.storage.generate_url(meta.file_id, expires_in=999999, public=False, user_id="13")
        assert "token=" in url

    @pytest.mark.asyncio
    async def test_generate_url_revoked(self, monkeypatch):
        data = b"revoked"
        meta = await self.storage.store(data, "revoked.txt", {"user_id": 14})
        monkeypatch.setattr(file_utils, "is_local_token_revoked", lambda file_id: True)
        with pytest.raises(FileStorageError):
            await self.storage.generate_url(meta.file_id, public=False, user_id="14")
        monkeypatch.setattr(file_utils, "is_local_token_revoked", lambda file_id: False)

    @pytest.mark.asyncio
    async def test_find_file_path_returns_none(self):
        assert self.storage._find_file_path("notarealfileid") is None

    @pytest.mark.asyncio
    async def test_sanitize_filename(self):
        bad_name = "../../evil.txt"
        sanitized = self.storage._sanitize_filename(bad_name)
        assert ".." not in sanitized
        assert os.path.basename(sanitized) == sanitized

    @pytest.mark.asyncio
    async def test_stream_decompress_from_file_no_algo(self):
        data = b"plain data"
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "plain.txt"
            out_path.write_bytes(data)
            result = _stream_decompress_from_file(out_path, "none")
            assert result == data

    @pytest.mark.asyncio
    async def test_decompress_data_invalid_algo(self):
        data = b"not compressed"
        with pytest.raises(FileStorageError):
            _decompress_data(data, "invalid_algo")

    @pytest.mark.asyncio
    async def test_stream_compress_to_file_invalid_algo(self):
        data = b"data"
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "invalid"
            _stream_compress_to_file(data, "invalid_algo", 6, out_path)
            assert out_path.read_bytes() == data

    @pytest.mark.asyncio
    async def test_stream_decompress_from_file_invalid_algo(self):
        data = b"data"
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "invalid"
            out_path.write_bytes(data)
            result = _stream_decompress_from_file(out_path, "invalid_algo")
            assert result == data

    @pytest.mark.asyncio
    async def test_file_metadata_extra_fields(self):
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
    async def test_file_metadata_default_values(self):
        meta = FileMetadata(
            file_id="id3",
            filename="f3.txt",
            content_type="text/plain",
            size=789,
        )
        assert meta.access_level == FileAccessLevel.PRIVATE
        assert isinstance(meta.extra, dict)

    @pytest.mark.asyncio
    async def test_file_access_level_enum_str(self):
        assert FileAccessLevel.PRIVATE.value == "private"
        assert FileAccessLevel.PUBLIC.value == "public"

    @pytest.mark.asyncio
    async def test_file_storage_error_str(self):
        err = FileStorageError("errormsg")
        assert str(err) == "errormsg"
        err2 = FileNotFoundError("notfound")
        assert str(err2) == "notfound"
        err3 = FileIntegrityError("badintegrity")
        assert str(err3) == "badintegrity"
