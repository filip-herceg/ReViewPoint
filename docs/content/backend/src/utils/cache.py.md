# utils/cache.py - Asynchronous In-Memory Cache Utilities

## Purpose

The `utils/cache.py` module provides high-performance asynchronous in-memory caching capabilities for the ReViewPoint platform. It implements a thread-safe, TTL-based cache with generic type support, automatic expiration handling, and optimized concurrent access patterns.

## Key Components

### Core Imports and Type System

#### Generic Cache Implementation

```python
import asyncio
from collections.abc import MutableMapping
from typing import Final, Generic, TypeVar

_K = TypeVar("_K", bound=str)
_V = TypeVar("_V")
```

**Type System Features:**

- Generic implementation supporting any value type
- String-bounded key types for consistent hashing
- Type-safe operations with compile-time checking
- Flexible value type support for diverse caching needs

### Asynchronous In-Memory Cache

#### High-Performance Cache Implementation

```python
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
```

**Core Architecture:**

- Generic cache supporting any key-value types
- Thread-safe operations with asyncio.Lock
- Per-key TTL (Time-To-Live) expiration
- Memory-efficient tuple storage (value, expiration_time)
- Lazy expiration with automatic cleanup

### Cache Operations

#### Asynchronous Value Retrieval

```python
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
```

**Features:**

- Automatic expiration checking on retrieval
- Lazy cleanup of expired entries
- Thread-safe concurrent access
- Type-safe return values with Optional typing
- High-precision timing using event loop time

**Usage Examples:**

```python
# Basic cache usage
cache = AsyncInMemoryCache[str, dict]()

# Store user data
user_data = {"id": 123, "name": "John Doe", "email": "john@example.com"}
await cache.set("user:123", user_data, ttl=300.0)  # 5 minutes

# Retrieve user data
cached_user = await cache.get("user:123")
if cached_user:
    print(f"Cache hit: {cached_user['name']}")
else:
    print("Cache miss - data expired or not found")

# Type-safe operations
profile_cache = AsyncInMemoryCache[str, UserProfile]()
await profile_cache.set("profile:456", user_profile, ttl=600.0)
profile = await profile_cache.get("profile:456")  # Returns UserProfile | None
```

#### Asynchronous Value Storage

```python
async def set(self, key: _K, value: _V, ttl: float = 60.0) -> None:
    """
    Set a value in the cache with a time-to-live (ttl) in seconds.
    """
    async with self._lock:
        expires: float = asyncio.get_event_loop().time() + ttl
        self._cache[key] = (value, expires)
```

**Features:**

- Configurable TTL with default 60-second expiration
- High-precision expiration timing
- Atomic set operations under lock
- Memory-efficient storage format
- Overwrite existing keys with new TTL

**Usage Examples:**

```python
# Default TTL (60 seconds)
await cache.set("temp_data", {"status": "processing"})

# Custom TTL values
await cache.set("session:abc123", session_data, ttl=1800.0)  # 30 minutes
await cache.set("rate_limit:user:456", {"count": 5}, ttl=300.0)  # 5 minutes
await cache.set("config:features", feature_flags, ttl=3600.0)  # 1 hour

# Long-term caching
await cache.set("static_config", app_config, ttl=86400.0)  # 24 hours
```

#### Cache Management

```python
async def clear(self) -> None:
    """
    Clear all items from the cache.
    """
    async with self._lock:
        self._cache.clear()
```

**Features:**

- Complete cache invalidation
- Thread-safe clearing operation
- Memory cleanup for cache reset
- Useful for testing and maintenance

### Global Cache Instance

#### Singleton Cache for Repository Layer

```python
# Singleton cache instance for repository use
user_cache: Final[AsyncInMemoryCache[str, object]] = AsyncInMemoryCache[str, object]()
```

**Global Cache Design:**

- Singleton pattern for shared cache access
- Generic object value type for flexibility
- Pre-configured for repository layer integration
- Memory-efficient shared instance across modules

## Integration Patterns

### Repository Layer Integration

#### User Repository Caching

```python
from src.utils.cache import user_cache
from src.models.user import User
from typing import Optional

class UserRepository:
    """User repository with intelligent caching."""

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user with cache optimization."""
        cache_key = f"user:id:{user_id}"

        # Try cache first
        cached_user = await user_cache.get(cache_key)
        if cached_user:
            return User.parse_obj(cached_user) if isinstance(cached_user, dict) else cached_user

        # Database lookup
        user = await self._fetch_user_from_db(user_id)
        if user:
            # Cache for 5 minutes
            await user_cache.set(cache_key, user.dict(), ttl=300.0)

        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email with caching."""
        cache_key = f"user:email:{email.lower()}"

        cached_user = await user_cache.get(cache_key)
        if cached_user:
            return User.parse_obj(cached_user)

        user = await self._fetch_user_by_email_from_db(email)
        if user:
            # Cache both email and ID lookups
            await user_cache.set(cache_key, user.dict(), ttl=300.0)
            await user_cache.set(f"user:id:{user.id}", user.dict(), ttl=300.0)

        return user

    async def update_user(self, user_id: int, data: dict) -> User:
        """Update user and invalidate cache."""
        # Update database
        updated_user = await self._update_user_in_db(user_id, data)

        # Invalidate related cache entries
        await self._invalidate_user_cache(user_id, updated_user.email)

        return updated_user

    async def _invalidate_user_cache(self, user_id: int, email: str) -> None:
        """Invalidate all cache entries for a user."""
        cache_keys = [
            f"user:id:{user_id}",
            f"user:email:{email.lower()}",
            f"user:profile:{user_id}",
            f"user:permissions:{user_id}"
        ]

        # Note: This implementation removes entries one by one
        # In a production Redis implementation, you might use pattern deletion
        for key in cache_keys:
            await user_cache.set(key, None, ttl=0.0)  # Immediate expiration
```

### Service Layer Integration

#### Cached Business Logic

```python
from src.utils.cache import AsyncInMemoryCache

class BusinessLogicService:
    """Service with comprehensive caching strategy."""

    def __init__(self):
        self.computation_cache = AsyncInMemoryCache[str, dict]()
        self.permission_cache = AsyncInMemoryCache[str, list]()
        self.config_cache = AsyncInMemoryCache[str, dict]()

    async def get_user_permissions(self, user_id: int) -> list[str]:
        """Get user permissions with caching."""
        cache_key = f"permissions:{user_id}"

        permissions = await self.permission_cache.get(cache_key)
        if permissions is not None:
            return permissions

        # Expensive permission calculation
        permissions = await self._calculate_user_permissions(user_id)

        # Cache for 15 minutes
        await self.permission_cache.set(cache_key, permissions, ttl=900.0)
        return permissions

    async def get_application_config(self) -> dict:
        """Get application configuration with long-term caching."""
        cache_key = "app_config"

        config = await self.config_cache.get(cache_key)
        if config is not None:
            return config

        # Load configuration from database/file
        config = await self._load_application_config()

        # Cache for 1 hour
        await self.config_cache.set(cache_key, config, ttl=3600.0)
        return config

    async def compute_analytics(self, user_id: int, time_range: str) -> dict:
        """Compute analytics with result caching."""
        cache_key = f"analytics:{user_id}:{time_range}"

        result = await self.computation_cache.get(cache_key)
        if result is not None:
            return result

        # Expensive analytics computation
        result = await self._compute_user_analytics(user_id, time_range)

        # Cache based on time range
        ttl = self._get_analytics_cache_ttl(time_range)
        await self.computation_cache.set(cache_key, result, ttl=ttl)
        return result

    def _get_analytics_cache_ttl(self, time_range: str) -> float:
        """Get appropriate cache TTL based on time range."""
        ttl_mapping = {
            "realtime": 30.0,      # 30 seconds
            "hourly": 300.0,       # 5 minutes
            "daily": 1800.0,       # 30 minutes
            "weekly": 3600.0,      # 1 hour
            "monthly": 7200.0,     # 2 hours
        }
        return ttl_mapping.get(time_range, 300.0)  # Default 5 minutes
```

### FastAPI Integration

#### Request-Level Caching

```python
from fastapi import FastAPI, Depends, Request
from src.utils.cache import AsyncInMemoryCache

# Application-level cache
request_cache = AsyncInMemoryCache[str, dict]()

async def cache_middleware(request: Request, call_next):
    """Middleware for request-level caching."""

    # Only cache GET requests
    if request.method != "GET":
        return await call_next(request)

    # Generate cache key from request
    cache_key = f"request:{request.url.path}:{hash(str(request.query_params))}"

    # Try cache first
    cached_response = await request_cache.get(cache_key)
    if cached_response:
        return JSONResponse(content=cached_response)

    # Process request
    response = await call_next(request)

    # Cache successful responses
    if response.status_code == 200:
        # Cache for 2 minutes
        await request_cache.set(cache_key, response.body, ttl=120.0)

    return response

app = FastAPI()
app.middleware("http")(cache_middleware)

# Endpoint-specific caching
@app.get("/api/users/{user_id}/profile")
async def get_user_profile(
    user_id: int,
    cache: AsyncInMemoryCache = Depends(lambda: request_cache)
):
    """Get user profile with endpoint caching."""
    cache_key = f"profile:{user_id}"

    profile = await cache.get(cache_key)
    if profile:
        return profile

    # Fetch from service
    profile = await user_service.get_profile(user_id)

    # Cache for 10 minutes
    await cache.set(cache_key, profile, ttl=600.0)
    return profile
```

### Advanced Caching Patterns

#### Multi-Level Cache Architecture

```python
from src.utils.cache import AsyncInMemoryCache
from typing import Protocol

class CacheBackend(Protocol):
    async def get(self, key: str) -> any: ...
    async def set(self, key: str, value: any, ttl: float = 60.0) -> None: ...
    async def clear(self) -> None: ...

class MultiLevelCache:
    """Multi-level cache with L1 (memory) and L2 (Redis) tiers."""

    def __init__(self, l1_cache: AsyncInMemoryCache, l2_cache: CacheBackend):
        self.l1 = l1_cache
        self.l2 = l2_cache

    async def get(self, key: str) -> any:
        """Get value with L1 -> L2 -> source fallback."""

        # Try L1 cache first
        value = await self.l1.get(key)
        if value is not None:
            return value

        # Try L2 cache
        value = await self.l2.get(key)
        if value is not None:
            # Populate L1 cache
            await self.l1.set(key, value, ttl=60.0)
            return value

        return None

    async def set(self, key: str, value: any, ttl: float = 60.0) -> None:
        """Set value in both cache levels."""
        # Set in both caches
        await self.l1.set(key, value, ttl=min(ttl, 300.0))  # L1: max 5 minutes
        await self.l2.set(key, value, ttl=ttl)  # L2: full TTL

    async def invalidate(self, key: str) -> None:
        """Invalidate key in both cache levels."""
        await self.l1.set(key, None, ttl=0.0)  # Immediate expiration
        await self.l2.delete(key) if hasattr(self.l2, 'delete') else None

# Usage
l1_cache = AsyncInMemoryCache[str, dict]()
l2_cache = RedisCache()  # Hypothetical Redis backend
multi_cache = MultiLevelCache(l1_cache, l2_cache)
```

#### Cache Invalidation Strategies

```python
from src.utils.cache import AsyncInMemoryCache
import asyncio
from typing import Set

class CacheInvalidationManager:
    """Manages cache invalidation with dependency tracking."""

    def __init__(self):
        self.cache = AsyncInMemoryCache[str, any]()
        self.dependencies: dict[str, Set[str]] = {}  # key -> dependent keys
        self.lock = asyncio.Lock()

    async def set_with_dependencies(
        self,
        key: str,
        value: any,
        ttl: float = 60.0,
        depends_on: list[str] = None
    ) -> None:
        """Set value with dependency tracking."""
        await self.cache.set(key, value, ttl)

        if depends_on:
            async with self.lock:
                for dependency in depends_on:
                    if dependency not in self.dependencies:
                        self.dependencies[dependency] = set()
                    self.dependencies[dependency].add(key)

    async def invalidate_with_dependencies(self, key: str) -> None:
        """Invalidate key and all dependent keys."""
        async with self.lock:
            # Get all dependent keys
            dependent_keys = self.dependencies.get(key, set())

            # Invalidate the key itself
            await self.cache.set(key, None, ttl=0.0)

            # Recursively invalidate dependent keys
            for dependent_key in dependent_keys:
                await self.invalidate_with_dependencies(dependent_key)

            # Clean up dependency tracking
            del self.dependencies[key]

# Usage example
cache_manager = CacheInvalidationManager()

# User profile depends on user data
await cache_manager.set_with_dependencies(
    "user:123",
    user_data,
    ttl=300.0
)
await cache_manager.set_with_dependencies(
    "profile:123",
    profile_data,
    ttl=600.0,
    depends_on=["user:123"]
)

# Invalidating user:123 will also invalidate profile:123
await cache_manager.invalidate_with_dependencies("user:123")
```

## Best Practices

### Cache Key Design

```python
class CacheKeyBuilder:
    """Standardized cache key generation."""

    @staticmethod
    def user_key(user_id: int) -> str:
        return f"user:id:{user_id}"

    @staticmethod
    def user_email_key(email: str) -> str:
        return f"user:email:{email.lower()}"

    @staticmethod
    def session_key(session_id: str) -> str:
        return f"session:{session_id}"

    @staticmethod
    def rate_limit_key(user_id: int, action: str) -> str:
        return f"rate_limit:{user_id}:{action}"

    @staticmethod
    def analytics_key(user_id: int, time_range: str, metric: str) -> str:
        return f"analytics:{user_id}:{time_range}:{metric}"

# Consistent key usage
cache_key = CacheKeyBuilder.user_key(user_id)
await cache.set(cache_key, user_data)
```

### Performance Monitoring

```python
import time
from functools import wraps

class CacheMetrics:
    """Cache performance monitoring."""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.total_time = 0.0
        self.operation_count = 0

    def record_hit(self, duration: float):
        self.hits += 1
        self.total_time += duration
        self.operation_count += 1

    def record_miss(self, duration: float):
        self.misses += 1
        self.total_time += duration
        self.operation_count += 1

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def average_time(self) -> float:
        return self.total_time / self.operation_count if self.operation_count > 0 else 0.0

cache_metrics = CacheMetrics()

def monitor_cache_performance(cache_operation):
    """Decorator to monitor cache performance."""
    @wraps(cache_operation)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await cache_operation(*args, **kwargs)
        duration = time.time() - start_time

        if result is not None:
            cache_metrics.record_hit(duration)
        else:
            cache_metrics.record_miss(duration)

        return result
    return wrapper

# Usage
@monitor_cache_performance
async def get_cached_data(key: str):
    return await cache.get(key)
```

### Testing Strategies

```python
import pytest
from src.utils.cache import AsyncInMemoryCache

class TestAsyncInMemoryCache:
    """Comprehensive cache testing."""

    @pytest.fixture
    async def cache(self):
        return AsyncInMemoryCache[str, dict]()

    @pytest.mark.asyncio
    async def test_basic_operations(self, cache):
        """Test basic cache operations."""
        # Test set and get
        test_data = {"key": "value", "number": 42}
        await cache.set("test_key", test_data, ttl=60.0)

        result = await cache.get("test_key")
        assert result == test_data

    @pytest.mark.asyncio
    async def test_expiration(self, cache):
        """Test TTL expiration."""
        await cache.set("expire_key", {"data": "test"}, ttl=0.1)  # 100ms

        # Should be available immediately
        result = await cache.get("expire_key")
        assert result is not None

        # Wait for expiration
        await asyncio.sleep(0.2)

        # Should be expired
        result = await cache.get("expire_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_concurrent_access(self, cache):
        """Test thread safety under concurrent access."""
        async def set_operation(i):
            await cache.set(f"key_{i}", {"value": i}, ttl=60.0)

        async def get_operation(i):
            return await cache.get(f"key_{i}")

        # Concurrent set operations
        await asyncio.gather(*[set_operation(i) for i in range(100)])

        # Concurrent get operations
        results = await asyncio.gather(*[get_operation(i) for i in range(100)])

        # Verify all operations completed successfully
        for i, result in enumerate(results):
            assert result == {"value": i}

    @pytest.mark.asyncio
    async def test_clear_cache(self, cache):
        """Test cache clearing."""
        # Add multiple entries
        for i in range(10):
            await cache.set(f"key_{i}", {"value": i}, ttl=60.0)

        # Verify entries exist
        result = await cache.get("key_5")
        assert result is not None

        # Clear cache
        await cache.clear()

        # Verify all entries are gone
        for i in range(10):
            result = await cache.get(f"key_{i}")
            assert result is None
```

This caching system provides high-performance, type-safe, and feature-rich in-memory caching capabilities with comprehensive integration patterns for the ReViewPoint platform.
