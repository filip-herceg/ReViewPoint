import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.file import create_file, delete_file, get_file_by_filename


@pytest.mark.asyncio
async def test_create_file_success(async_session: AsyncSession):
    file = await create_file(async_session, "test.txt", "text/plain", user_id=1)
    assert file.filename == "test.txt"
    assert file.content_type == "text/plain"
    assert file.user_id == 1


@pytest.mark.asyncio
async def test_create_file_missing_filename(async_session: AsyncSession):
    with pytest.raises(Exception):
        await create_file(async_session, "", "text/plain", user_id=1)


@pytest.mark.asyncio
async def test_get_file_by_filename(async_session: AsyncSession):
    await create_file(async_session, "findme.txt", "text/plain", user_id=2)
    file = await get_file_by_filename(async_session, "findme.txt")
    assert file is not None
    assert file.filename == "findme.txt"


@pytest.mark.asyncio
async def test_get_file_by_filename_not_found(async_session: AsyncSession):
    file = await get_file_by_filename(async_session, "doesnotexist.txt")
    assert file is None


@pytest.mark.asyncio
async def test_delete_file(async_session: AsyncSession):
    await create_file(async_session, "todelete.txt", "text/plain", user_id=3)
    deleted = await delete_file(async_session, "todelete.txt")
    assert deleted is True
    file = await get_file_by_filename(async_session, "todelete.txt")
    assert file is None


@pytest.mark.asyncio
async def test_delete_file_not_found(async_session: AsyncSession):
    deleted = await delete_file(async_session, "notfound.txt")
    assert deleted is False
