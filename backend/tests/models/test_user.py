# type: ignore
from datetime import datetime

import pytest
from backend.models.user import User
from backend.repositories.user import UserRepository
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


@pytest.mark.asyncio
async def test_user_repository_crud(async_session):
    """Test async CRUD operations via UserRepository."""
    # Create
    user = await UserRepository.create_user(
        async_session, email="repo@example.com", hashed_password="hashed"
    )
    assert user.id is not None
    assert user.email == "repo@example.com"

    # Read by email
    user_db = await UserRepository.get_user_by_email(async_session, "repo@example.com")
    assert user_db is not None
    assert user_db.email == "repo@example.com"

    # Update
    updated = await UserRepository.update_user(async_session, user_db, is_active=False)
    assert updated.is_active is False

    # Delete
    await UserRepository.delete_user(async_session, updated)
    user_none = await UserRepository.get_user_by_email(
        async_session, "repo@example.com"
    )
    assert user_none is None


@pytest.mark.asyncio
def _make_users(async_session, count=5, **kwargs):
    """Helper to create multiple users."""
    users = [
        User(
            email=f"user{n}@example.com", hashed_password="pw", is_active=True, **kwargs
        )
        for n in range(count)
    ]
    async_session.add_all(users)
    return users


@pytest.mark.asyncio
async def test_soft_delete_and_restore(async_session):
    user = User(email="soft@example.com", hashed_password="pw", is_active=True)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    await UserRepository.soft_delete_user(async_session, user)
    assert user.is_deleted
    # Should not be returned by normal queries
    assert await UserRepository.get_user_by_email(async_session, user.email) is None
    # Restore
    await UserRepository.restore_soft_deleted_user(async_session, user)
    assert not user.is_deleted
    assert await UserRepository.get_user_by_email(async_session, user.email) is not None


@pytest.mark.asyncio
async def test_bulk_create_and_bulk_soft_delete(async_session):
    users_data = [
        {"email": f"bulk{i}@ex.com", "hashed_password": "pw", "is_active": True}
        for i in range(3)
    ]
    users = await UserRepository.bulk_create_users(async_session, users_data)
    assert len(users) == 3
    ids = [u.id for u in users]
    count = await UserRepository.bulk_soft_delete_users(async_session, ids)
    assert count == 3
    # All should be soft deleted
    for u in users:
        await async_session.refresh(u)
        assert u.is_deleted


@pytest.mark.asyncio
async def test_bulk_update_and_bulk_restore(async_session):
    users = await UserRepository.bulk_create_users(
        async_session,
        [
            {"email": f"up{i}@ex.com", "hashed_password": "pw", "is_active": True}
            for i in range(2)
        ],
    )
    ids = [u.id for u in users]
    n = await UserRepository.bulk_update_users(async_session, ids, {"is_active": False})
    assert n == 2
    for u in users:
        await async_session.refresh(u)
        assert not u.is_active
    # Soft delete and restore
    await UserRepository.bulk_soft_delete_users(async_session, ids)
    n = await UserRepository.bulk_restore_users(async_session, ids)
    assert n == 2
    for u in users:
        await async_session.refresh(u)
        assert not u.is_deleted


@pytest.mark.asyncio
async def test_bulk_permanent_delete(async_session):
    users = await UserRepository.bulk_create_users(
        async_session,
        [
            {"email": f"del{i}@ex.com", "hashed_password": "pw", "is_active": True}
            for i in range(2)
        ],
    )
    ids = [u.id for u in users]
    n = await UserRepository.bulk_permanent_delete_users(async_session, ids)
    assert n == 2
    for uid in ids:
        assert await UserRepository.get_user_by_id(async_session, uid) is None


@pytest.mark.asyncio
async def test_search_and_filter_helpers(async_session):
    await UserRepository.bulk_create_users(
        async_session,
        [
            {"email": f"findme{i}@ex.com", "hashed_password": "pw", "is_active": True}
            for i in range(3)
        ],
    )
    found = await UserRepository.search_users_by_email(async_session, "findme")
    assert len(found) == 3
    now = datetime.utcnow()
    filtered = await UserRepository.filter_users_by_registration_date(
        async_session, now.replace(year=now.year - 1), now.replace(year=now.year + 1)
    )
    assert len(filtered) >= 3


@pytest.mark.asyncio
async def test_get_users_by_ids_and_status(async_session):
    users = await UserRepository.bulk_create_users(
        async_session,
        [
            {
                "email": f"stat{i}@ex.com",
                "hashed_password": "pw",
                "is_active": bool(i % 2),
            }
            for i in range(4)
        ],
    )
    ids = [u.id for u in users]
    by_ids = await UserRepository.get_users_by_ids(async_session, ids)
    assert len(by_ids) == 4
    active = await UserRepository.get_users_by_status(async_session, True)
    inactive = await UserRepository.get_users_by_status(async_session, False)
    assert all(u.is_active for u in active)
    assert all(not u.is_active for u in inactive)


@pytest.mark.asyncio
async def test_get_users_by_email_domain_and_deleted(async_session):
    await UserRepository.bulk_create_users(
        async_session,
        [
            {
                "email": f"dom{i}@somedomain.com",
                "hashed_password": "pw",
                "is_active": True,
            }
            for i in range(2)
        ],
    )
    users = await UserRepository.get_users_by_email_domain(
        async_session, "somedomain.com"
    )
    assert len(users) == 2
    # Soft delete one
    await UserRepository.soft_delete_user(async_session, users[0])
    deleted = await UserRepository.get_deleted_users(async_session)
    assert any(u.id == users[0].id for u in deleted)


@pytest.mark.asyncio
async def test_recently_updated_and_pagination(async_session):
    await UserRepository.bulk_create_users(
        async_session,
        [
            {"email": f"recent{i}@ex.com", "hashed_password": "pw", "is_active": True}
            for i in range(5)
        ],
    )
    now = datetime.utcnow()
    recents = await UserRepository.get_recently_updated_users(
        async_session, now.replace(year=now.year - 1)
    )
    assert len(recents) >= 5
    paged = await UserRepository.get_users_with_pagination(
        async_session, skip=0, limit=2
    )
    assert len(paged) == 2


@pytest.mark.asyncio
async def test_update_user_field_and_activate_deactivate(async_session):
    user = await UserRepository.create_user(
        async_session, email="field@ex.com", hashed_password="pw"
    )
    await UserRepository.update_user_field(
        async_session, user, "email", "field2@ex.com"
    )
    assert user.email == "field2@ex.com"
    await UserRepository.deactivate_user(async_session, user)
    assert not user.is_active
    await UserRepository.activate_user(async_session, user)
    assert user.is_active


@pytest.mark.asyncio
async def test_stubs_and_not_implemented(async_session):
    user = await UserRepository.create_user(
        async_session, email="stub@ex.com", hashed_password="pw"
    )
    # Profile info stub
    with pytest.raises(NotImplementedError):
        await UserRepository.get_users_with_profile_info(async_session)
    # No login stub
    with pytest.raises(NotImplementedError):
        await UserRepository.get_users_with_no_login_since(
            async_session, datetime.utcnow()
        )
    # Anonymize stub
    with pytest.raises(NotImplementedError):
        await UserRepository.anonymize_user(async_session, user)
    # Export stub
    with pytest.raises(NotImplementedError):
        await UserRepository.export_users(async_session)
    # Advanced search stub
    with pytest.raises(NotImplementedError):
        await UserRepository.advanced_search(async_session, {})


@pytest.mark.asyncio
async def test_get_user_by_id_cached(async_session):
    user = await UserRepository.create_user(
        async_session, email="cache@ex.com", hashed_password="pw"
    )
    cached = await UserRepository.get_user_by_id_cached(async_session, user.id)
    assert cached.id == user.id
