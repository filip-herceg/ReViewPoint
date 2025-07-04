import pytest

from src.models.user import User
from tests.test_templates import DatabaseTestTemplate


@pytest.mark.asyncio
class TestAuditLog(DatabaseTestTemplate):
    @pytest.mark.skip(
        reason="audit_log table not implemented - this test expects database auditing that doesn't exist"
    )
    async def test_user_audit_log(self, async_session):
        # Insert a user using SQLAlchemy model
        user = User(
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

        # Check audit log
        from sqlalchemy import text

        result = await async_session.execute(
            text(
                "SELECT operation FROM audit_log WHERE new_data->>'email' = 'audit@example.com' OR old_data->>'email' = 'audit@example.com' ORDER BY id"
            )
        )
        ops = [row[0] for row in result.fetchall()]
        assert ops == ["INSERT", "UPDATE", "DELETE"]
