import pytest
from backend.core.database import db_healthcheck


@pytest.mark.asyncio
async def test_db_healthcheck():
    assert await db_healthcheck() is True
