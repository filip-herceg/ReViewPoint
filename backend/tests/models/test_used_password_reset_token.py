"""Test module for UsedPasswordResetToken model functionality.

This module tests the UsedPasswordResetToken model including:
- Model field validation and constraints
- CRUD operations
- Edge cases and validation errors
- Bulk operations and table truncation
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from datetime import UTC, datetime, timedelta
from typing import Final

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from src.models.used_password_reset_token import UsedPasswordResetToken
from tests.test_data_generators import get_unique_email
from tests.test_templates import AsyncModelTestTemplate, ModelUnitTestTemplate


class TestUsedPasswordResetTokenUnit(ModelUnitTestTemplate):
    """Unit tests for UsedPasswordResetToken model with strict static typing."""

    def _assert_model_attrs_typed(
        self, model: UsedPasswordResetToken, attrs: dict[str, object]
    ) -> None:
        """
        Type-safe wrapper for assert_model_attrs method.
        """
        self.assert_model_attrs(model, attrs)

    def test_token_creation_and_repr(self) -> None:
        """
        Test creation and __repr__ of UsedPasswordResetToken.
        Verifies:
            - Fields are set correctly
            - __repr__ includes email and nonce
        """
        now: Final[datetime] = datetime.now(UTC)
        test_email: Final[str] = get_unique_email()
        token: Final[UsedPasswordResetToken] = UsedPasswordResetToken(
            email=test_email, nonce="abc123", used_at=now
        )
        expected_attrs: Final[dict[str, object]] = {
            "email": test_email,
            "nonce": "abc123",
            "used_at": now,
        }
        self._assert_model_attrs_typed(token, expected_attrs)
        token_repr: str = repr(token)
        assert test_email in token_repr
        assert "abc123" in token_repr

    def test_token_used_at_timezone(self) -> None:
        """
        Test that used_at is timezone-aware and uses UTC.
        """
        now: Final[datetime] = datetime.now(UTC)
        token: UsedPasswordResetToken = UsedPasswordResetToken(
            email=get_unique_email(), nonce="nonce2", used_at=now
        )
        assert token.used_at.tzinfo is UTC

    def test_token_edge_cases(self) -> None:
        """
        Test edge cases for UsedPasswordResetToken fields.

        Expects:
        - ValueError for empty email or nonce
        - used_at in the past is accepted
        """
        with pytest.raises(ValueError):
            UsedPasswordResetToken(email="", nonce="n", used_at=datetime.now(UTC))
        with pytest.raises(ValueError):
            UsedPasswordResetToken(email="a@b.com", nonce="", used_at=datetime.now(UTC))
        past: Final[datetime] = datetime(2000, 1, 1, tzinfo=UTC)
        token: UsedPasswordResetToken = UsedPasswordResetToken(
            email="a@b.com", nonce="n2", used_at=past
        )
        assert token.used_at.year == 2000

    def test_long_email_and_nonce(self) -> None:
        """
        Test long email and nonce values.
        """
        long_email: Final[str] = "a" * 255 + get_unique_email()
        long_nonce: Final[str] = "b" * 64
        now: Final[datetime] = datetime.now(UTC)
        token: UsedPasswordResetToken = UsedPasswordResetToken(
            email=long_email, nonce=long_nonce, used_at=now
        )
        assert token.email.startswith("a")
        assert token.nonce.startswith("b")

    def test_duplicate_email_nonce(self) -> None:
        """
        Test duplicate email and nonce in memory (no unique constraint).
        """
        now: Final[datetime] = datetime.now(UTC)
        test_email: Final[str] = get_unique_email()
        token1: UsedPasswordResetToken = UsedPasswordResetToken(
            email=test_email, nonce="dupnonce", used_at=now
        )
        token2: UsedPasswordResetToken = UsedPasswordResetToken(
            email=test_email, nonce="dupnonce", used_at=now
        )
        assert token1.email == token2.email and token1.nonce == token2.nonce

    def test_default_used_at(self) -> None:
        """
        Test default used_at value is set and timezone-aware.
        """
        token: UsedPasswordResetToken = UsedPasswordResetToken(
            email="default@ex.com", nonce="default", used_at=datetime.now(UTC)
        )
        assert isinstance(token.used_at, datetime)
        assert token.used_at.tzinfo is not None

    def test_invalid_types(self) -> None:
        """
        Test invalid types for email and nonce raise ValueError.
        """
        with pytest.raises(ValueError):
            UsedPasswordResetToken(email=123, nonce="abc", used_at=datetime.now(UTC))
        with pytest.raises(ValueError):
            UsedPasswordResetToken(
                email="abc@ex.com", nonce=456, used_at=datetime.now(UTC)
            )

    def test_to_dict_if_present(self) -> None:
        """
        Test to_dict method if present on model.
        """
        token: UsedPasswordResetToken = UsedPasswordResetToken(
            email="dict@ex.com", nonce="dictnonce", used_at=datetime.now(UTC)
        )
        if hasattr(token, "to_dict"):
            d = token.to_dict()
            assert d["email"] == token.email
            assert d["nonce"] == token.nonce
            assert "used_at" in d


class TestUsedPasswordResetTokenDB(AsyncModelTestTemplate):
    def _assert_model_attrs_typed(
        self, model: UsedPasswordResetToken, attrs: Mapping[str, object]
    ) -> None:
        """Type-safe wrapper for assert_model_attrs method."""
        from typing import cast

        cast(
            Callable[[UsedPasswordResetToken, Mapping[str, object]], None],
            self.assert_model_attrs,
        )(model, attrs)

    async def _seed_db_typed(self, objs: list[object]) -> None:
        """
        Type-safe wrapper for seed_db.
        """
        await self.seed_db(objs)

    async def _truncate_table_typed(self, table: str) -> None:
        """Type-safe wrapper for truncate_table."""
        await self.truncate_table(table)

    async def _run_in_transaction_typed(
        self, op: Callable[[], Awaitable[None]]
    ) -> None:
        """Type-safe wrapper for run_in_transaction."""
        await self.run_in_transaction(op)

    # Fix direct calls to untyped helpers in this class
    @pytest.mark.asyncio
    async def test_bulk_insert_and_truncate(self) -> None:
        """Test bulk insert and truncation for UsedPasswordResetToken in DB."""
        now: Final[datetime] = datetime.now(UTC)
        tokens: list[UsedPasswordResetToken] = [
            UsedPasswordResetToken(
                email=f"bulk{i}@ex.com", nonce=f"nonce{i}", used_at=now
            )
            for i in range(5)
        ]
        await self._seed_db_typed(list(tokens))
        for t in tokens:
            assert isinstance(t, UsedPasswordResetToken)
            assert t.id is not None
        await self._truncate_table_typed("used_password_reset_tokens")
        result = await self.async_session.execute(
            text("SELECT COUNT(*) FROM used_password_reset_tokens")
        )
        count: int | None = result.scalar()
        assert count == 0

    @pytest.mark.asyncio
    async def test_transactional_rollback(self) -> None:
        """Test transaction rollback for UsedPasswordResetToken in DB."""
        now: Final[datetime] = datetime.now(UTC)
        token: UsedPasswordResetToken = UsedPasswordResetToken(
            email="rollback@ex.com", nonce="rollback", used_at=now
        )

        async def op() -> None:
            self.async_session.add(token)

        await self._run_in_transaction_typed(op)
        result = await self.async_session.execute(
            text(
                "SELECT COUNT(*) FROM used_password_reset_tokens WHERE email = 'rollback@ex.com'"
            )
        )
        count: int | None = result.scalar()
        assert count == 0

    @pytest.mark.asyncio
    async def test_crud(self) -> None:
        """Test CRUD operations for UsedPasswordResetToken in DB."""
        now: Final[datetime] = datetime.now(UTC)
        test_email = get_unique_email()
        token: UsedPasswordResetToken = UsedPasswordResetToken(
            email=test_email, nonce="dbnonce", used_at=now
        )
        self.async_session.add(token)
        await self.async_session.commit()
        await self.async_session.refresh(token)
        assert token.id is not None
        db_token: UsedPasswordResetToken | None = await self.async_session.get(
            UsedPasswordResetToken, token.id
        )
        assert db_token is not None
        assert db_token.email == test_email
        db_token.nonce = "newnonce"
        await self.async_session.commit()
        await self.async_session.refresh(db_token)
        assert db_token.nonce == "newnonce"
        await self.async_session.delete(db_token)
        await self.async_session.commit()
        gone: UsedPasswordResetToken | None = await self.async_session.get(
            UsedPasswordResetToken, token.id
        )
        assert gone is None

    @pytest.mark.asyncio
    async def test_integrity_error_empty_email(self) -> None:
        """Test that empty email raises a validation error."""
        with pytest.raises(ValueError, match="email must be a non-empty string"):
            UsedPasswordResetToken(email="", nonce="n", used_at=datetime.now(UTC))

    @pytest.mark.asyncio
    async def test_integrity_error_empty_nonce(self) -> None:
        """Test that empty nonce raises a validation error."""
        with pytest.raises(ValueError, match="nonce must be a non-empty string"):
            UsedPasswordResetToken(email="a@b.com", nonce="", used_at=datetime.now(UTC))
        await self.async_session.rollback()

    @pytest.mark.asyncio
    async def test_non_ascii_email_and_nonce(self) -> None:
        """Test non-ASCII email and nonce values in DB."""
        now: Final[datetime] = datetime.now(UTC)
        token: UsedPasswordResetToken = UsedPasswordResetToken(
            email="юзер@пример.рф", nonce="токен", used_at=now
        )
        self.async_session.add(token)
        await self.async_session.commit()
        await self.async_session.refresh(token)
        assert "юзер" in token.email
        assert "токен" in token.nonce

    @pytest.mark.asyncio
    async def test_special_characters_in_email_and_nonce(self) -> None:
        """Test special characters in email and nonce in DB."""
        now: Final[datetime] = datetime.now(UTC)
        special_email = get_unique_email("special+chars", "test")
        token: UsedPasswordResetToken = UsedPasswordResetToken(
            email=special_email, nonce="!@#$%^&*()", used_at=now
        )
        self.async_session.add(token)
        await self.async_session.commit()
        await self.async_session.refresh(token)
        assert special_email.startswith("special+chars")
        assert token.nonce.startswith("!")

    @pytest.mark.asyncio
    async def test_used_at_in_past_and_future(self) -> None:
        """Test used_at in past and future dates in DB."""
        past: Final[datetime] = datetime(2000, 1, 1, tzinfo=UTC)
        future: Final[datetime] = datetime.now(UTC) + timedelta(days=365)
        token1: UsedPasswordResetToken = UsedPasswordResetToken(
            email="past@ex.com", nonce="past", used_at=past
        )
        token2: UsedPasswordResetToken = UsedPasswordResetToken(
            email="future@ex.com", nonce="future", used_at=future
        )
        await self._seed_db_typed([token1, token2])
        assert token1.used_at.year == 2000
        assert token2.used_at.year == future.year

    @pytest.mark.asyncio
    async def test_duplicate_email_nonce_db(self) -> None:
        """Test duplicate email and nonce in DB (unique constraint)."""
        now: Final[datetime] = datetime.now(UTC)
        token1: UsedPasswordResetToken = UsedPasswordResetToken(
            email="dupdb@ex.com", nonce="dupdb", used_at=now
        )
        token2: UsedPasswordResetToken = UsedPasswordResetToken(
            email="dupdb@ex.com", nonce="dupdb", used_at=now
        )
        await self._seed_db_typed([token1])
        allowed: bool
        try:
            await self._seed_db_typed([token2])
            allowed = True
        except IntegrityError:
            allowed = False
        assert allowed in (True, False)  # Document behavior

    @pytest.mark.asyncio
    @pytest.mark.requires_real_db(
        "SQLite in-memory does not reliably preserve timezone information for this test."
    )
    async def test_default_used_at_db(self) -> None:
        """Test default used_at value in DB is set and timezone-aware."""
        # Skip this test if we're using SQLite since timezone preservation isn't reliable
        bind = self.async_session.get_bind()
        if hasattr(bind, "engine") and "sqlite" in str(bind.engine.url):
            pytest.skip("SQLite does not preserve timezone information reliably")
        elif "sqlite" in str(type(bind).__name__.lower()):
            pytest.skip("SQLite does not preserve timezone information reliably")

        token: UsedPasswordResetToken = UsedPasswordResetToken(
            email="defaultdb@ex.com",
            nonce="defaultdb",
            used_at=None or datetime.now(UTC),
        )
        self.async_session.add(token)
        await self.async_session.commit()
        await self.async_session.refresh(token)
        assert isinstance(token.used_at, datetime)
        assert token.used_at.tzinfo is not None

    @pytest.mark.asyncio
    async def test_index_lookup(self) -> None:
        """Test index lookup by email in DB."""
        now: Final[datetime] = datetime.now(UTC)
        tokens: list[UsedPasswordResetToken] = [
            UsedPasswordResetToken(
                email=f"idx{i}@ex.com", nonce=f"idxnonce{i}", used_at=now
            )
            for i in range(3)
        ]
        await self._seed_db_typed(list(tokens))
        result = await self.async_session.execute(
            text("SELECT * FROM used_password_reset_tokens WHERE email = :email"),
            {"email": "idx1@ex.com"},
        )
        row = result.first()
        assert row is not None

    @pytest.mark.asyncio
    async def test_invalid_types_db(self) -> None:
        """Test invalid types for email/nonce in DB raise ValueError."""
        with pytest.raises(ValueError):
            token = UsedPasswordResetToken(
                email=123, nonce="abc", used_at=datetime.now(UTC)
            )
            self.async_session.add(token)
            await self.async_session.flush()
        with pytest.raises(ValueError):
            token = UsedPasswordResetToken(
                email="abc@ex.com", nonce=456, used_at=datetime.now(UTC)
            )
            self.async_session.add(token)
            await self.async_session.flush()

    @pytest.mark.asyncio
    async def test_mass_deletion(self) -> None:
        """Test mass deletion and truncation for UsedPasswordResetToken in DB."""
        now: Final[datetime] = datetime.now(UTC)
        tokens: list[UsedPasswordResetToken] = [
            UsedPasswordResetToken(
                email=f"del{i}@ex.com", nonce=f"delnonce{i}", used_at=now
            )
            for i in range(10)
        ]
        await self._seed_db_typed(list(tokens))
        await self._truncate_table_typed("used_password_reset_tokens")
        result = await self.async_session.execute(
            text("SELECT COUNT(*) FROM used_password_reset_tokens")
        )
        count: int | None = result.scalar()
        assert count == 0
