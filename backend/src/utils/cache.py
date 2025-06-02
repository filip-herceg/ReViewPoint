import asyncio
from typing import Any


class AsyncInMemoryCache:
    def __init__(self):
        self._cache: dict[str, tuple[Any, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any:
        async with self._lock:
            value, expires = self._cache.get(key, (None, 0))
            if expires and expires < asyncio.get_event_loop().time():
                self._cache.pop(key, None)
                return None
            return value

    async def set(self, key: str, value: Any, ttl: float = 60.0) -> None:
        async with self._lock:
            expires = asyncio.get_event_loop().time() + ttl
            self._cache[key] = (value, expires)

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()


# Singleton cache instance for repository use
user_cache = AsyncInMemoryCache()
