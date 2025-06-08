import asyncio

import pytest

from src.utils.rate_limit import AsyncRateLimiter


@pytest.mark.asyncio
async def test_async_rate_limiter() -> None:
    limiter = AsyncRateLimiter(max_calls=2, period=0.5)
    key = "user:1:test"
    assert await limiter.is_allowed(key)
    assert await limiter.is_allowed(key)
    assert not await limiter.is_allowed(key)
    await asyncio.sleep(0.6)
    assert await limiter.is_allowed(key)

    # Test reset functionality
    key2 = "user:2:test"
    assert await limiter.is_allowed(key2)
    limiter.reset(key2)
    assert await limiter.is_allowed(key2)

    # Test global reset
    key3 = "user:3:test"
    assert await limiter.is_allowed(key3)
    limiter.reset()
    assert await limiter.is_allowed(key)
    assert await limiter.is_allowed(key2)
    assert await limiter.is_allowed(key3)
