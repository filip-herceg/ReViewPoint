import pytest
from datetime import datetime, timedelta, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.blacklisted_token import BlacklistedToken
import uuid


@pytest.mark.asyncio
async def test_blacklisted_token_model_fields(async_session: AsyncSession):
    now = datetime.now(UTC)
    token = BlacklistedToken(jti="testjti-{}".format(uuid.uuid4()), expires_at=now)
    async_session.add(token)
    await async_session.flush()
    assert token.jti.startswith("testjti-")
    assert token.expires_at == now
    assert token.created_at is not None
    assert isinstance(token.created_at, datetime)


@pytest.mark.asyncio
async def test_blacklisted_token_unique_jti(async_session: AsyncSession):
    now = datetime.now(UTC) + timedelta(hours=1)
    jti = "uniquejti-{}".format(uuid.uuid4())
    token1 = BlacklistedToken(jti=jti, expires_at=now)
    token2 = BlacklistedToken(jti=jti, expires_at=now)
    async_session.add(token1)
    await async_session.commit()
    async_session.add(token2)
    with pytest.raises(Exception):
        await async_session.commit()
    await async_session.rollback()
