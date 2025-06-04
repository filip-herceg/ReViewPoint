import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.services import user as user_service
from src.utils.errors import ValidationError, UserAlreadyExistsError, UserNotFoundError

@pytest.mark.asyncio
async def test_register_user_success(async_session: AsyncSession):
    data = {"email": "testuser@example.com", "password": "Abc12345"}
    user = await user_service.register_user(async_session, data)
    assert user.id is not None
    assert user.email == data["email"]
    assert user.is_active
    assert user.hashed_password != data["password"]

@pytest.mark.asyncio
async def test_register_user_duplicate_email(async_session: AsyncSession):
    data = {"email": "dupe@example.com", "password": "Abc12345"}
    await user_service.register_user(async_session, data)
    with pytest.raises(UserAlreadyExistsError):
        await user_service.register_user(async_session, data)

@pytest.mark.asyncio
async def test_register_user_invalid_email(async_session: AsyncSession):
    data = {"email": "bademail", "password": "Abc12345"}
    with pytest.raises(ValidationError):
        await user_service.register_user(async_session, data)

@pytest.mark.asyncio
async def test_register_user_invalid_password(async_session: AsyncSession):
    data = {"email": "pwfail@example.com", "password": "short"}
    with pytest.raises(ValidationError):
        await user_service.register_user(async_session, data)

@pytest.mark.asyncio
async def test_authenticate_user_success(async_session: AsyncSession):
    data = {"email": "authuser@example.com", "password": "Abc12345"}
    await user_service.register_user(async_session, data)
    token = await user_service.authenticate_user(async_session, data["email"], data["password"])
    assert isinstance(token, str)
    assert len(token) > 10

@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(async_session: AsyncSession):
    data = {"email": "wrongpw@example.com", "password": "Abc12345"}
    await user_service.register_user(async_session, data)
    with pytest.raises(ValidationError):
        await user_service.authenticate_user(async_session, data["email"], "wrongpass")

@pytest.mark.asyncio
async def test_authenticate_user_not_found(async_session: AsyncSession):
    with pytest.raises(UserNotFoundError):
        await user_service.authenticate_user(async_session, "notfound@example.com", "Abc12345")

@pytest.mark.asyncio
async def test_logout_user_deactivates(async_session: AsyncSession):
    data = {"email": "logout@example.com", "password": "Abc12345"}
    user = await user_service.register_user(async_session, data)
    await user_service.logout_user(async_session, user.id)
    refreshed = await async_session.get(User, user.id)
    assert refreshed is not None and not refreshed.is_active

@pytest.mark.asyncio
async def test_is_authenticated():
    user = User(email="active@example.com", hashed_password="x", is_active=True, is_deleted=False)
    assert user_service.is_authenticated(user)
    user.is_active = False
    assert not user_service.is_authenticated(user)
    user.is_active = True
    user.is_deleted = True
    assert not user_service.is_authenticated(user)

@pytest.mark.asyncio
async def test_is_authenticated_stub_cases():
    # Active and not deleted
    user = User(email="active@example.com", hashed_password="x", is_active=True, is_deleted=False)
    assert user_service.is_authenticated(user)
    # Inactive
    user.is_active = False
    user.is_deleted = False
    assert not user_service.is_authenticated(user)
    # Deleted
    user.is_active = True
    user.is_deleted = True
    assert not user_service.is_authenticated(user)
    # Inactive and deleted
    user.is_active = False
    user.is_deleted = True
    assert not user_service.is_authenticated(user)

@pytest.mark.asyncio
async def test_logout_user_nonexistent(async_session: AsyncSession):
    # Should not raise, but should not fail if user does not exist
    try:
        await user_service.logout_user(async_session, user_id=999999)
    except Exception as e:
        pytest.fail(f"logout_user raised an exception for nonexistent user: {e}")
