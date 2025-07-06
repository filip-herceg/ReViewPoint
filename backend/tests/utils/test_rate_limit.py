import asyncio
from typing import Final, List
import pytest
from src.utils.rate_limit import AsyncRateLimiter
from tests.test_templates import UtilityUnitTestTemplate


class TestAsyncRateLimiter(UtilityUnitTestTemplate):
    """Test the AsyncRateLimiter utility for correct rate limiting and reset behavior."""

    @pytest.mark.asyncio
    @pytest.mark.skip_if_fast_tests("Rate limiter is bypassed in test mode")
    async def test_async_rate_limiter(self) -> None:
        """
        Test AsyncRateLimiter allows up to max_calls within the period, blocks further calls,
        and allows again after the period. Also tests reset for a single key and global reset.
        """
        limiter: Final[AsyncRateLimiter] = AsyncRateLimiter(max_calls=2, period=0.5)
        key: Final[str] = "user:1:test"
        results: List[bool] = [await limiter.is_allowed(key) for _ in range(2)]
        self.assert_all_true(results)
        self.assert_is_false(await limiter.is_allowed(key))
        await asyncio.sleep(0.6)
        self.assert_is_true(await limiter.is_allowed(key))

        # Test reset functionality for a single key
        key2: Final[str] = "user:2:test"
        self.assert_is_true(await limiter.is_allowed(key2))
        limiter.reset(key2)
        self.assert_is_true(await limiter.is_allowed(key2))

        # Test global reset
        key3: Final[str] = "user:3:test"
        self.assert_is_true(await limiter.is_allowed(key3))
        limiter.reset()
        all_keys: List[str] = [key, key2, key3]
        results = [await limiter.is_allowed(k) for k in all_keys]
        self.assert_all_true(results)
