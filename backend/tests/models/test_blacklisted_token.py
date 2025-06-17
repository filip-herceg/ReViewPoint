# mypy: ignore-errors
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.blacklisted_token import BlacklistedToken


@pytest.mark.asyncio
async def test_blacklisted_token_model_fields(async_session: AsyncSession) -> None:
    now = datetime.now(UTC)
    token = BlacklistedToken(jti=f"testjti-{uuid.uuid4()}", expires_at=now)
    async_session.add(token)
    await async_session.flush()
    assert token.jti.startswith("testjti-")
    assert token.expires_at == now
    assert token.created_at is not None
    assert isinstance(token.created_at, datetime)


@pytest.mark.asyncio
async def test_blacklisted_token_unique_jti(async_session: AsyncSession) -> None:
    now = datetime.now(UTC) + timedelta(hours=1)
    jti = f"uniquejti-{uuid.uuid4()}"
    token1 = BlacklistedToken(jti=jti, expires_at=now)
    token2 = BlacklistedToken(jti=jti, expires_at=now)
    async_session.add(token1)
    await async_session.commit()
    async_session.add(token2)
    with pytest.raises(IntegrityError):
        await async_session.commit()
    await async_session.rollback()
