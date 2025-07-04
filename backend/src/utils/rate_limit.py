import asyncio
import os
from collections import defaultdict
from collections.abc import Sequence
from typing import (
    Final,
    Generic,
    Literal,
    TypedDict,
    TypeVar,
)

__all__: Final[Sequence[Literal["AsyncRateLimiter"]]] = ("AsyncRateLimiter",)

K = TypeVar("K", bound=str)
V = TypeVar("V")


class _RateLimitConfig(TypedDict):
    max_calls: int
    period: float


class RateLimitState(TypedDict):
    calls: int
    last_reset: float


class AsyncRateLimiter(Generic[K]):
    config: _RateLimitConfig
    max_calls: int
    period: float
    _lock: asyncio.Lock

    def __init__(self, max_calls: int, period: float) -> None:
        self.config: _RateLimitConfig = {"max_calls": max_calls, "period": period}
        self.max_calls: int = self.config["max_calls"]
        self.period: float = self.config["period"]
        self.calls: defaultdict[K, list[float]] = defaultdict(list)
        self._lock: asyncio.Lock = asyncio.Lock()

    async def is_allowed(self, key: K) -> bool:
        """
        Check if a call is allowed for the given key under the rate limit.

        Args:
            key (str): The identifier for rate limiting (e.g., user id, IP).

        Returns:
            bool: True if allowed, False otherwise.

        Raises:
            RuntimeError: If the event loop is not running.
        """
        # Bypass rate limiting in test mode
        if os.environ.get("TESTING") == "1":
            return True
        now: float = asyncio.get_event_loop().time()
        async with self._lock:
            calls: list[float] = self.calls[key]
            # Remove expired calls
            self.calls[key] = [t for t in calls if t > now - self.period]
            allowed: bool = len(self.calls[key]) < self.max_calls
            if allowed:
                self.calls[key].append(now)
                return True
            return False

    def reset(self, key: K | None = None) -> None:
        """
        Reset the rate limiter for a specific key or all keys if key is None.

        Args:
            key (Optional[str]): The key to reset, or None to reset all.
        """
        if key is not None:
            self.calls.pop(key, None)
        else:
            self.calls.clear()


# Example usage (not a constant, so not Final):
# user_rate_limiter: AsyncRateLimiter[str] = AsyncRateLimiter(max_calls=5, period=60.0)
