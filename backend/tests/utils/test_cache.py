import asyncio
from typing import Final
import pytest
from src.utils.cache import AsyncInMemoryCache
from tests.test_templates import UtilityUnitTestTemplate


class TestAsyncInMemoryCache(UtilityUnitTestTemplate):
    @pytest.mark.asyncio
    async def test_set_and_get(self) -> None:
        """
        Test that set and get work for a single key-value pair.
        """
        cache: Final[AsyncInMemoryCache[str, str]] = AsyncInMemoryCache()
        key: Final[str] = "key1"
        value: Final[str] = "value1"
        await cache.set(key, value)
        result: str | None = await cache.get(key)
        self.assert_equal(result, value)

    @pytest.mark.asyncio
    @pytest.mark.requires_timing_precision(
        "TTL expiry not reliable in fast tests due to timing issues"
    )
    async def test_ttl_expiry(self) -> None:
        """
        Test that a key expires after its TTL.
        """
        cache: Final[AsyncInMemoryCache[str, str]] = AsyncInMemoryCache()
        key: Final[str] = "key2"
        value: Final[str] = "value2"
        await cache.set(key, value, ttl=0.1)
        result: str | None = await cache.get(key)
        self.assert_equal(result, value)
        await asyncio.sleep(0.2)
        expired: str | None = await cache.get(key)
        self.assert_is_none(expired)

    @pytest.mark.asyncio
    async def test_clear(self) -> None:
        """
        Test that clear removes all keys from the cache.
        """
        cache: Final[AsyncInMemoryCache[str, str]] = AsyncInMemoryCache()
        key: Final[str] = "key3"
        value: Final[str] = "value3"
        await cache.set(key, value)
        await cache.clear()
        result: str | None = await cache.get(key)
        self.assert_is_none(result)
