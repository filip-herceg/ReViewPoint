import pytest
from sqlalchemy import text

from tests.test_templates import DatabaseTestTemplate


@pytest.mark.asyncio
class TestAuditLog(DatabaseTestTemplate):
    async def test_user_audit_log(self, async_session):
        # Insert a user
        await async_session.execute(
            text(
                """
            INSERT INTO "user" (email, name, password_hash) VALUES ('audit@example.com', 'Audit User', 'hash')
        """
            )
        )
        await async_session.commit()
        # Update the user
        await async_session.execute(
            text(
                """
            UPDATE "user" SET name = 'Audit User Updated' WHERE email = 'audit@example.com'
        """
            )
        )
        await async_session.commit()
        # Delete the user
        await async_session.execute(
            text(
                """
            DELETE FROM "user" WHERE email = 'audit@example.com'
        """
            )
        )
        await async_session.commit()
        # Check audit log
        result = await async_session.execute(
            text(
                "SELECT operation FROM audit_log WHERE new_data->>'email' = 'audit@example.com' OR old_data->>'email' = 'audit@example.com' ORDER BY id"
            )
        )
        ops = [row[0] for row in result.fetchall()]
        assert ops == ["INSERT", "UPDATE", "DELETE"]
