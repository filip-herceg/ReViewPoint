import pytest
from datetime import datetime, timedelta, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.blacklisted_token import blacklist_token, is_token_blacklisted
import uuid

@pytest.mark.asyncio
async def test_blacklist_token_and_check(async_session: AsyncSession):
    jti = "testjti-repo-{}".format(uuid.uuid4())
    expires_at = datetime.now(UTC) + timedelta(minutes=10)
    await blacklist_token(async_session, jti, expires_at)
    # Should be blacklisted
    assert await is_token_blacklisted(async_session, jti) is True

@pytest.mark.asyncio
async def test_is_token_blacklisted_expired(async_session: AsyncSession):
    jti = "expiredjti-{}".format(uuid.uuid4())
    expires_at = datetime.now(UTC) - timedelta(minutes=1)
    await blacklist_token(async_session, jti, expires_at)
    # Should not be blacklisted (expired)
    assert await is_token_blacklisted(async_session, jti) is False

@pytest.mark.asyncio
async def test_is_token_blacklisted_not_found(async_session: AsyncSession):
    # Should return False for unknown jti
    assert await is_token_blacklisted(async_session, "notfoundjti-{}".format(uuid.uuid4())) is False
