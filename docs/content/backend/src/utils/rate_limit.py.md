# utils/rate_limit.py - Asynchronous Rate Limiting Utilities

## Purpose

The `utils/rate_limit.py` module provides flexible, high-performance asynchronous rate limiting capabilities for the ReViewPoint platform. It implements a sliding window rate limiter with per-key tracking, thread-safe operations, and configurable limits for protecting against abuse and ensuring fair resource usage.

## Key Components

### Core Imports and Type Definitions

#### Essential Async and Collection Libraries

```python
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
```

### Type System Architecture

#### Generic Type Variables

```python
K = TypeVar("K", bound=str)
V = TypeVar("V")
```

**Features:**
- Generic key type bounded to string for flexibility
- Type-safe value handling for configuration data
- Compile-time type checking for rate limiter operations

#### Configuration and State Types

```python
class _RateLimitConfig(TypedDict):
    max_calls: int
    period: float

class RateLimitState(TypedDict):
    calls: int
    last_reset: float
```

**Type Definitions:**
- **_RateLimitConfig**: Internal configuration structure for rate limits
- **RateLimitState**: State tracking for rate limit monitoring
- Type-safe configuration with required fields
- Clear separation between configuration and runtime state

### Asynchronous Rate Limiter

#### Core Rate Limiter Implementation

```python
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
```

**Key Features:**
- Generic implementation supporting any string-based key type
- Configurable maximum calls and time period
- Thread-safe operations with asyncio.Lock
- Per-key call tracking with sliding window algorithm
- Memory-efficient defaultdict for sparse key usage

**Configuration Parameters:**
- **max_calls**: Maximum number of calls allowed within the time period
- **period**: Time window in seconds for rate limit enforcement
- **calls**: Per-key timestamp tracking for sliding window implementation
- **_lock**: Async lock for thread-safe concurrent access

### Rate Limit Checking

#### Sliding Window Rate Limit Enforcement

```python
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
```

**Algorithm Features:**
- Sliding window implementation for accurate rate limiting
- Automatic cleanup of expired call timestamps
- Atomic check-and-increment operation under lock
- Test environment bypass for development convenience
- High-precision timing using event loop time

**Usage Examples:**
```python
# User request rate limiting
user_limiter = AsyncRateLimiter[str](max_calls=10, period=60.0)

async def handle_user_request(user_id: str) -> dict:
    if not await user_limiter.is_allowed(user_id):
        raise RateLimitExceededError("Too many requests. Try again later.")
    
    return await process_user_request(user_id)

# API endpoint rate limiting
api_limiter = AsyncRateLimiter[str](max_calls=100, period=3600.0)  # 100/hour

async def api_endpoint(request):
    client_ip = request.client.host
    if not await api_limiter.is_allowed(client_ip):
        return {"error": "Rate limit exceeded", "retry_after": 3600}
    
    return await handle_request(request)
```

### Rate Limit Management

#### Key-Specific and Global Reset Operations

```python
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
```

**Reset Operations:**
- **Specific key reset**: Remove rate limit state for individual users/IPs
- **Global reset**: Clear all rate limit state for system maintenance
- Thread-safe operations with automatic cleanup
- Graceful handling of non-existent keys

**Usage Examples:**
```python
# Reset rate limit for specific user (admin action)
await user_limiter.reset("user_123")

# Clear all rate limits (system maintenance)
await user_limiter.reset()

# Reset during user privilege upgrade
async def upgrade_user_to_premium(user_id: str):
    await upgrade_user_account(user_id)
    # Reset rate limits for immediate premium benefits
    user_limiter.reset(user_id)
    api_limiter.reset(user_id)
```

## Integration Patterns

### FastAPI Middleware Integration

#### Request Rate Limiting Middleware

```python
from fastapi import FastAPI, Request, HTTPException
from src.utils.rate_limit import AsyncRateLimiter

# Global rate limiters
ip_limiter = AsyncRateLimiter[str](max_calls=1000, period=3600.0)  # 1000/hour per IP
user_limiter = AsyncRateLimiter[str](max_calls=500, period=3600.0)  # 500/hour per user

async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all requests."""
    
    # IP-based rate limiting
    client_ip = request.client.host
    if not await ip_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="IP rate limit exceeded",
            headers={"Retry-After": "3600"}
        )
    
    # User-based rate limiting (if authenticated)
    if hasattr(request.state, "user") and request.state.user:
        user_id = str(request.state.user.id)
        if not await user_limiter.is_allowed(user_id):
            raise HTTPException(
                status_code=429,
                detail="User rate limit exceeded",
                headers={"Retry-After": "3600"}
            )
    
    response = await call_next(request)
    return response

app = FastAPI()
app.middleware("http")(rate_limit_middleware)
```

### Endpoint-Specific Rate Limiting

#### Granular Rate Limit Control

```python
from functools import wraps
from src.utils.rate_limit import AsyncRateLimiter

# Endpoint-specific rate limiters
login_limiter = AsyncRateLimiter[str](max_calls=5, period=300.0)  # 5 login attempts per 5 minutes
upload_limiter = AsyncRateLimiter[str](max_calls=10, period=3600.0)  # 10 uploads per hour
email_limiter = AsyncRateLimiter[str](max_calls=3, period=3600.0)  # 3 emails per hour

def rate_limit(limiter: AsyncRateLimiter[str], key_func=None):
    """Decorator for endpoint-specific rate limiting."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract key from request or user
            if key_func:
                key = await key_func(*args, **kwargs)
            else:
                # Default to user ID if available
                request = args[0] if args else kwargs.get('request')
                key = getattr(request.state, 'user_id', request.client.host)
            
            if not await limiter.is_allowed(str(key)):
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded for {func.__name__}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage examples
@app.post("/login")
@rate_limit(login_limiter, lambda request: request.client.host)
async def login_endpoint(request: LoginRequest):
    return await authenticate_user(request.email, request.password)

@app.post("/upload")
@rate_limit(upload_limiter, lambda user: user.id)
async def upload_endpoint(file: UploadFile, user: User = Depends(get_current_user)):
    return await upload_service.upload_file(file, user)
```

### Service Layer Integration

#### Business Logic Rate Limiting

```python
from src.utils.rate_limit import AsyncRateLimiter
from src.utils.errors import RateLimitExceededError

class UserService:
    def __init__(self):
        self.password_reset_limiter = AsyncRateLimiter[str](max_calls=3, period=3600.0)
        self.email_verification_limiter = AsyncRateLimiter[str](max_calls=5, period=3600.0)
        self.profile_update_limiter = AsyncRateLimiter[str](max_calls=10, period=3600.0)
    
    async def request_password_reset(self, email: str) -> None:
        """Request password reset with rate limiting."""
        if not await self.password_reset_limiter.is_allowed(email):
            raise RateLimitExceededError(
                "Too many password reset requests. Please try again in an hour."
            )
        
        await self.send_password_reset_email(email)
    
    async def send_verification_email(self, user_id: int) -> None:
        """Send verification email with rate limiting."""
        key = str(user_id)
        if not await self.email_verification_limiter.is_allowed(key):
            raise RateLimitExceededError(
                "Too many verification emails sent. Please try again later."
            )
        
        await self.email_service.send_verification_email(user_id)
    
    async def update_profile(self, user_id: int, data: dict) -> User:
        """Update user profile with rate limiting."""
        key = str(user_id)
        if not await self.profile_update_limiter.is_allowed(key):
            raise RateLimitExceededError(
                "Too many profile updates. Please try again later."
            )
        
        return await self.user_repository.update_profile(user_id, data)
```

### Cache Integration

#### Redis-Backed Rate Limiting

```python
import json
from typing import Optional
from src.utils.cache import CacheService
from src.utils.rate_limit import AsyncRateLimiter

class RedisRateLimiter(AsyncRateLimiter[str]):
    """Redis-backed rate limiter for distributed systems."""
    
    def __init__(self, max_calls: int, period: float, cache: CacheService):
        super().__init__(max_calls, period)
        self.cache = cache
        self.key_prefix = "rate_limit"
    
    async def is_allowed(self, key: str) -> bool:
        """Check rate limit using Redis for persistence."""
        if os.environ.get("TESTING") == "1":
            return True
        
        cache_key = f"{self.key_prefix}:{key}"
        now = asyncio.get_event_loop().time()
        
        # Get current call history from Redis
        history_json = await self.cache.get(cache_key)
        if history_json:
            history = json.loads(history_json)
        else:
            history = []
        
        # Remove expired calls
        history = [t for t in history if t > now - self.period]
        
        # Check if limit is exceeded
        if len(history) >= self.max_calls:
            return False
        
        # Add current call
        history.append(now)
        
        # Store updated history in Redis
        await self.cache.set(
            cache_key, 
            json.dumps(history), 
            expire=int(self.period)
        )
        
        return True
    
    async def reset(self, key: Optional[str] = None) -> None:
        """Reset rate limit state in Redis."""
        if key is not None:
            cache_key = f"{self.key_prefix}:{key}"
            await self.cache.delete(cache_key)
        else:
            # Reset all rate limit keys (requires pattern matching)
            pattern = f"{self.key_prefix}:*"
            keys = await self.cache.keys(pattern)
            if keys:
                await self.cache.delete_many(keys)
```

## Advanced Features

### Adaptive Rate Limiting

#### Dynamic Rate Limit Adjustment

```python
class AdaptiveRateLimiter(AsyncRateLimiter[str]):
    """Rate limiter with dynamic adjustment based on system load."""
    
    def __init__(self, base_max_calls: int, period: float):
        super().__init__(base_max_calls, period)
        self.base_max_calls = base_max_calls
        self.load_factor = 1.0
    
    async def adjust_for_load(self, cpu_usage: float, memory_usage: float) -> None:
        """Adjust rate limits based on system metrics."""
        # Reduce limits under high load
        if cpu_usage > 0.8 or memory_usage > 0.9:
            self.load_factor = 0.5  # 50% of normal rate
        elif cpu_usage > 0.6 or memory_usage > 0.7:
            self.load_factor = 0.7  # 70% of normal rate
        else:
            self.load_factor = 1.0  # Normal rate
        
        self.max_calls = int(self.base_max_calls * self.load_factor)
    
    async def is_allowed(self, key: str) -> bool:
        """Check rate limit with dynamic adjustment."""
        # Update max_calls based on current load factor
        self.max_calls = int(self.base_max_calls * self.load_factor)
        return await super().is_allowed(key)
```

### Tiered Rate Limiting

#### User Role-Based Rate Limits

```python
from enum import Enum
from src.utils.rate_limit import AsyncRateLimiter

class UserTier(Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class TieredRateLimiter:
    """Rate limiter with different limits per user tier."""
    
    def __init__(self):
        self.limiters = {
            UserTier.FREE: AsyncRateLimiter[str](max_calls=100, period=3600.0),
            UserTier.PREMIUM: AsyncRateLimiter[str](max_calls=1000, period=3600.0),
            UserTier.ENTERPRISE: AsyncRateLimiter[str](max_calls=10000, period=3600.0),
        }
    
    async def is_allowed(self, user_id: str, tier: UserTier) -> bool:
        """Check rate limit based on user tier."""
        limiter = self.limiters[tier]
        return await limiter.is_allowed(user_id)
    
    def reset(self, user_id: str, tier: UserTier | None = None) -> None:
        """Reset rate limits for user tier(s)."""
        if tier:
            self.limiters[tier].reset(user_id)
        else:
            # Reset across all tiers
            for limiter in self.limiters.values():
                limiter.reset(user_id)

# Usage
tiered_limiter = TieredRateLimiter()

async def api_endpoint(user: User):
    user_tier = UserTier(user.subscription_tier)
    if not await tiered_limiter.is_allowed(str(user.id), user_tier):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {user_tier.value} tier"
        )
    
    return await process_request(user)
```

## Security Considerations

### DOS Protection

#### Multi-Layer Rate Limiting

```python
class DOSProtectionLimiter:
    """Multi-layer rate limiting for DOS protection."""
    
    def __init__(self):
        # Aggressive short-term limiting
        self.burst_limiter = AsyncRateLimiter[str](max_calls=10, period=60.0)
        # Moderate medium-term limiting
        self.hourly_limiter = AsyncRateLimiter[str](max_calls=500, period=3600.0)
        # Conservative long-term limiting
        self.daily_limiter = AsyncRateLimiter[str](max_calls=5000, period=86400.0)
    
    async def is_allowed(self, key: str) -> tuple[bool, str]:
        """Check all rate limit layers."""
        if not await self.burst_limiter.is_allowed(key):
            return False, "Burst rate limit exceeded"
        
        if not await self.hourly_limiter.is_allowed(key):
            return False, "Hourly rate limit exceeded"
        
        if not await self.daily_limiter.is_allowed(key):
            return False, "Daily rate limit exceeded"
        
        return True, "Allowed"
```

### Memory Management

#### Automatic Cleanup

```python
class MemoryEfficientRateLimiter(AsyncRateLimiter[str]):
    """Rate limiter with automatic memory cleanup."""
    
    def __init__(self, max_calls: int, period: float, max_keys: int = 10000):
        super().__init__(max_calls, period)
        self.max_keys = max_keys
        self.cleanup_interval = period / 4  # Cleanup 4 times per period
        self.last_cleanup = 0.0
    
    async def is_allowed(self, key: str) -> bool:
        """Check rate limit with automatic cleanup."""
        now = asyncio.get_event_loop().time()
        
        # Perform periodic cleanup
        if now - self.last_cleanup > self.cleanup_interval:
            await self._cleanup_expired_keys(now)
            self.last_cleanup = now
        
        return await super().is_allowed(key)
    
    async def _cleanup_expired_keys(self, now: float) -> None:
        """Remove keys with no recent activity."""
        async with self._lock:
            keys_to_remove = []
            
            for key, timestamps in self.calls.items():
                # Remove expired timestamps
                valid_timestamps = [t for t in timestamps if t > now - self.period]
                
                if not valid_timestamps:
                    keys_to_remove.append(key)
                else:
                    self.calls[key] = valid_timestamps
            
            # Remove empty keys
            for key in keys_to_remove:
                del self.calls[key]
            
            # If still too many keys, remove oldest
            if len(self.calls) > self.max_keys:
                # Sort by most recent activity
                sorted_keys = sorted(
                    self.calls.keys(),
                    key=lambda k: max(self.calls[k]) if self.calls[k] else 0
                )
                
                # Remove oldest keys
                excess_count = len(self.calls) - self.max_keys
                for key in sorted_keys[:excess_count]:
                    del self.calls[key]
```

## Best Practices

### Configuration Guidelines

```python
# Rate limit configurations by use case
RATE_LIMITS = {
    # Authentication endpoints
    "login": {"max_calls": 5, "period": 300.0},  # 5 attempts per 5 minutes
    "password_reset": {"max_calls": 3, "period": 3600.0},  # 3 per hour
    "register": {"max_calls": 3, "period": 3600.0},  # 3 per hour
    
    # API endpoints
    "api_general": {"max_calls": 1000, "period": 3600.0},  # 1000 per hour
    "api_search": {"max_calls": 100, "period": 60.0},  # 100 per minute
    "api_upload": {"max_calls": 10, "period": 3600.0},  # 10 per hour
    
    # Email endpoints
    "email_send": {"max_calls": 10, "period": 3600.0},  # 10 per hour
    "email_verify": {"max_calls": 5, "period": 3600.0},  # 5 per hour
    
    # Administrative actions
    "admin_action": {"max_calls": 100, "period": 3600.0},  # 100 per hour
}
```

### Testing Strategies

```python
import pytest
from src.utils.rate_limit import AsyncRateLimiter

class TestRateLimiter:
    """Comprehensive rate limiter testing."""
    
    @pytest.fixture
    def limiter(self):
        return AsyncRateLimiter[str](max_calls=3, period=60.0)
    
    @pytest.mark.asyncio
    async def test_basic_rate_limiting(self, limiter):
        """Test basic rate limiting functionality."""
        key = "test_user"
        
        # First 3 calls should be allowed
        for i in range(3):
            assert await limiter.is_allowed(key) is True
        
        # 4th call should be denied
        assert await limiter.is_allowed(key) is False
    
    @pytest.mark.asyncio
    async def test_different_keys(self, limiter):
        """Test that different keys have separate limits."""
        # User 1 reaches limit
        for i in range(3):
            await limiter.is_allowed("user1")
        
        # User 2 should still be allowed
        assert await limiter.is_allowed("user2") is True
    
    @pytest.mark.asyncio
    async def test_reset_functionality(self, limiter):
        """Test rate limit reset."""
        key = "test_user"
        
        # Reach limit
        for i in range(3):
            await limiter.is_allowed(key)
        
        assert await limiter.is_allowed(key) is False
        
        # Reset and verify
        limiter.reset(key)
        assert await limiter.is_allowed(key) is True
    
    @pytest.mark.asyncio
    async def test_concurrent_access(self, limiter):
        """Test thread safety under concurrent access."""
        key = "concurrent_user"
        
        async def make_call():
            return await limiter.is_allowed(key)
        
        # Make 10 concurrent calls
        tasks = [make_call() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # Only 3 should be allowed
        allowed_count = sum(results)
        assert allowed_count == 3
```

This rate limiting system provides robust, scalable, and flexible protection against abuse while maintaining high performance and easy integration with the ReViewPoint platform architecture.
