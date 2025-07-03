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
from tests.test_templates import UtilityUnitTestTemplate


@fixture(autouse=True)
async def cleanup_users(async_session: AsyncSession) -> None:
    await async_session.execute(delete(User))
    await async_session.commit()
    user_action_limiter.reset()


class TestErrorHandlingUtilities(UtilityUnitTestTemplate):
    @pytest.mark.asyncio
    async def test_error_handling_utilities(self, async_session: AsyncSession):
        create_user_with_validation = user_repo.create_user_with_validation
        sensitive_user_action = user_repo.sensitive_user_action
        safe_get_user_by_id = user_repo.safe_get_user_by_id

        # ValidationError
        async def create_invalid_user():
            await create_user_with_validation(async_session, "bademail", "pw")

        await self.assert_async_raises(ValidationError, create_invalid_user)

        # UserAlreadyExistsError
        user = await create_user_with_validation(
            async_session, "exists@b.com", "Abc12345"
        )
        user_id = user.id

        async def create_duplicate_user():
            await create_user_with_validation(async_session, "exists@b.com", "Abc12345")

        await self.assert_async_raises(UserAlreadyExistsError, create_duplicate_user)

        # UserNotFoundError
        async def get_nonexistent_user():
            await safe_get_user_by_id(async_session, 999999)

        await self.assert_async_raises(UserNotFoundError, get_nonexistent_user)

        # RateLimitExceededError
        for _ in range(5):
            await sensitive_user_action(async_session, user_id, "test")

        async def exceed_rate_limit():
            await sensitive_user_action(async_session, user_id, "test")

        await self.assert_async_raises(RateLimitExceededError, exceed_rate_limit)
