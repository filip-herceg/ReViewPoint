import asyncio

import pytest

from src.utils.cache import AsyncInMemoryCache


@pytest.mark.asyncio
async def test_async_in_memory_cache() -> None:
    cache = AsyncInMemoryCache()

    # Test set and get
    await cache.set("key1", "value1")
    assert await cache.get("key1") == "value1"

    # Test TTL expiry
    await cache.set("key2", "value2", ttl=0.1)
    assert await cache.get("key2") == "value2"
    await asyncio.sleep(0.2)
    assert await cache.get("key2") is None

    # Test clear
    await cache.set("key3", "value3")
    await cache.clear()
    assert await cache.get("key3") is None
