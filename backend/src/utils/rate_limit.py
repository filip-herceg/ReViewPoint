import asyncio
from collections import defaultdict


class AsyncRateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def is_allowed(self, key: str) -> bool:
        now = asyncio.get_event_loop().time()
        async with self._lock:
            calls = self.calls[key]
            # Remove expired calls
            self.calls[key] = [t for t in calls if t > now - self.period]
            if len(self.calls[key]) < self.max_calls:
                self.calls[key].append(now)
                return True
            return False


# Example: user_rate_limiter = AsyncRateLimiter(max_calls=5, period=60.0)
