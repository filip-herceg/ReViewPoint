import asyncio
from collections.abc import MutableMapping
from typing import Final, Generic, TypeVar

_K = TypeVar("_K", bound=str)
_V = TypeVar("_V")


class AsyncInMemoryCache(Generic[_K, _V]):
    """
    An asynchronous in-memory cache with per-key TTL.
    All keys are str, values are of type _V.
    """

    _cache: MutableMapping[_K, tuple[_V | None, float]]
    _lock: asyncio.Lock

    def __init__(self) -> None:
        self._cache: MutableMapping[_K, tuple[_V | None, float]] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def get(self, key: _K) -> _V | None:
        """
        Get a value from the cache by key.
        Returns None if not found or expired.
        """
        async with self._lock:
            value: _V | None
            expires: float
            value, expires = self._cache.get(key, (None, 0.0))
            if expires and expires < asyncio.get_event_loop().time():
                self._cache.pop(key, None)
                return None
            return value

    async def set(self, key: _K, value: _V, ttl: float = 60.0) -> None:
        """
        Set a value in the cache with a time-to-live (ttl) in seconds.
        """
        async with self._lock:
            expires: float = asyncio.get_event_loop().time() + ttl
            self._cache[key] = (value, expires)

    async def clear(self) -> None:
        """
        Clear all items from the cache.
        """
        async with self._lock:
            self._cache.clear()


# Singleton cache instance for repository use
user_cache: Final[AsyncInMemoryCache[str, object]] = AsyncInMemoryCache[str, object]()
