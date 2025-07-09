"""Test module for audit log functionality.

This module tests database auditing functionality including:
- User model CRUD operations auditing
- Audit trail verification
- Database trigger-based logging

Note: Currently skipped as audit_log table and triggers are not implemented.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Final

import pytest
from sqlalchemy import Result, Row, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from tests.test_templates import DatabaseTestTemplate


@pytest.mark.asyncio
class TestAuditLog(DatabaseTestTemplate):
    """Test class for database audit log functionality."""

    @pytest.mark.skip(
        reason="audit_log table not implemented - this test expects database auditing that doesn't exist"
    )
    async def test_user_audit_log(self, async_session: AsyncSession) -> None:
        """Test that user CRUD operations are properly audited.

        This test verifies that database triggers create appropriate audit log
        entries for INSERT, UPDATE, and DELETE operations on the users table.
        The audit log should contain operation type and relevant data changes.

        Currently skipped because:
        - audit_log table schema is not defined
        - Database triggers for auditing are not implemented
        - Test expects specific audit trail structure

        Parameters
        ----------
        async_session : AsyncSession
            The async database session fixture for test isolation.

        Raises
        ------
        AssertionError
            If audit log entries don't match expected operations sequence.
        """
        # Insert a user using SQLAlchemy model
        user: User = User(
            email="audit@example.com", name="Audit User", hashed_password="hash"
        )
        async_session.add(user)
        await async_session.commit()

        # Update the user
        user.name = "Audit User Updated"
        await async_session.commit()

        # Delete the user
        await async_session.delete(user)
        await async_session.commit()

        # Check audit log - this query expects audit_log table with:
        # - operation column (VARCHAR) with values like 'INSERT', 'UPDATE', 'DELETE'
        # - new_data column (JSONB) containing new row data
        # - old_data column (JSONB) containing previous row data
        # - id column for ordering
        audit_query: str = (
            "SELECT operation FROM audit_log "
            "WHERE new_data->>'email' = 'audit@example.com' "
            "OR old_data->>'email' = 'audit@example.com' "
            "ORDER BY id"
        )

        result: Result[Any] = await async_session.execute(text(audit_query))
        rows: Sequence[Row[Any]] = result.fetchall()
        ops: list[str] = [row[0] for row in rows]

        # Expected sequence: INSERT (user creation), UPDATE (name change), DELETE (user removal)
        expected_operations: Final[list[str]] = ["INSERT", "UPDATE", "DELETE"]
        assert ops == expected_operations
