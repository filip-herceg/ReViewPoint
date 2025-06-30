import asyncio

import pytest

from src.utils.cache import AsyncInMemoryCache
from tests.test_templates import UtilityUnitTestTemplate


class TestAsyncInMemoryCache(UtilityUnitTestTemplate):
    @pytest.mark.asyncio
    async def test_set_and_get(self):
        cache = AsyncInMemoryCache()
        await cache.set("key1", "value1")
        self.assert_equal(await cache.get("key1"), "value1")

    @pytest.mark.asyncio
    async def test_ttl_expiry(self):
        cache = AsyncInMemoryCache()
        await cache.set("key2", "value2", ttl=0.1)
        self.assert_equal(await cache.get("key2"), "value2")
        await asyncio.sleep(0.2)
        self.assert_is_none(await cache.get("key2"))

    @pytest.mark.asyncio
    async def test_clear(self):
        cache = AsyncInMemoryCache()
        await cache.set("key3", "value3")
        await cache.clear()
        self.assert_is_none(await cache.get("key3"))
