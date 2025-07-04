import uuid
from datetime import UTC, datetime, timedelta

import pytest

from src.models.blacklisted_token import BlacklistedToken
from tests.test_templates import AsyncModelTestTemplate


class TestBlacklistedTokenModel(AsyncModelTestTemplate):
    @pytest.mark.asyncio
    async def test_blacklisted_token_model_fields(self):
        now = datetime.now(UTC)
        token = BlacklistedToken(jti=f"testjti-{uuid.uuid4()}", expires_at=now)
        self.async_session.add(token)
        await self.async_session.flush()
        self.assert_model_attrs(token, {"jti": token.jti, "expires_at": now})
        assert token.created_at is not None
        assert isinstance(token.created_at, datetime)

    @pytest.mark.asyncio
    async def test_blacklisted_token_unique_jti(self):
        now = datetime.now(UTC) + timedelta(hours=1)
        jti = f"uniquejti-{uuid.uuid4()}"
        token1 = BlacklistedToken(jti=jti, expires_at=now)
        token2 = BlacklistedToken(jti=jti, expires_at=now)
        await self.seed_db([token1])
        await self.assert_integrity_error(token2)

    @pytest.mark.asyncio
    async def test_blacklisted_token_to_dict_and_repr(self):
        now = datetime.now(UTC)
        jti = f"dictjti-{uuid.uuid4()}"
        token = BlacklistedToken(jti=jti, expires_at=now)
        await self.seed_db([token])
        d = token.to_dict()
        assert d["jti"] == jti
        assert d["expires_at"] == now
        assert "created_at" in d
        self.assert_repr(token, "BlacklistedToken")

    @pytest.mark.asyncio
    async def test_blacklisted_token_expired(self):
        now = datetime.now(UTC) - timedelta(hours=1)
        token = BlacklistedToken(jti=f"expiredjti-{uuid.uuid4()}", expires_at=now)
        await self.seed_db([token])
        assert token.expires_at < datetime.now(UTC)

    @pytest.mark.asyncio
    async def test_bulk_insert_and_truncate(self):
        now = datetime.now(UTC) + timedelta(hours=2)
        tokens = [
            BlacklistedToken(jti=f"bulk-{i}-{uuid.uuid4()}", expires_at=now)
            for i in range(5)
        ]
        await self.seed_db(tokens)
        for t in tokens:
            assert t.id is not None
        await self.truncate_table("blacklisted_tokens")
        # After truncate, table should be empty
        from sqlalchemy import text

        result = await self.async_session.execute(
            text("SELECT COUNT(*) FROM blacklisted_tokens")
        )
        count = result.scalar()
        assert count == 0

    @pytest.mark.asyncio
    async def test_transactional_rollback(self):
        now = datetime.now(UTC) + timedelta(hours=3)
        token = BlacklistedToken(jti=f"rollback-{uuid.uuid4()}", expires_at=now)

        # Manually create a transaction that we can control
        from sqlalchemy import text

        # Start a new transaction manually
        await self.async_session.execute(text("BEGIN"))
        try:
            self.async_session.add(token)
            await self.async_session.flush()  # Send SQL but don't commit
            # Rollback manually
            await self.async_session.execute(text("ROLLBACK"))
        except Exception:
            await self.async_session.execute(text("ROLLBACK"))

        # After rollback, token should not be in DB
        result = await self.async_session.execute(
            text(f"SELECT COUNT(*) FROM blacklisted_tokens WHERE jti = '{token.jti}'")
        )
        count = result.scalar()
        assert count == 0
