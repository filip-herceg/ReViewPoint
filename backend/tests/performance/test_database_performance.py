import statistics
import time
from collections.abc import Sequence
from typing import Final

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from tests.test_templates import DatabaseTestTemplate


@pytest.mark.performance
class TestDatabasePerformance(DatabaseTestTemplate):
    @pytest.mark.asyncio
    async def test_query_performance(
        self: "TestDatabasePerformance", async_session: AsyncSession
    ) -> None:
        """
        Test database query performance with populated database.

        Verifies:
        - Average query time is below threshold
        - 95th percentile query time is below threshold
        Raises:
        - AssertionError if performance is too slow
        """
        num_queries: Final[int] = 50
        query_times: list[float] = []
        for _ in range(num_queries):
            start: float = time.time()
            await async_session.execute(
                select(User).where(User.email.like("%@example.com"))
            )
            query_times.append(time.time() - start)
        avg_time: float = statistics.mean(query_times)
        # Use quantiles with n=20 for 95th percentile (19th out of 20 quantiles)
        quantiles: Sequence[float] = statistics.quantiles(query_times, n=20)
        p95_time: float = quantiles[18] if len(quantiles) > 18 else max(query_times)
        assert avg_time < 0.05, f"Average query time too slow: {avg_time:.4f}s"
        assert p95_time < 0.2, f"95th percentile query time too slow: {p95_time:.4f}s"
