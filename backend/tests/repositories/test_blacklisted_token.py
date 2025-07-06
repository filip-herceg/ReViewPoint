
import uuid
from datetime import UTC, datetime, timedelta
from typing import Final
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.repositories.blacklisted_token import blacklist_token, is_token_blacklisted

class TestBlacklistedTokenRepository:
    @pytest.mark.asyncio
    async def test_blacklist_token_and_check(self: "TestBlacklistedTokenRepository", async_session: AsyncSession) -> None:
        """Test that a token can be blacklisted and is detected as blacklisted."""
        jti: Final[str] = f"testjti-repo-{uuid.uuid4()}"
        expires_at: Final[datetime] = datetime.now(UTC) + timedelta(minutes=10)
        await blacklist_token(async_session, jti, expires_at)
        assert await is_token_blacklisted(async_session, jti) is True

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_expired(self: "TestBlacklistedTokenRepository", async_session: AsyncSession) -> None:
        """Test that an expired blacklisted token is not considered blacklisted."""
        jti: Final[str] = f"expiredjti-{uuid.uuid4()}"
        expires_at: Final[datetime] = datetime.now(UTC) - timedelta(minutes=1)
        await blacklist_token(async_session, jti, expires_at)
        assert await is_token_blacklisted(async_session, jti) is False

    @pytest.mark.asyncio
    async def test_is_token_blacklisted_not_found(self: "TestBlacklistedTokenRepository", async_session: AsyncSession) -> None:
        """Test that a non-existent token is not considered blacklisted."""
        jti: Final[str] = f"notfoundjti-{uuid.uuid4()}"
        assert await is_token_blacklisted(async_session, jti) is False

    @pytest.mark.asyncio
    async def test_duplicate_jti(self: "TestBlacklistedTokenRepository", async_session: AsyncSession) -> None:
        """Test that inserting a duplicate JTI raises an IntegrityError."""
        jti: Final[str] = f"dupjti-{uuid.uuid4()}"
        expires_at: Final[datetime] = datetime.now(UTC) + timedelta(minutes=10)
        await blacklist_token(async_session, jti, expires_at)
        with pytest.raises(IntegrityError):
            await blacklist_token(async_session, jti, expires_at)
            await async_session.flush()  # Ensure constraint is checked
        await async_session.rollback()

    @pytest.mark.asyncio
    async def test_blacklist_token_naive_datetime(self: "TestBlacklistedTokenRepository", async_session: AsyncSession) -> None:
        """Test that a token can be blacklisted with a naive datetime (no tzinfo)."""
        jti: Final[str] = f"naivejti-{uuid.uuid4()}"
        expires_at: Final[datetime] = datetime.now() + timedelta(minutes=10)  # naive
        await blacklist_token(async_session, jti, expires_at)
        assert await is_token_blacklisted(async_session, jti) is True

    @pytest.mark.asyncio
    async def test_blacklist_token_far_future(self: "TestBlacklistedTokenRepository", async_session: AsyncSession) -> None:
        """Test that a token with a far-future expiry is considered blacklisted."""
        jti: Final[str] = f"futurejti-{uuid.uuid4()}"
        expires_at: Final[datetime] = datetime(2999, 1, 1, tzinfo=UTC)
        await blacklist_token(async_session, jti, expires_at)
        assert await is_token_blacklisted(async_session, jti) is True

    @pytest.mark.asyncio
    async def test_blacklist_token_immediate_expiry(self: "TestBlacklistedTokenRepository", async_session: AsyncSession) -> None:
        """Test that a token with immediate expiry is not considered blacklisted."""
        jti: Final[str] = f"immediatejti-{uuid.uuid4()}"
        expires_at: Final[datetime] = datetime.now(UTC)
        await blacklist_token(async_session, jti, expires_at)
        assert await is_token_blacklisted(async_session, jti) is False

    @pytest.mark.asyncio
    async def test_bulk_blacklist_and_check(self: "TestBlacklistedTokenRepository", async_session: AsyncSession) -> None:
        """Test that multiple tokens can be blacklisted and checked in bulk."""
        now: Final[datetime] = datetime.now(UTC)
        jtis: list[str] = [f"bulk-{i}-{uuid.uuid4()}" for i in range(5)]
        for jti in jtis:
            await blacklist_token(async_session, jti, now + timedelta(minutes=5))
        for jti in jtis:
            assert await is_token_blacklisted(async_session, jti) is True

    @pytest.mark.asyncio
    @pytest.mark.requires_real_db(
        "Transaction rollback test not supported in SQLite in-memory mode"
    )
    async def test_transactional_rollback_blacklist(self: "TestBlacklistedTokenRepository", async_session: AsyncSession) -> None:
        """Test that blacklisting a token inside a rolled-back transaction does not persist the token.
        Skipped for SQLite in-memory mode where rollback is not supported.
        """
        jti: Final[str] = f"rollbackjti-{uuid.uuid4()}"
        expires_at: Final[datetime] = datetime.now(UTC) + timedelta(minutes=10)
        await blacklist_token(async_session, jti, expires_at)
        await async_session.rollback()
        assert await is_token_blacklisted(async_session, jti) is False
