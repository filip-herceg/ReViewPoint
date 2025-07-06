"""Test module for BlacklistedToken model functionality.

This module tests the BlacklistedToken model including:
- Model field validation and constraints
- Unique constraint on JTI (JWT ID)
- Database operations (insert, update, delete)
- Model serialization with to_dict method
- Transaction handling and rollback scenarios
- Bulk operations and table truncation
"""
from __future__ import annotations

import uuid
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from typing import Any, Final

import pytest
from sqlalchemy import Result, text

from src.models.blacklisted_token import BlacklistedToken
from tests.test_templates import AsyncModelTestTemplate


class TestBlacklistedTokenModel(AsyncModelTestTemplate):
    """Test class for BlacklistedToken model functionality."""

    async def _seed_db_typed(self, objs: list[BlacklistedToken]) -> None:
        """Type-safe wrapper for seed_db method."""
        from typing import cast
        await cast(Any, self.seed_db)(objs)

    async def _assert_integrity_error_typed(self, obj: BlacklistedToken) -> None:
        """Type-safe wrapper for assert_integrity_error method."""
        from typing import cast
        await cast(Any, self.assert_integrity_error)(obj)

    async def _truncate_table_typed(self, table: str) -> None:
        """Type-safe wrapper for truncate_table method."""
        from typing import cast
        await cast(Any, self.truncate_table)(table)

    def _assert_model_attrs_typed(self, model: BlacklistedToken, attrs: dict[str, Any]) -> None:
        """Type-safe wrapper for assert_model_attrs method."""
        from typing import cast
        cast(Any, self.assert_model_attrs)(model, attrs)

    def _assert_repr_typed(self, obj: BlacklistedToken, class_name: str) -> None:
        """Type-safe wrapper for assert_repr method."""
        from typing import cast
        cast(Any, self.assert_repr)(obj, class_name)

    @pytest.mark.asyncio
    async def test_blacklisted_token_model_fields(self) -> None:
        """Test that BlacklistedToken model fields are properly set and validated.

        This test verifies that:
        - JTI and expires_at fields are correctly assigned
        - Model can be added to session and flushed
        - created_at timestamp is automatically set by BaseModel
        - Field values match expected values after database interaction
        """
        now: datetime = datetime.now(UTC)
        jti_value: str = f"testjti-{uuid.uuid4()}"
        token: BlacklistedToken = BlacklistedToken(jti=jti_value, expires_at=now)

        self.async_session.add(token)
        await self.async_session.flush()

        expected_attrs: Final[dict[str, Any]] = {"jti": token.jti, "expires_at": now}
        self._assert_model_attrs_typed(token, expected_attrs)
        assert token.created_at is not None
        assert isinstance(token.created_at, datetime)

    @pytest.mark.asyncio
    async def test_blacklisted_token_unique_jti(self) -> None:
        """Test that JTI field has unique constraint enforced.

        This test verifies that:
        - Multiple tokens with the same JTI cannot be inserted
        - Database integrity constraint is properly enforced
        - IntegrityError is raised on constraint violation
        """
        expires_time: datetime = datetime.now(UTC) + timedelta(hours=1)
        jti_value: str = f"uniquejti-{uuid.uuid4()}"

        token1: BlacklistedToken = BlacklistedToken(jti=jti_value, expires_at=expires_time)
        token2: BlacklistedToken = BlacklistedToken(jti=jti_value, expires_at=expires_time)

        await self._seed_db_typed([token1])
        await self._assert_integrity_error_typed(token2)

    @pytest.mark.asyncio
    async def test_blacklisted_token_to_dict_and_repr(self) -> None:
        """Test model serialization and string representation.

        This test verifies that:
        - to_dict method returns correct dictionary representation
        - All expected fields are present in dictionary
        - Model __repr__ method includes class name
        """
        now: datetime = datetime.now(UTC)
        jti_value: str = f"dictjti-{uuid.uuid4()}"
        token: BlacklistedToken = BlacklistedToken(jti=jti_value, expires_at=now)

        await self._seed_db_typed([token])

        token_dict: Mapping[str, Any] = token.to_dict()
        assert token_dict["jti"] == jti_value
        assert token_dict["expires_at"] == now
        assert "created_at" in token_dict

        self._assert_repr_typed(token, "BlacklistedToken")

    @pytest.mark.asyncio
    async def test_blacklisted_token_expired(self) -> None:
        """Test handling of expired tokens.

        This test verifies that:
        - Tokens can be created with past expiration dates
        - Expiration time comparison works correctly
        - Expired tokens are properly identified
        """
        past_time: datetime = datetime.now(UTC) - timedelta(hours=1)
        jti_value: str = f"expiredjti-{uuid.uuid4()}"
        token: BlacklistedToken = BlacklistedToken(jti=jti_value, expires_at=past_time)

        await self._seed_db_typed([token])

        current_time: datetime = datetime.now(UTC)
        assert token.expires_at < current_time

    @pytest.mark.asyncio
    async def test_bulk_insert_and_truncate(self) -> None:
        """Test bulk database operations and table truncation.

        This test verifies that:
        - Multiple tokens can be inserted in bulk
        - All tokens receive database IDs after insertion
        - Table truncation removes all records
        - Record count is correctly zero after truncation
        """
        future_time: datetime = datetime.now(UTC) + timedelta(hours=2)
        tokens: list[BlacklistedToken] = [
            BlacklistedToken(jti=f"bulk-{i}-{uuid.uuid4()}", expires_at=future_time)
            for i in range(5)
        ]

        await self._seed_db_typed(tokens)

        # Verify all tokens have IDs
        for token in tokens:
            assert token.id is not None

        # Truncate table and verify it's empty
        await self._truncate_table_typed("blacklisted_tokens")

        result: Result[tuple[int]] = await self.async_session.execute(
            text("SELECT COUNT(*) FROM blacklisted_tokens")
        )
        count: int | None = result.scalar()
        assert count == 0

    @pytest.mark.asyncio
    async def test_transactional_rollback(self) -> None:
        """Test transaction rollback functionality.

        This test verifies that:
        - Manual transaction control works correctly
        - Changes are properly rolled back on rollback
        - Token is not persisted after rollback
        - Database remains in consistent state
        """
        future_time: datetime = datetime.now(UTC) + timedelta(hours=3)
        jti_value: str = f"rollback-{uuid.uuid4()}"
        token: BlacklistedToken = BlacklistedToken(jti=jti_value, expires_at=future_time)

        # Manually create a transaction that we can control
        await self.async_session.execute(text("BEGIN"))
        try:
            self.async_session.add(token)
            await self.async_session.flush()  # Send SQL but don't commit
            # Rollback manually
            await self.async_session.execute(text("ROLLBACK"))
        except Exception:
            await self.async_session.execute(text("ROLLBACK"))

        # After rollback, token should not be in DB
        result: Result[tuple[int]] = await self.async_session.execute(
            text(f"SELECT COUNT(*) FROM blacklisted_tokens WHERE jti = '{token.jti}'")
        )
        count: int | None = result.scalar()
        assert count == 0
