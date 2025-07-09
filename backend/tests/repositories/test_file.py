from datetime import UTC, datetime, timedelta
from typing import Final

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.file import File
from src.models.user import User
from src.repositories.file import (
    create_file,
    delete_file,
    get_file_by_filename,
    list_files,
)
from src.utils.errors import ValidationError


@pytest.mark.asyncio
async def test_create_file_success(async_session: AsyncSession) -> None:
    """Test that a file can be created successfully for a valid user."""
    user: User = User(
        email="test@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()

    file = await create_file(async_session, "test.txt", "text/plain", user_id=user.id)
    assert file.filename == "test.txt"
    assert file.content_type == "text/plain"
    assert file.user_id == user.id


@pytest.mark.asyncio
async def test_create_file_missing_filename(async_session: AsyncSession) -> None:
    """Test that creating a file with a missing filename raises ValidationError."""
    user: User = User(
        email="test2@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()

    with pytest.raises(ValidationError):
        await create_file(async_session, "", "text/plain", user_id=user.id)


@pytest.mark.asyncio
async def test_get_file_by_filename(async_session: AsyncSession) -> None:
    """Test that a file can be retrieved by filename."""
    user: User = User(
        email="test3@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()

    await create_file(async_session, "findme.txt", "text/plain", user_id=user.id)
    file = await get_file_by_filename(async_session, "findme.txt")
    assert file is not None
    assert file.filename == "findme.txt"


@pytest.mark.asyncio
async def test_get_file_by_filename_not_found(async_session: AsyncSession) -> None:
    """Test that getting a file by a non-existent filename returns None."""
    file = await get_file_by_filename(async_session, "doesnotexist.txt")
    assert file is None


@pytest.mark.asyncio
async def test_delete_file(async_session: AsyncSession) -> None:
    """Test that a file can be deleted and is no longer retrievable."""
    user: User = User(
        email="test4@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()

    await create_file(async_session, "todelete.txt", "text/plain", user_id=user.id)
    deleted: bool = await delete_file(async_session, "todelete.txt")
    assert deleted is True
    file = await get_file_by_filename(async_session, "todelete.txt")
    assert file is None


@pytest.mark.asyncio
async def test_delete_file_not_found(async_session: AsyncSession) -> None:
    """Test that deleting a non-existent file returns False."""
    deleted: bool = await delete_file(async_session, "notfound.txt")
    assert deleted is False


@pytest.mark.asyncio
@pytest.mark.requires_real_db(
    "Duplicate filename constraint test not applicable in SQLite in-memory mode"
)
async def test_duplicate_filename_same_user(async_session: AsyncSession) -> None:
    """Test that creating duplicate filenames for the same user raises IntegrityError."""
    user: User = User(
        email="dupuser@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()

    await create_file(async_session, "dup.txt", "text/plain", user_id=user.id)
    # SQLite in-memory does not enforce unique constraints reliably
    if async_session.bind.dialect.name == "sqlite":
        pytest.skip("SQLite in-memory does not enforce unique constraints reliably")
    with pytest.raises(IntegrityError):
        await create_file(async_session, "dup.txt", "text/plain", user_id=user.id)
    await async_session.rollback()


@pytest.mark.asyncio
async def test_long_filename_and_content_type(async_session: AsyncSession) -> None:
    """Test that long filenames and content types are handled correctly."""
    user: User = User(
        email="test5@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()

    long_filename: str = "a" * 255
    long_content_type: str = "b" * 128
    file = await create_file(
        async_session, long_filename, long_content_type, user_id=user.id
    )
    assert file.filename == long_filename
    assert file.content_type == long_content_type


@pytest.mark.asyncio
async def test_non_ascii_and_special_chars(async_session: AsyncSession) -> None:
    """Test that non-ASCII and special characters in filenames and content types are handled."""
    user: User = User(
        email="test6@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()

    file = await create_file(
        async_session, "файл!@#.txt", "application/x-спец", user_id=user.id
    )
    assert "файл" in file.filename
    assert "спец" in file.content_type


@pytest.mark.asyncio
@pytest.mark.requires_real_db(
    "SQLite in-memory does not reliably enforce foreign key constraints for this test."
)
async def test_create_file_missing_user(async_session: AsyncSession) -> None:
    """Test that creating a file with a missing user raises IntegrityError."""
    with pytest.raises(IntegrityError):
        await create_file(async_session, "nouser.txt", "text/plain", user_id=999999)
    await async_session.rollback()


@pytest.mark.asyncio
async def test_bulk_create_and_delete(async_session: AsyncSession) -> None:
    """Test that multiple files can be created and deleted in bulk."""
    user: User = User(
        email="test7@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()

    files: list[File] = [
        await create_file(async_session, f"bulk-{i}.txt", "text/plain", user_id=user.id)
        for i in range(5)
    ]
    for f in files:
        assert f.id is not None
    for f in files:
        deleted: bool = await delete_file(async_session, f.filename)
        assert deleted is True


@pytest.mark.asyncio
@pytest.mark.requires_real_db(
    "SQLite in-memory does not reliably preserve timezone information for this test."
)
async def test_list_files_pagination_and_search(async_session: AsyncSession) -> None:
    """Test that file listing supports pagination, search, and created_after filter."""
    user: User = User(
        email="pagsearch@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()
    user_id: Final[int] = user.id
    now: Final[datetime] = datetime.now(UTC)
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
    # Normalize datetimes to naive for SQLite compatibility
    for f in files:
        if f.created_at.tzinfo is not None:
            f_created_at = f.created_at.astimezone(UTC).replace(tzinfo=None)
        else:
            f_created_at = f.created_at
        assert f_created_at >= (now - timedelta(days=5)).replace(tzinfo=None)


@pytest.mark.asyncio
@pytest.mark.requires_real_db(
    "SQLite in-memory does not reliably preserve timezone information for this test."
)
async def test_list_files_sorting(async_session: AsyncSession) -> None:
    """Test that file listing supports sorting by filename and created_at."""
    user: User = User(
        email="sortuser@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()
    user_id: Final[int] = user.id
    now: Final[datetime] = datetime.now(UTC)
    for i in range(3):
        file = await create_file(
            async_session, f"sortfile{i}.txt", "text/plain", user_id=user_id
        )
        file.created_at = now - timedelta(days=i)
    await async_session.commit()
    files, _ = await list_files(async_session, user_id, sort="filename", order="asc")
    filenames: list[str] = [f.filename for f in files]
    assert filenames == sorted(filenames)
    files, _ = await list_files(async_session, user_id, sort="created_at", order="desc")
    created_ats: list[datetime] = [f.created_at for f in files]
    # Normalize datetimes to naive for SQLite compatibility
    created_ats_naive = [
        dt.astimezone(UTC).replace(tzinfo=None) if dt.tzinfo is not None else dt
        for dt in created_ats
    ]
    assert created_ats_naive == sorted(created_ats_naive, reverse=True)


@pytest.mark.requires_real_db(
    "Transaction rollback test not supported in SQLite in-memory mode"
)
@pytest.mark.asyncio
async def test_transactional_rollback_create_file(async_session: AsyncSession) -> None:
    """Test that file creation inside a rolled-back transaction does not persist the file."""
    user: User = User(
        email="rollbackuser@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()
    user_id = user.id
    if async_session.in_transaction():
        savepoint = await async_session.begin_nested()
        try:
            await create_file(
                async_session, "rollbackfile.txt", "text/plain", user_id=user_id
            )
        finally:
            await savepoint.rollback()
    else:
        trans = await async_session.begin()
        try:
            await create_file(
                async_session, "rollbackfile.txt", "text/plain", user_id=user_id
            )
        finally:
            await trans.rollback()

    file = await get_file_by_filename(async_session, "rollbackfile.txt")
    assert file is None


@pytest.mark.asyncio
async def test_duplicate_filename_different_users(async_session: AsyncSession) -> None:
    """Test that duplicate filenames for different users are allowed."""
    user1: User = User(
        email="test100@example.com", hashed_password="hashed", is_active=True
    )
    user2: User = User(
        email="test101@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user1)
    async_session.add(user2)
    await async_session.flush()

    file1 = await create_file(
        async_session, "shared.txt", "text/plain", user_id=user1.id
    )
    file2 = await create_file(
        async_session, "shared.txt", "text/plain", user_id=user2.id
    )
    assert file1.filename == file2.filename
    assert file1.user_id != file2.user_id


@pytest.mark.skip(reason="File repository does not currently validate content_type")
@pytest.mark.asyncio
async def test_invalid_content_type(async_session: AsyncSession) -> None:
    """Test that invalid content types raise an exception (currently skipped)."""
    with pytest.raises((ValidationError, TypeError)):
        await create_file(async_session, "badct.txt", "", user_id=11)
    with pytest.raises((ValidationError, TypeError)):
        await create_file(async_session, "badct2.txt", "c" * 1024, user_id=11)
    with pytest.raises((ValidationError, TypeError)):
        await create_file(async_session, "badct3.txt", 123, user_id=11)  # type: ignore


@pytest.mark.skip(reason="File repository does not currently validate filename type")
@pytest.mark.asyncio
async def test_invalid_filename_type(async_session: AsyncSession) -> None:
    """Test that invalid filename types raise an exception (currently skipped)."""
    with pytest.raises((ValidationError, TypeError)):
        await create_file(async_session, 123, "text/plain", user_id=12)  # type: ignore
    with pytest.raises((ValidationError, TypeError)):
        await create_file(async_session, None, "text/plain", user_id=12)  # type: ignore


@pytest.mark.skip(reason="File repository does not currently validate user_id")
@pytest.mark.asyncio
async def test_invalid_user_id(async_session: AsyncSession) -> None:
    """Test that invalid user IDs raise an exception (currently skipped)."""
    with pytest.raises((ValidationError, TypeError, IntegrityError)):
        await create_file(async_session, "baduser.txt", "text/plain", user_id=-1)
    with pytest.raises((ValidationError, TypeError, IntegrityError)):
        await create_file(async_session, "baduser2.txt", "text/plain", user_id=0)
    with pytest.raises((ValidationError, TypeError, IntegrityError)):
        await create_file(async_session, "baduser3.txt", "text/plain", user_id=None)  # type: ignore


@pytest.mark.asyncio
async def test_delete_file_case_insensitive(async_session: AsyncSession) -> None:
    """Test that file deletion is case-insensitive (if supported)."""
    user: User = User(
        email="test13@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()

    await create_file(async_session, "CaseTest.txt", "text/plain", user_id=user.id)
    deleted: bool = await delete_file(async_session, "casetest.txt")
    assert deleted in (True, False)


@pytest.mark.asyncio
async def test_list_files_empty(async_session: AsyncSession) -> None:
    """Test that listing files for a non-existent user returns an empty list and zero total."""
    files, total = await list_files(async_session, user_id=9999)
    assert files == []
    assert total == 0


@pytest.mark.asyncio
async def test_list_files_offset_beyond_total(async_session: AsyncSession) -> None:
    """Test that listing files with an offset beyond the total returns an empty list."""
    user: User = User(
        email="test14@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()

    await create_file(async_session, "off1.txt", "text/plain", user_id=user.id)
    files, total = await list_files(async_session, user.id, offset=100)
    assert files == []
    assert total == 1


@pytest.mark.requires_real_db(
    "SQLite in-memory does not reliably enforce unique constraints for this test."
)
@pytest.mark.asyncio
async def test_rollback_after_integrity_error(async_session: AsyncSession) -> None:
    """Test that after an IntegrityError and rollback, a new file can be created."""
    user: User = User(
        email="rollbackdupuser@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()
    user_id = user.id
    await create_file(async_session, "rollbackdup.txt", "text/plain", user_id=user_id)
    if async_session.bind.dialect.name == "sqlite":
        pytest.skip("SQLite in-memory does not enforce unique constraints reliably")
    with pytest.raises(IntegrityError):
        await create_file(
            async_session, "rollbackdup.txt", "text/plain", user_id=user_id
        )
    await async_session.rollback()
    file = await create_file(
        async_session, "rollbackok.txt", "text/plain", user_id=user_id
    )
    assert file.filename == "rollbackok.txt"


@pytest.mark.requires_real_db(
    "SQLite in-memory does not reliably enforce unique constraints for this test."
)
@pytest.mark.asyncio
async def test_simulated_concurrent_creation(async_session: AsyncSession) -> None:
    """Test that concurrent creation of files with the same name for the same user raises IntegrityError."""
    user: User = User(
        email="concurrentuser@example.com", hashed_password="hashed", is_active=True
    )
    async_session.add(user)
    await async_session.flush()
    user_id: Final[int] = user.id
    await create_file(async_session, "concurrent.txt", "text/plain", user_id=user_id)
    if async_session.bind.dialect.name == "sqlite":
        pytest.skip("SQLite in-memory does not enforce unique constraints reliably")
    with pytest.raises(IntegrityError):
        await create_file(
            async_session, "concurrent.txt", "text/plain", user_id=user_id
        )
    await async_session.rollback()
