import asyncio

import pytest

from src.utils.rate_limit import AsyncRateLimiter
from tests.test_templates import UtilityUnitTestTemplate


class TestAsyncRateLimiter(UtilityUnitTestTemplate):
    @pytest.mark.asyncio
    @pytest.mark.skip_if_fast_tests("Rate limiter is bypassed in test mode")
    async def test_async_rate_limiter(self):
        limiter = AsyncRateLimiter(max_calls=2, period=0.5)
        key = "user:1:test"
        results = [await limiter.is_allowed(key) for _ in range(2)]
        self.assert_all_true(results)
        self.assert_is_false(await limiter.is_allowed(key))
        await asyncio.sleep(0.6)
        self.assert_is_true(await limiter.is_allowed(key))

        # Test reset functionality
        key2 = "user:2:test"
        self.assert_is_true(await limiter.is_allowed(key2))
        limiter.reset(key2)
        self.assert_is_true(await limiter.is_allowed(key2))

        # Test global reset
        key3 = "user:3:test"
        self.assert_is_true(await limiter.is_allowed(key3))
        limiter.reset()
        all_keys = [key, key2, key3]
        results = [await limiter.is_allowed(k) for k in all_keys]
        self.assert_all_true(results)
