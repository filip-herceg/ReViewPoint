import pytest
from backend.models.file import File
from backend.models.user import User
from sqlalchemy import select


@pytest.mark.asyncio
async def test_file_crud(async_session):
    # Create user
    user = User(email="fileuser@example.com", hashed_password="hashed", is_active=True)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    # Create file
    file = File(filename="doc.txt", content_type="text/plain", user_id=user.id)
    async_session.add(file)
    await async_session.commit()
    await async_session.refresh(file)
    assert file.id is not None
    assert file.user_id == user.id

    # Read
    stmt = select(File).where(File.filename == "doc.txt")
    result = await async_session.execute(stmt)
    file_db = result.scalar_one()
    assert file_db.filename == "doc.txt"
    assert file_db.user_id == user.id

    # Update
    file_db.content_type = "application/pdf"
    await async_session.commit()
    await async_session.refresh(file_db)
    assert file_db.content_type == "application/pdf"

    # Delete
    await async_session.delete(file_db)
    await async_session.commit()
    result = await async_session.execute(select(File).where(File.filename == "doc.txt"))
    assert result.scalar() is None
