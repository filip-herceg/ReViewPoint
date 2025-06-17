import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.blacklisted_token import blacklist_token, is_token_blacklisted


@pytest.mark.asyncio
async def test_blacklist_token_and_check(async_session: AsyncSession) -> None:
    jti = f"testjti-repo-{uuid.uuid4()}"
    expires_at = datetime.now(UTC) + timedelta(minutes=10)
    await blacklist_token(async_session, jti, expires_at)
    # Should be blacklisted
    assert await is_token_blacklisted(async_session, jti) is True


@pytest.mark.asyncio
async def test_is_token_blacklisted_expired(async_session: AsyncSession) -> None:
    jti = f"expiredjti-{uuid.uuid4()}"
    expires_at = datetime.now(UTC) - timedelta(minutes=1)
    await blacklist_token(async_session, jti, expires_at)
    # Should not be blacklisted (expired)
    assert await is_token_blacklisted(async_session, jti) is False


@pytest.mark.asyncio
async def test_is_token_blacklisted_not_found(async_session: AsyncSession) -> None:
    # Should return False for unknown jti
    assert (
        await is_token_blacklisted(async_session, f"notfoundjti-{uuid.uuid4()}")
        is False
    )
