import pytest
from pytest_asyncio import fixture
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.repositories import user as user_repo
from src.repositories.user import user_action_limiter
from src.utils.errors import (
    RateLimitExceededError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)


@fixture(autouse=True)
async def cleanup_users(async_session: AsyncSession) -> None:
    await async_session.execute(delete(User))
    await async_session.commit()

    # Reset rate limiter between tests
    user_action_limiter.reset()


@pytest.mark.asyncio
async def test_error_handling_utilities(async_session: AsyncSession) -> None:
    create_user_with_validation = user_repo.create_user_with_validation
    sensitive_user_action = user_repo.sensitive_user_action
    safe_get_user_by_id = user_repo.safe_get_user_by_id

    # ValidationError
    with pytest.raises(ValidationError):
        await create_user_with_validation(async_session, "bademail", "pw")

    # UserAlreadyExistsError
    user = await create_user_with_validation(async_session, "exists@b.com", "Abc12345")
    user_id = user.id
    with pytest.raises(UserAlreadyExistsError):
        await create_user_with_validation(async_session, "exists@b.com", "Abc12345")

    # UserNotFoundError
    with pytest.raises(UserNotFoundError):
        await safe_get_user_by_id(async_session, 999999)

    # RateLimitExceededError
    for _ in range(5):
        await sensitive_user_action(async_session, user_id, "test")
    with pytest.raises(RateLimitExceededError):
        await sensitive_user_action(async_session, user_id, "test")
