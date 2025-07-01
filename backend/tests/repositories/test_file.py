from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from src.repositories.file import (
    create_file,
    delete_file,
    get_file_by_filename,
    list_files,
)
from src.utils.errors import ValidationError


class TestFileRepository:
    @pytest.mark.asyncio
    async def test_create_file_success(self, async_session):
        file = await create_file(async_session, "test.txt", "text/plain", user_id=1)
        assert file.filename == "test.txt"
        assert file.content_type == "text/plain"
        assert file.user_id == 1

    @pytest.mark.asyncio
    async def test_create_file_missing_filename(self, async_session):
        with pytest.raises(ValidationError):
            await create_file(async_session, "", "text/plain", user_id=1)

    @pytest.mark.asyncio
    async def test_get_file_by_filename(self, async_session):
        await create_file(async_session, "findme.txt", "text/plain", user_id=2)
        file = await get_file_by_filename(async_session, "findme.txt")
        assert file is not None
        assert file.filename == "findme.txt"

    @pytest.mark.asyncio
    async def test_get_file_by_filename_not_found(self, async_session):
        file = await get_file_by_filename(async_session, "doesnotexist.txt")
        assert file is None

    @pytest.mark.asyncio
    async def test_delete_file(self, async_session):
        await create_file(async_session, "todelete.txt", "text/plain", user_id=3)
        deleted = await delete_file(async_session, "todelete.txt")
        assert deleted is True
        file = await get_file_by_filename(async_session, "todelete.txt")
        assert file is None

    @pytest.mark.asyncio
    async def test_delete_file_not_found(self, async_session):
        deleted = await delete_file(async_session, "notfound.txt")
        assert deleted is False

    @pytest.mark.asyncio
    async def test_duplicate_filename_same_user(self, async_session):
        await create_file(async_session, "dup.txt", "text/plain", user_id=4)
        with pytest.raises(IntegrityError):
            await create_file(async_session, "dup.txt", "text/plain", user_id=4)
        await async_session.rollback()

    @pytest.mark.asyncio
    async def test_long_filename_and_content_type(self, async_session):
        long_filename = "a" * 255
        long_content_type = "b" * 128
        file = await create_file(
            async_session, long_filename, long_content_type, user_id=5
        )
        assert file.filename == long_filename
        assert file.content_type == long_content_type

    @pytest.mark.asyncio
    async def test_non_ascii_and_special_chars(self, async_session):
        file = await create_file(
            async_session, "файл!@#.txt", "application/x-спец", user_id=6
        )
        assert "файл" in file.filename
        assert "спец" in file.content_type

    @pytest.mark.asyncio
    async def test_create_file_missing_user(self, async_session):
        with pytest.raises(IntegrityError):
            await create_file(async_session, "nouser.txt", "text/plain", user_id=999999)
        await async_session.rollback()

    @pytest.mark.asyncio
    async def test_bulk_create_and_delete(self, async_session):
        files = [
            await create_file(async_session, f"bulk-{i}.txt", "text/plain", user_id=7)
            for i in range(5)
        ]
        for f in files:
            assert f.id is not None
        for f in files:
            deleted = await delete_file(async_session, f.filename)
            assert deleted is True

    @pytest.mark.asyncio
    async def test_list_files_pagination_and_search(self, async_session):
        user_id = 8
        now = datetime.now(UTC)
        for i in range(10):
            file = await create_file(
                async_session, f"file{i}.txt", "text/plain", user_id=user_id
            )
            file.created_at = now - timedelta(days=i)
        await async_session.commit()
        files, total = await list_files(async_session, user_id, offset=0, limit=5)
        assert len(files) == 5
        assert total == 10
        files, total = await list_files(async_session, user_id, q="file1")
        assert any("file1" in f.filename for f in files)
        files, total = await list_files(
            async_session, user_id, created_after=now - timedelta(days=5)
        )
        assert all(f.created_at >= now - timedelta(days=5) for f in files)

    @pytest.mark.asyncio
    async def test_list_files_sorting(self, async_session):
        user_id = 9
        now = datetime.now(UTC)
        for i in range(3):
            file = await create_file(
                async_session, f"sortfile{i}.txt", "text/plain", user_id=user_id
            )
            file.created_at = now - timedelta(days=i)
        await async_session.commit()
        files, _ = await list_files(
            async_session, user_id, sort="filename", order="asc"
        )
        filenames = [f.filename for f in files]
        assert filenames == sorted(filenames)
        files, _ = await list_files(
            async_session, user_id, sort="created_at", order="desc"
        )
        created_ats = [f.created_at for f in files]
        assert created_ats == sorted(created_ats, reverse=True)

    @pytest.mark.asyncio
    async def test_transactional_rollback_create_file(self, async_session):
        async def op():
            await create_file(
                async_session, "rollbackfile.txt", "text/plain", user_id=10
            )

        trans = await async_session.begin()
        try:
            await op()
        finally:
            await trans.rollback()
        file = await get_file_by_filename(async_session, "rollbackfile.txt")
        assert file is None

    @pytest.mark.asyncio
    async def test_duplicate_filename_different_users(self, async_session):
        file1 = await create_file(
            async_session, "shared.txt", "text/plain", user_id=100
        )
        file2 = await create_file(
            async_session, "shared.txt", "text/plain", user_id=101
        )
        assert file1.filename == file2.filename
        assert file1.user_id != file2.user_id

    @pytest.mark.asyncio
    async def test_invalid_content_type(self, async_session):
        with pytest.raises(Exception):
            await create_file(async_session, "badct.txt", "", user_id=11)
        with pytest.raises(Exception):
            await create_file(async_session, "badct2.txt", "c" * 1024, user_id=11)
        with pytest.raises(Exception):
            await create_file(async_session, "badct3.txt", 123, user_id=11)  # type: ignore

    @pytest.mark.asyncio
    async def test_invalid_filename_type(self, async_session):
        with pytest.raises(Exception):
            await create_file(async_session, 123, "text/plain", user_id=12)  # type: ignore
        with pytest.raises(Exception):
            await create_file(async_session, None, "text/plain", user_id=12)  # type: ignore

    @pytest.mark.asyncio
    async def test_invalid_user_id(self, async_session):
        with pytest.raises(Exception):
            await create_file(async_session, "baduser.txt", "text/plain", user_id=-1)
        with pytest.raises(Exception):
            await create_file(async_session, "baduser2.txt", "text/plain", user_id=0)
        with pytest.raises(Exception):
            await create_file(async_session, "baduser3.txt", "text/plain", user_id=None)  # type: ignore

    @pytest.mark.asyncio
    async def test_delete_file_case_insensitive(self, async_session):
        await create_file(async_session, "CaseTest.txt", "text/plain", user_id=13)
        deleted = await delete_file(async_session, "casetest.txt")
        assert deleted in (True, False)

    @pytest.mark.asyncio
    async def test_list_files_empty(self, async_session):
        files, total = await list_files(async_session, user_id=9999)
        assert files == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_list_files_offset_beyond_total(self, async_session):
        user_id = 14
        await create_file(async_session, "off1.txt", "text/plain", user_id=user_id)
        files, total = await list_files(async_session, user_id, offset=100)
        assert files == []
        assert total == 1

    @pytest.mark.asyncio
    async def test_rollback_after_integrity_error(self, async_session):
        await create_file(async_session, "rollbackdup.txt", "text/plain", user_id=15)
        with pytest.raises(IntegrityError):
            await create_file(
                async_session, "rollbackdup.txt", "text/plain", user_id=15
            )
        await async_session.rollback()
        file = await create_file(
            async_session, "rollbackok.txt", "text/plain", user_id=15
        )
        assert file.filename == "rollbackok.txt"

    @pytest.mark.asyncio
    async def test_simulated_concurrent_creation(self, async_session):
        user_id = 16
        await create_file(
            async_session, "concurrent.txt", "text/plain", user_id=user_id
        )
        with pytest.raises(IntegrityError):
            await create_file(
                async_session, "concurrent.txt", "text/plain", user_id=user_id
            )
        await async_session.rollback()
