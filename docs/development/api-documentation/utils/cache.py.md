# Cache Utilities Documentation

## Purpose

The `cache.py` module provides asynchronous in-memory caching functionality for the ReViewPoint application. This module implements a generic, thread-safe cache system with per-key time-to-live (TTL) capabilities, specifically designed for high-performance data caching in async/await environments. The cache is particularly useful for repository layers to reduce database query overhead and improve application response times.

## Architecture

The cache system follows a generic async pattern:

- **Generic Type Safety**: TypeScript-style generic implementation with `_K` and `_V` type variables
- **Async/Await Compatible**: Fully asynchronous operations with proper lock management
- **TTL Management**: Per-key expiration with automatic cleanup
- **Thread Safety**: AsyncIO lock protection for concurrent access
- **Memory Efficient**: Tuple-based storage with minimal overhead
- **Singleton Pattern**: Global cache instance for application-wide use

## Core Class

### `AsyncInMemoryCache[_K, _V]`

Generic asynchronous in-memory cache with TTL support and thread safety.

```python
# Example usage - Basic cache operations
cache = AsyncInMemoryCache[str, dict]()

# Store user data with 5-minute TTL
await cache.set("user:123", {"name": "John", "email": "john@example.com"}, ttl=300.0)

# Retrieve cached data
user_data = await cache.get("user:123")
if user_data:
    print(f"Found cached user: {user_data['name']}")
else:
    print("User not found or expired")
```

**Generic Type Parameters:**

- `_K` - Key type (bound to `str` for string keys only)
- `_V` - Value type (any type that needs caching)

**Core Features:**

- Automatic expiration based on TTL
- Thread-safe concurrent access
- Memory-efficient storage
- Type-safe operations

## Field Specifications

### Internal Storage

**Cache Storage:**

```python
_cache: MutableMapping[_K, tuple[_V | None, float]]
```

- **Type**: `MutableMapping` with tuple values `(value, expires_timestamp)`
- **Thread Safety**: Protected by AsyncIO lock
- **Value Structure**: `(cached_value, expiration_time)`
- **Key Constraint**: Keys must be strings (`_K` bound to `str`)

**Lock Management:**

```python
_lock: asyncio.Lock
```

- **Type**: AsyncIO Lock for thread safety
- **Scope**: Protects all cache operations
- **Initialization**: Created during cache instance construction
- **Usage**: Acquired for all read/write operations

## Core Methods

### Cache Retrieval

**Get Operation with Expiration Check:**

```python
async def get(self, key: _K) -> _V | None:
    """Get a value from the cache by key. Returns None if not found or expired."""
```

**Implementation Details:**

- **Lock Acquisition**: Thread-safe access with async context manager
- **Expiration Logic**: Automatic comparison with current event loop time
- **Cleanup**: Expired entries are automatically removed
- **Return Value**: Original value or `None` for missing/expired entries

**Advanced Usage Example:**

```python
# Repository pattern with cache fallback
async def get_user_by_id(user_id: str) -> User | None:
    # Try cache first
    cached_user = await user_cache.get(f"user:{user_id}")
    if cached_user:
        return User.from_dict(cached_user)

    # Cache miss - query database
    user = await database.fetch_user(user_id)
    if user:
        # Cache for 15 minutes
        await user_cache.set(f"user:{user_id}", user.to_dict(), ttl=900.0)

    return user
```

### Cache Storage

**Set Operation with TTL:**

```python
async def set(self, key: _K, value: _V, ttl: float = 60.0) -> None:
    """Set a value in the cache with a time-to-live (ttl) in seconds."""
```

**TTL Calculation:**

- **Current Time**: Uses `asyncio.get_event_loop().time()` for precision
- **Expiration**: `current_time + ttl_seconds`
- **Default TTL**: 60 seconds if not specified
- **Storage Format**: `(value, expiration_timestamp)` tuple

**Cache Patterns:**

```python
# Short-term API response cache (30 seconds)
await cache.set("api:health_status", {"status": "healthy"}, ttl=30.0)

# Medium-term user session cache (1 hour)
await cache.set("session:abc123", session_data, ttl=3600.0)

# Long-term configuration cache (24 hours)
await cache.set("config:app_settings", config, ttl=86400.0)
```

### Cache Management

**Clear All Entries:**

```python
async def clear(self) -> None:
    """Clear all items from the cache."""
```

**Use Cases:**

- Application shutdown cleanup
- Cache invalidation after major updates
- Memory pressure management
- Testing environment reset

## Global Cache Instance

### Singleton User Cache

**Pre-configured Instance:**

```python
user_cache: Final[AsyncInMemoryCache[str, object]] = AsyncInMemoryCache[str, object]()
```

**Configuration:**

- **Type**: `AsyncInMemoryCache[str, object]` for maximum flexibility
- **Scope**: Application-wide singleton for user-related caching
- **Immutability**: `Final` annotation prevents reassignment
- **Usage**: Import and use directly in repository layers

**Repository Integration Example:**

```python
from src.utils.cache import user_cache

class UserRepository:
    async def get_user_by_email(self, email: str) -> User | None:
        # Check cache first
        cache_key = f"user:email:{email}"
        cached_data = await user_cache.get(cache_key)

        if cached_data:
            return User.from_dict(cached_data)

        # Database query on cache miss
        user = await self._fetch_user_from_db(email)

        if user:
            # Cache successful lookups for 10 minutes
            await user_cache.set(cache_key, user.to_dict(), ttl=600.0)

        return user

    async def invalidate_user_cache(self, user_id: str, email: str) -> None:
        """Remove user from cache after updates"""
        await user_cache.set(f"user:{user_id}", None, ttl=0.0)
        await user_cache.set(f"user:email:{email}", None, ttl=0.0)
```

## Advanced Usage Patterns

### Cache-Aside Pattern

```python
async def get_user_profile(user_id: str) -> UserProfile:
    """Implement cache-aside pattern for user profiles."""

    cache_key = f"profile:{user_id}"

    # 1. Check cache first
    cached_profile = await user_cache.get(cache_key)
    if cached_profile:
        return UserProfile.from_dict(cached_profile)

    # 2. Cache miss - load from database
    profile = await load_profile_from_database(user_id)

    # 3. Store in cache for future requests
    if profile:
        await user_cache.set(cache_key, profile.to_dict(), ttl=1800.0)  # 30 minutes

    return profile

async def update_user_profile(user_id: str, profile_data: dict) -> UserProfile:
    """Update profile and invalidate cache."""

    # 1. Update database
    updated_profile = await update_profile_in_database(user_id, profile_data)

    # 2. Update cache with fresh data
    cache_key = f"profile:{user_id}"
    await user_cache.set(cache_key, updated_profile.to_dict(), ttl=1800.0)

    return updated_profile
```

### Multi-Level Caching Strategy

```python
class CacheManager:
    """Advanced caching with multiple cache levels."""

    def __init__(self):
        self.l1_cache = AsyncInMemoryCache[str, dict]()  # Fast, short TTL
        self.l2_cache = AsyncInMemoryCache[str, dict]()  # Slower, long TTL

    async def get_with_fallback(self, key: str) -> dict | None:
        """Try L1 cache, then L2 cache, then data source."""

        # Level 1: Fast cache (1 minute TTL)
        data = await self.l1_cache.get(key)
        if data:
            return data

        # Level 2: Long-term cache (1 hour TTL)
        data = await self.l2_cache.get(key)
        if data:
            # Promote to L1 cache
            await self.l1_cache.set(key, data, ttl=60.0)
            return data

        # Cache miss - load from data source
        data = await self._load_from_source(key)
        if data:
            # Store in both cache levels
            await self.l1_cache.set(key, data, ttl=60.0)
            await self.l2_cache.set(key, data, ttl=3600.0)

        return data
```

### Cache Warming Strategies

```python
async def warm_user_cache() -> None:
    """Pre-populate cache with frequently accessed users."""

    # Get most active users from database
    active_users = await get_most_active_users(limit=100)

    tasks = []
    for user in active_users:
        # Warm cache with user data
        cache_key = f"user:{user.id}"
        task = user_cache.set(cache_key, user.to_dict(), ttl=3600.0)
        tasks.append(task)

    # Execute all cache operations concurrently
    await asyncio.gather(*tasks)
    logger.info(f"Warmed cache with {len(active_users)} user records")

async def background_cache_maintenance() -> None:
    """Background task for cache maintenance."""

    while True:
        try:
            # Warm cache every hour
            await warm_user_cache()
            await asyncio.sleep(3600)  # 1 hour

        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
            await asyncio.sleep(300)  # Retry in 5 minutes
```

## Performance Considerations

### Memory Management

**Memory Efficiency:**

```python
# Efficient data structures
async def optimize_cache_memory() -> dict:
    """Monitor and optimize cache memory usage."""

    cache_stats = {
        "total_entries": len(user_cache._cache),
        "estimated_memory_kb": 0,
        "expired_entries": 0
    }

    current_time = asyncio.get_event_loop().time()
    expired_keys = []

    # Calculate memory usage and find expired entries
    for key, (value, expires) in user_cache._cache.items():
        if expires < current_time:
            expired_keys.append(key)
            cache_stats["expired_entries"] += 1
        else:
            # Rough memory estimation
            cache_stats["estimated_memory_kb"] += len(str(value)) / 1024

    # Clean up expired entries
    for key in expired_keys:
        user_cache._cache.pop(key, None)

    return cache_stats
```

### Concurrency Optimization

**Lock Contention Minimization:**

```python
class HighPerformanceCache(AsyncInMemoryCache[str, dict]):
    """Enhanced cache with reduced lock contention."""

    async def get_batch(self, keys: list[str]) -> dict[str, dict | None]:
        """Batch get operation to reduce lock acquisition overhead."""

        results = {}
        current_time = asyncio.get_event_loop().time()

        async with self._lock:
            for key in keys:
                value, expires = self._cache.get(key, (None, 0.0))

                if expires and expires < current_time:
                    self._cache.pop(key, None)
                    results[key] = None
                else:
                    results[key] = value

        return results

    async def set_batch(self, items: dict[str, dict], ttl: float = 60.0) -> None:
        """Batch set operation for multiple items."""

        expires = asyncio.get_event_loop().time() + ttl

        async with self._lock:
            for key, value in items.items():
                self._cache[key] = (value, expires)
```

## Error Handling

### Cache Operation Safety

```python
async def safe_cache_get(key: str, default: _V | None = None) -> _V | None:
    """Safely get from cache with error handling."""

    try:
        return await user_cache.get(key)
    except Exception as e:
        logger.error(f"Cache get failed for key {key}: {e}")
        return default

async def safe_cache_set(key: str, value: _V, ttl: float = 60.0) -> bool:
    """Safely set cache value with error handling."""

    try:
        await user_cache.set(key, value, ttl)
        return True
    except Exception as e:
        logger.error(f"Cache set failed for key {key}: {e}")
        return False

class CacheCircuitBreaker:
    """Circuit breaker for cache operations."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = 0.0
        self.is_open = False

    async def call(self, cache_operation: callable, *args, **kwargs):
        """Execute cache operation with circuit breaker protection."""

        current_time = asyncio.get_event_loop().time()

        # Check if circuit breaker should be reset
        if self.is_open and (current_time - self.last_failure_time) > self.recovery_timeout:
            self.is_open = False
            self.failure_count = 0

        # If circuit is open, fail fast
        if self.is_open:
            raise Exception("Cache circuit breaker is open")

        try:
            result = await cache_operation(*args, **kwargs)
            # Reset failure count on success
            self.failure_count = 0
            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = current_time

            # Open circuit if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
                logger.warning("Cache circuit breaker opened due to failures")

            raise e
```

## Testing Strategies

### Unit Testing

```python
import pytest
import asyncio
from src.utils.cache import AsyncInMemoryCache

class TestAsyncInMemoryCache:
    @pytest.fixture
    async def cache(self):
        """Create a fresh cache for each test."""
        return AsyncInMemoryCache[str, dict]()

    async def test_basic_operations(self, cache):
        """Test basic cache set and get operations."""

        # Test set and get
        test_data = {"name": "test", "value": 123}
        await cache.set("test_key", test_data, ttl=60.0)

        result = await cache.get("test_key")
        assert result == test_data

    async def test_expiration(self, cache):
        """Test TTL expiration functionality."""

        # Set with very short TTL
        await cache.set("expire_test", {"data": "value"}, ttl=0.1)

        # Should be available immediately
        result = await cache.get("expire_test")
        assert result is not None

        # Wait for expiration
        await asyncio.sleep(0.2)

        # Should be expired and return None
        result = await cache.get("expire_test")
        assert result is None

    async def test_concurrent_access(self, cache):
        """Test thread safety with concurrent operations."""

        async def set_operation(key: str, value: dict):
            await cache.set(key, value, ttl=60.0)

        async def get_operation(key: str) -> dict | None:
            return await cache.get(key)

        # Run concurrent operations
        tasks = []
        for i in range(10):
            tasks.append(set_operation(f"key_{i}", {"value": i}))
            tasks.append(get_operation(f"key_{i}"))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify no exceptions occurred
        for result in results:
            assert not isinstance(result, Exception)
```

### Integration Testing

```python
async def test_repository_cache_integration():
    """Test cache integration with repository pattern."""

    from src.repositories.user import UserRepository
    from src.utils.cache import user_cache

    # Clear cache before test
    await user_cache.clear()

    repo = UserRepository()

    # First call should hit database
    user1 = await repo.get_user_by_id("test_user_123")

    # Second call should hit cache
    user2 = await repo.get_user_by_id("test_user_123")

    # Verify same data returned
    assert user1.to_dict() == user2.to_dict()

    # Verify cache was used (check cache directly)
    cached_data = await user_cache.get("user:test_user_123")
    assert cached_data is not None
```

## Best Practices

### Cache Key Design

- **Hierarchical Keys**: Use colon-separated namespaces (`user:123`, `session:abc`, `config:app`)
- **Descriptive Names**: Include entity type and identifier in key names
- **Consistent Patterns**: Maintain consistent naming conventions across application
- **Avoid Collisions**: Use prefixes to prevent key collisions between different data types

### TTL Management

- **Match Data Volatility**: Short TTL for frequently changing data, long TTL for stable data
- **Cache Warming**: Pre-populate cache for predictable access patterns
- **Graceful Degradation**: Application should work when cache is unavailable
- **Cache Invalidation**: Implement proper invalidation on data updates

### Performance Optimization

- **Batch Operations**: Use batch methods to reduce lock contention
- **Memory Monitoring**: Track cache size and implement cleanup strategies
- **Circuit Breakers**: Implement failsafe mechanisms for cache failures
- **Async Patterns**: Use proper async/await patterns to avoid blocking

## Related Files

### Dependencies

- `asyncio` - Asynchronous event loop and locking primitives
- `collections.abc.MutableMapping` - Type annotations for cache storage
- `typing` - Generic type support and type safety

### Integration Points

- `src.repositories.user` - User repository caching implementation
- `src.repositories.file` - File metadata caching
- `src.services.auth` - Authentication token caching
- `src.api.v1.users` - API endpoint caching

### Configuration

- `src.core.config` - Cache configuration settings
- `src.core.logging` - Cache operation logging
- Background tasks for cache maintenance and warming

## Configuration

### Cache Settings

```python
# Cache configuration
CACHE_CONFIG = {
    "default_ttl": 60.0,  # Default TTL in seconds
    "max_memory_mb": 128,  # Maximum memory usage
    "cleanup_interval": 300,  # Cleanup expired entries every 5 minutes
    "enable_metrics": True,  # Enable cache performance metrics
}

# Environment-specific TTL values
TTL_SETTINGS = {
    "user_profile": 1800,    # 30 minutes
    "user_session": 3600,    # 1 hour
    "api_response": 300,     # 5 minutes
    "configuration": 86400,  # 24 hours
}
```

This cache utility provides a robust foundation for high-performance data caching in the ReViewPoint application, enabling significant performance improvements through intelligent data retention and fast in-memory access patterns.
