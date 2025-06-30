import statistics
import time

import pytest
from tests.test_templates import DatabaseTestTemplate
from sqlalchemy import select

from src.models.user import User


@pytest.mark.performance
class TestDatabasePerformance(DatabaseTestTemplate):
    @pytest.mark.asyncio
    async def test_query_performance(self, async_session):
        """Test database query performance with populated database."""
        query_times = []
        # Run query multiple times
        for _ in range(50):
            start = time.time()
            await async_session.execute(
                select(User).where(User.email.like("%@example.com"))
            )
            query_times.append(time.time() - start)
        # Calculate statistics
        avg_time = statistics.mean(query_times)
        p95_time = statistics.quantiles(query_times, n=20)[19]  # 95th percentile
        # Assert performance thresholds (adjust as needed for your infra)
        assert avg_time < 0.05, f"Average query time too slow: {avg_time:.4f}s"
        assert p95_time < 0.2, f"95th percentile query time too slow: {p95_time:.4f}s"
