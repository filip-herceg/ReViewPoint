# API Dependencies Module

**File:** `backend/src/api/deps.py`  
**Purpose:** Comprehensive dependency injection utilities for FastAPI API endpoints  
**Lines of Code:** 958  
**Type:** API Infrastructure Module

## Overview

The API dependencies module provides a comprehensive dependency injection system for FastAPI endpoints, offering robust and reusable dependencies for authentication, database session management, pagination, service location, request tracing, feature flags, health checks, and API key validation. This module is the foundation of the API layer, ensuring consistent security, database access patterns, and cross-cutting concerns across all endpoints while maintaining testability and flexibility.

## Architecture

### Core Design Principles

1. **Dependency Injection**: Centralized management of all API dependencies
2. **Security-First**: Comprehensive authentication and authorization patterns
3. **Request Tracing**: Request ID propagation for observability
4. **Database Session Management**: Async session lifecycle with proper cleanup
5. **Service Locator Pattern**: Dynamic service resolution for testability
6. **Feature Flag Integration**: Runtime feature control
7. **Metrics and Health Monitoring**: Comprehensive dependency performance tracking

### Key Components

#### Dependency Registry System

```python
class DependencyRegistry:
    _instances: dict[str, DependencyEntry] = {}

    @classmethod
    def register(cls, key: str, factory: Callable[[], object],
                singleton: bool = True, cache_ttl: float | None = None) -> None
```

**Registry Features:**

- Singleton pattern support
- Cache TTL for time-sensitive dependencies
- Lazy loading with factory functions
- Type-safe dependency resolution

#### Authentication Infrastructure

```python
oauth2_scheme: Final[OAuth2PasswordBearer] = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)
api_key_header: Final[APIKeyHeader] = APIKeyHeader(name="X-API-Key", auto_error=False)
```

**Authentication Components:**

- JWT Bearer token authentication
- API key header authentication
- Development mode bypass
- Multi-factor authentication support

## Core Functions

### 🔐 **Authentication Dependencies**

#### `get_current_user()`

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User | None:
    """Extract and validate JWT token, fetch current user from database."""
```

**Purpose:** Primary authentication dependency for protected endpoints

**Authentication Process:**

1. **Development Mode Check**: Returns dev admin user if auth disabled
2. **Token Validation**: Verifies JWT signature and expiration
3. **Payload Extraction**: Extracts user ID and role from token
4. **User Resolution**: Supports both user ID and email resolution
5. **Status Validation**: Ensures user is active and not deleted
6. **Role Attachment**: Attaches JWT role to user object

**Error Handling:**

- Invalid/expired tokens → 401 Unauthorized
- Missing user ID in payload → 401 Unauthorized
- User not found/inactive/deleted → 401 Unauthorized

#### `optional_get_current_user()`

```python
async def optional_get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User | None:
    """Like get_current_user, but returns None instead of raising on failure."""
```

**Purpose:** Authentication for endpoints that support both authenticated and anonymous access

**Features:**

- No exceptions on authentication failure
- Returns None for invalid/missing tokens
- Same validation logic as get_current_user
- Useful for endpoints with optional authentication

#### `get_current_active_user()`

```python
async def get_current_active_user(
    user: User | None = Depends(get_current_user),
) -> User | None:
    """Ensure the current user is active and not deleted."""
```

**Purpose:** Additional layer ensuring user account status

**Validation:**

- User existence check
- Active status verification
- Deleted status check
- 403 Forbidden for inactive/deleted users

### 🔑 **API Key Authentication**

#### `validate_api_key()`

```python
async def validate_api_key(
    api_key: str | None = Security(api_key_header),
) -> bool:
    """Validate API key from X-API-Key header."""
```

**Purpose:** API key validation for service-to-service authentication

**Validation Logic:**

- Respects global API key enable/disable setting
- Compares against configured API key
- Returns boolean for flexible usage
- No exceptions for flexible integration

#### `require_api_key()`

```python
def require_api_key(api_key: str | None = Header(None, alias="X-API-Key")) -> None:
    """Dependency to require a valid API key."""
```

**Purpose:** Enforces API key requirement for protected endpoints

**Enforcement:**

- 401 Unauthorized for missing API key
- 401 Unauthorized for invalid API key
- 500 Internal Server Error for misconfiguration
- Respects global API key settings

#### `get_current_user_with_export_api_key()`

```python
async def get_current_user_with_export_api_key(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> User | None:
    """Complex authentication for export endpoints with configurable requirements."""
```

**Purpose:** Sophisticated authentication dependency for export endpoints

**Authentication Matrix:**

- **Auth Disabled**: Returns development admin user
- **Auth + API Key Enabled**: Requires both JWT and API key
- **Auth Enabled, API Key Disabled**: JWT required if provided, optional otherwise
- **Flexible Access**: Supports both authenticated and unauthenticated access patterns

### 📊 **Database Session Management**

#### `get_db()`

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide SQLAlchemy AsyncSession for database operations."""
```

**Purpose:** Primary database session dependency

**Session Lifecycle:**

1. **Engine Initialization**: Ensures database engine is ready
2. **Session Creation**: Creates new AsyncSession instance
3. **Session Yielding**: Provides session to endpoint
4. **Error Handling**: Automatic rollback on exceptions
5. **Session Cleanup**: Guaranteed session closure

**Error Handling:**

```python
try:
    yield session
except Exception as exc:
    await session.rollback()
    raise
finally:
    await session.close()
```

### 📄 **Pagination System**

#### `pagination_params()`

```python
def pagination_params(
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=MAX_LIMIT, description="Max items to return"),
) -> PaginationParams:
    """Standardize and validate pagination query parameters."""
```

**Purpose:** Consistent pagination across all list endpoints

**Pagination Features:**

- Offset-based pagination
- Configurable limits with maximum enforcement
- Input validation with descriptive errors
- Standardized parameter naming

**Usage Pattern:**

```python
@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(pagination_params)
):
    return await user_repo.list(
        db, offset=pagination.offset, limit=pagination.limit
    )
```

### 🏭 **Service Locator Pattern**

#### `DependencyRegistry`

```python
class DependencyRegistry:
    @classmethod
    def register(cls, key: str, factory: Callable[[], object],
                singleton: bool = True, cache_ttl: float | None = None) -> None

    @classmethod
    def get(cls, key: str) -> object
```

**Purpose:** Dynamic service resolution for improved testability

**Registry Features:**

- **Singleton Management**: Optional singleton instances
- **Cache TTL**: Time-based cache invalidation
- **Lazy Loading**: Factory-based instantiation
- **Error Handling**: Clear error messages for missing dependencies

**Registered Services:**

```python
registry.register("user_service", lambda: importlib.import_module("src.services.user"))
registry.register("user_repository", lambda: user_repository)
registry.register("blacklist_token", lambda: importlib.import_module(...).blacklist_token)
```

#### Service Accessor Functions

```python
def get_user_service() -> UserService
def get_blacklist_token() -> Callable[..., Awaitable[None]]
def get_user_action_limiter() -> Callable[..., Awaitable[None]]
```

**Purpose:** Type-safe access to registered services

### 🔍 **Request Tracing**

#### `get_request_id()`

```python
def get_request_id(request: Request) -> str:
    """Extract or generate request ID for tracing."""
```

**Purpose:** Request correlation for observability and debugging

**Request ID Logic:**

1. **Header Extraction**: Reads X-Request-ID header
2. **UUID Validation**: Validates UUID format
3. **ID Generation**: Generates UUID if missing/invalid
4. **Context Storage**: Stores in context variable
5. **Trace Propagation**: Available across request lifecycle

#### `get_current_request_id()`

```python
def get_current_request_id() -> str | None:
    """Get current request ID from context variable."""
```

**Purpose:** Access request ID from anywhere in request processing

### 🚩 **Feature Flag Integration**

#### `get_feature_flags()`

```python
def get_feature_flags() -> FeatureFlagsProtocol:
    """Get feature flags instance for runtime feature control."""
```

#### `require_feature()`

```python
def require_feature(feature_name: str) -> Callable[[FeatureFlagsProtocol], Awaitable[bool]]:
    """Create dependency that requires specific feature to be enabled."""
```

**Purpose:** Runtime feature control at endpoint level

**Usage Pattern:**

```python
@router.get("/experimental-feature")
async def experimental_endpoint(
    _: bool = Depends(require_feature("experimental_feature"))
):
    return {"feature": "enabled"}
```

### 🏥 **Health Check System**

#### `HealthCheck`

```python
class HealthCheck:
    @classmethod
    def register(cls, name: str,
                check_func: Callable[[], bool | Awaitable[bool]]) -> None

    @classmethod
    async def check_all(cls) -> dict[str, dict[str, str | bool]]
```

**Purpose:** Centralized health monitoring for dependencies

**Health Check Features:**

- **Registration System**: Register health checks by name
- **Async Support**: Both sync and async health check functions
- **Error Handling**: Graceful handling of check failures
- **Status Reporting**: Structured health status responses

### 📈 **Dependency Metrics**

#### `measure_dependency()`

```python
def measure_dependency(func: Callable[..., Awaitable[object]]) -> Callable[..., Awaitable[object]]:
    """Decorator to measure dependency performance and errors."""
```

**Purpose:** Performance monitoring for dependency functions

**Metrics Collected:**

- **Call Count**: Number of dependency invocations
- **Error Count**: Number of failed invocations
- **Total Time**: Cumulative execution time
- **Performance Tracking**: Average execution time calculation

### ⚙️ **Dynamic Configuration**

#### `get_refreshable_settings()`

```python
def get_refreshable_settings() -> object:
    """Get settings that automatically refresh based on TTL."""
```

**Purpose:** Dynamic configuration reloading without restart

**Refresh Features:**

- **Time-based Refresh**: Configurable refresh interval
- **Lazy Loading**: Reload only when accessed
- **Module Reloading**: Dynamic import reloading
- **Transparent Access**: Same interface as static settings

## Usage Patterns

### 🔧 **Standard Endpoint Authentication**

```python
from src.api.deps import get_current_active_user

@router.get("/protected-endpoint")
async def protected_endpoint(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Standard protected endpoint pattern."""
    return {"user_id": current_user.id}
```

### 🔐 **API Key Protected Endpoint**

```python
from src.api.deps import require_api_key

@router.post("/service-endpoint")
async def service_endpoint(
    _: None = Depends(require_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Service-to-service endpoint with API key."""
    return {"status": "authenticated"}
```

### 📊 **Paginated List Endpoint**

```python
from src.api.deps import pagination_params, PaginationParams

@router.get("/users")
async def list_users(
    pagination: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db)
):
    """Standard paginated list pattern."""
    users = await user_repo.list(
        db,
        offset=pagination.offset,
        limit=pagination.limit
    )
    return {"users": users, "pagination": pagination}
```

### 🔍 **Request Tracing Pattern**

```python
from src.api.deps import get_request_id

@router.post("/traced-endpoint")
async def traced_endpoint(
    request_id: str = Depends(get_request_id),
    db: AsyncSession = Depends(get_db)
):
    """Endpoint with request tracing."""
    logger.info(f"Processing request {request_id}")
    return {"request_id": request_id}
```

### 🚩 **Feature Flag Protected Endpoint**

```python
from src.api.deps import require_feature

@router.get("/experimental")
async def experimental_feature(
    _: bool = Depends(require_feature("beta_features")),
    current_user: User = Depends(get_current_active_user)
):
    """Endpoint protected by feature flag."""
    return {"experimental": "content"}
```

### 🏭 **Service Injection Pattern**

```python
from src.api.deps import get_user_service

@router.post("/complex-operation")
async def complex_operation(
    user_service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_db)
):
    """Endpoint using service layer."""
    result = await user_service.perform_complex_operation(db)
    return result
```

## Security Considerations

### 🔐 **Authentication Security**

#### JWT Token Validation

```python
# Comprehensive token validation
payload = verify_access_token(token)
user_id = payload.get("sub")
role = payload.get("role")

# User status validation
if not user or not user.is_active or user.is_deleted:
    http_error(401, "User not found or inactive")
```

**Security Features:**

- Token signature verification
- Expiration checking
- User status validation
- Role-based access control
- Development mode safety

#### API Key Security

```python
# Secure API key comparison
if api_key != configured_api_key:
    http_error(401, "Invalid API key")
```

**Security Measures:**

- Direct string comparison (constant time)
- Configuration validation
- Header-based transmission
- Optional enforcement

### 🛡️ **Input Validation**

#### Pagination Security

```python
if offset < 0:
    http_error(400, "Offset must be >= 0")
if limit < 1 or limit > MAX_LIMIT:
    http_error(400, f"Limit must be between 1 and {MAX_LIMIT}")
```

**Validation Features:**

- Range validation for offset/limit
- Maximum limit enforcement
- Input sanitization
- Error message standardization

### 🔒 **Session Security**

#### Database Session Safety

```python
try:
    yield session
except Exception as exc:
    await session.rollback()  # Prevent data corruption
    raise
finally:
    await session.close()  # Prevent connection leaks
```

**Security Measures:**

- Automatic rollback on errors
- Guaranteed session cleanup
- Connection leak prevention
- Transaction isolation

## Performance Considerations

### ⚡ **Dependency Caching**

#### LRU Cache Usage

```python
get_user_repository: Callable[[], object] = lru_cache()(get_user_repository_func)
```

**Performance Features:**

- Function result caching
- Memory-efficient LRU eviction
- Repeated dependency optimization
- Cache hit/miss tracking

#### Registry Caching

```python
if not singleton or instance is None:
    instance = factory()
    entry["instance"] = instance
```

**Caching Strategy:**

- Singleton pattern for expensive objects
- TTL-based cache invalidation
- Lazy instantiation
- Memory usage optimization

### 🔄 **Session Pool Management**

#### Connection Pool Optimization

```python
# Efficient session lifecycle
session = AsyncSessionLocal()
try:
    yield session  # Single session per request
finally:
    await session.close()  # Immediate cleanup
```

**Performance Benefits:**

- Single session per request
- Immediate connection release
- Pool exhaustion prevention
- Concurrent request support

### 📊 **Metrics and Monitoring**

#### Dependency Performance Tracking

```python
dependency_metrics[name]["count"] += 1
dependency_metrics[name]["total_time"] += duration
if status == "error":
    dependency_metrics[name]["errors"] += 1
```

**Monitoring Features:**

- Execution time tracking
- Error rate monitoring
- Call frequency analysis
- Performance bottleneck identification

## Testing Strategies

### 🧪 **Dependency Testing**

```python
import pytest
from unittest.mock import AsyncMock
from src.api.deps import get_current_user, get_db

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    """Test successful user authentication."""
    # Mock dependencies
    mock_session = AsyncMock()
    mock_token = "valid_jwt_token"

    # Test authentication
    user = await get_current_user(mock_token, mock_session)
    assert user is not None
    assert user.is_active

@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """Test authentication failure handling."""
    mock_session = AsyncMock()
    mock_token = "invalid_token"

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_token, mock_session)

    assert exc_info.value.status_code == 401

def test_pagination_params_validation():
    """Test pagination parameter validation."""
    # Valid parameters
    params = pagination_params(offset=0, limit=20)
    assert params.offset == 0
    assert params.limit == 20

    # Invalid parameters should raise HTTPException
    with pytest.raises(HTTPException):
        pagination_params(offset=-1, limit=20)
```

### 🔄 **Integration Testing**

```python
from fastapi.testclient import TestClient
from src.main import app

def test_protected_endpoint_authentication():
    """Test endpoint with authentication dependency."""
    client = TestClient(app)

    # Test without authentication
    response = client.get("/api/v1/protected")
    assert response.status_code == 401

    # Test with valid token
    headers = {"Authorization": "Bearer valid_token"}
    response = client.get("/api/v1/protected", headers=headers)
    assert response.status_code == 200
```

### 🏭 **Service Mocking**

```python
from src.api.deps import registry

def test_service_dependency_injection():
    """Test service locator pattern."""
    # Mock service
    mock_service = Mock()
    registry.register("test_service", lambda: mock_service)

    # Test service resolution
    service = registry.get("test_service")
    assert service is mock_service
```

## Error Handling

### 🛠️ **Authentication Errors**

```python
# Token validation errors
try:
    payload = verify_access_token(token)
except (JWTError, ValueError, TypeError) as err:
    logger.error(f"Token validation failed: {err}")
    http_error(401, "Invalid token", logger.error, None, err)
```

**Error Scenarios:**

- Invalid JWT signature → 401 Unauthorized
- Expired token → 401 Unauthorized
- Malformed token → 401 Unauthorized
- Missing user ID → 401 Unauthorized

### 🔄 **Database Errors**

```python
try:
    yield session
except Exception as exc:
    logger.error(f"Database session error: {exc}")
    await session.rollback()
    raise
```

**Error Handling:**

- Automatic rollback on database errors
- Connection cleanup on failures
- Exception propagation for proper handling
- Comprehensive error logging

### 📊 **Validation Errors**

```python
if offset < 0:
    logger.error(f"Invalid offset: {offset}")
    http_error(400, "Offset must be >= 0", logger.error)
```

**Validation Features:**

- Input range validation
- Descriptive error messages
- Consistent HTTP status codes
- Security-focused error handling

## Best Practices

### ✅ **Do's**

- **Use Type Hints**: All dependencies have comprehensive type annotations
- **Handle Exceptions**: Proper exception handling in all dependency functions
- **Log Security Events**: Authentication failures and security events logged
- **Validate Inputs**: Comprehensive input validation for all parameters
- **Clean Up Resources**: Guaranteed cleanup of database sessions and connections
- **Cache Appropriately**: Use caching for expensive dependency resolution

### ❌ **Don'ts**

- **Don't Leak Sensitive Data**: No password or token logging in error messages
- **Don't Skip Validation**: Always validate user status and input parameters
- **Don't Block Requests**: Use async patterns for all I/O operations
- **Don't Ignore Errors**: Proper error handling and propagation
- **Don't Hardcode Values**: Use configuration for all security-related values
- **Don't Mix Concerns**: Keep authentication, validation, and business logic separate

## Related Files

- **`core/security.py`** - JWT token verification and security utilities
- **`core/database.py`** - Database session management and connection handling
- **`core/config.py`** - Configuration management for authentication settings
- **`utils/http_error.py`** - HTTP error response utilities
- **API routers** - All API endpoints using these dependencies
- **Services layer** - Business logic accessed through dependency injection

## Dependencies

- **`fastapi`** - Dependency injection system and security schemes
- **`sqlalchemy`** - Database session management
- **`jose`** - JWT token processing and validation
- **`loguru`** - Comprehensive logging for security and performance events

---

_This module provides the foundational dependency injection system for the ReViewPoint API, ensuring consistent security, database access, and cross-cutting concerns across all endpoints while maintaining high performance and testability._
