import asyncio
import os
from collections import defaultdict


class AsyncRateLimiter:
    def __init__(self, max_calls: int, period: float) -> None:
        self.max_calls = max_calls
        self.period = period
        self.calls: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def is_allowed(self, key: str) -> bool:
        # Bypass rate limiting in test mode
        if os.environ.get("TESTING") == "1":
            return True
        now = asyncio.get_event_loop().time()
        async with self._lock:
            calls = self.calls[key]
            # Remove expired calls
            self.calls[key] = [t for t in calls if t > now - self.period]
            if len(self.calls[key]) < self.max_calls:
                self.calls[key].append(now)
                return True
            return False

    def reset(self, key: str | None = None) -> None:
        """Reset the rate limiter for a specific key or all keys if key is None."""
        if key is not None:
            self.calls.pop(key, None)
        else:
            self.calls.clear()


# Example: user_rate_limiter = AsyncRateLimiter(max_calls=5, period=60.0)
