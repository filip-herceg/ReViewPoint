import uuid
from datetime import UTC, datetime, timedelta

import pytest
from tests.test_templates import AsyncModelTestTemplate
from sqlalchemy.exc import IntegrityError

from src.repositories.blacklisted_token import blacklist_token, is_token_blacklisted


class TestBlacklistedTokenRepository(AsyncModelTestTemplate):
    @pytest.mark.asyncio
    async def test_blacklist_token_and_check(self):
        jti = f"testjti-repo-{uuid.uuid4()}"
        expires_at = datetime.now(UTC) + timedelta(minutes=10)
        await blacklist_token(self.async_session, jti, expires_at)
        assert await is_token_blacklisted(self.async_session, jti) is True

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_expired(self):
        jti = f"expiredjti-{uuid.uuid4()}"
        expires_at = datetime.now(UTC) - timedelta(minutes=1)
        await blacklist_token(self.async_session, jti, expires_at)
        assert await is_token_blacklisted(self.async_session, jti) is False

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_not_found(self):
        assert (
            await is_token_blacklisted(
                self.async_session, f"notfoundjti-{uuid.uuid4()}"
            )
            is False
        )

    @pytest.mark.asyncio
    async def test_duplicate_jti(self):
        jti = f"dupjti-{uuid.uuid4()}"
        expires_at = datetime.now(UTC) + timedelta(minutes=10)
        await blacklist_token(self.async_session, jti, expires_at)
        with pytest.raises(IntegrityError):
            await blacklist_token(self.async_session, jti, expires_at)
        await self.async_session.rollback()

    @pytest.mark.asyncio
    async def test_blacklist_token_naive_datetime(self):
        jti = f"naivejti-{uuid.uuid4()}"
        expires_at = datetime.now() + timedelta(minutes=10)  # naive
        await blacklist_token(self.async_session, jti, expires_at)
        assert await is_token_blacklisted(self.async_session, jti) is True

    @pytest.mark.asyncio
    async def test_blacklist_token_far_future(self):
        jti = f"futurejti-{uuid.uuid4()}"
        expires_at = datetime(2999, 1, 1, tzinfo=UTC)
        await blacklist_token(self.async_session, jti, expires_at)
        assert await is_token_blacklisted(self.async_session, jti) is True

    @pytest.mark.asyncio
    async def test_blacklist_token_immediate_expiry(self):
        jti = f"immediatejti-{uuid.uuid4()}"
        expires_at = datetime.now(UTC)
        await blacklist_token(self.async_session, jti, expires_at)
        assert await is_token_blacklisted(self.async_session, jti) is False

    @pytest.mark.asyncio
    async def test_bulk_blacklist_and_check(self):
        now = datetime.now(UTC)
        jtis = [f"bulk-{i}-{uuid.uuid4()}" for i in range(5)]
        for jti in jtis:
            await blacklist_token(self.async_session, jti, now + timedelta(minutes=5))
        for jti in jtis:
            assert await is_token_blacklisted(self.async_session, jti) is True

    @pytest.mark.asyncio
    async def test_transactional_rollback_blacklist(self):
        jti = f"rollbackjti-{uuid.uuid4()}"
        expires_at = datetime.now(UTC) + timedelta(minutes=10)

        async def op():
            await blacklist_token(self.async_session, jti, expires_at)

        await self.run_in_transaction(op)
        assert await is_token_blacklisted(self.async_session, jti) is False
