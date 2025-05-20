import pytest
from backend.models.user import User
from sqlalchemy import select


@pytest.mark.asyncio
async def test_user_crud(async_session):
    # Create
    user = User(email="test@example.com", hashed_password="hashed", is_active=True)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    assert user.id is not None

    # Read
    stmt = select(User).where(User.email == "test@example.com")
    result = await async_session.execute(stmt)
    user_db = result.scalar_one()
    assert user_db.email == "test@example.com"

    # Update
    user_db.is_active = False
    await async_session.commit()
    await async_session.refresh(user_db)
    assert user_db.is_active is False

    # Delete
    await async_session.delete(user_db)
    await async_session.commit()
    result = await async_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    assert result.scalar() is None
