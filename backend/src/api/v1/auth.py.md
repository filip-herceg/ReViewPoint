# Authentication API Router

**File:** `backend/src/api/v1/auth.py`  
**Purpose:** FastAPI authentication endpoints for user registration, login, logout, token refresh, password reset, and profile access  
**Lines of Code:** 787  
**Type:** API Router Module  

## Overview

The Authentication API Router provides comprehensive user authentication functionality through RESTful endpoints. This module implements secure authentication flows including user registration, login/logout, JWT token management, password reset workflows, and user profile access. Built with FastAPI, it integrates rate limiting, feature flags, API key protection, and comprehensive error handling to ensure robust and secure authentication services.

## Architecture

### Core Design Principles

1. **Security-First**: All endpoints protected with API keys and feature flags
2. **Rate Limiting**: Comprehensive rate limiting for abuse prevention
3. **Error Handling**: Consistent error responses with proper HTTP status codes
4. **Audit Logging**: Comprehensive logging for security monitoring
5. **Token Management**: JWT access/refresh token patterns
6. **Input Validation**: Strong validation for all user inputs

### Authentication Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Register     │    │      Login      │    │   Password      │
│   /register     │    │     /login      │    │     Reset       │
│                 │    │                 │    │                 │
│ • Validation    │    │ • Credentials   │    │ • Request       │
│ • User Creation │    │ • JWT Tokens    │    │ • Token Verify  │
│ • Auto-Login    │    │ • User Profile  │    │ • Password Set  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Token Mgmt    │
                    │                 │
                    │ • Refresh       │
                    │ • Logout        │
                    │ • Blacklist     │
                    └─────────────────┘
```

## Core Endpoints

### 🔐 **User Registration**

#### `POST /register`
```python
@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    data: UserRegisterRequest,
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    user_action_limiter: UserActionLimiterProtocol = Depends(get_user_action_limiter),
) -> AuthResponse:
```

**Purpose:** Create new user account with immediate authentication

**Process Flow:**
1. **Rate Limit Check**: 5 attempts per email per hour
2. **Input Validation**: Email format, password strength, name optional
3. **Uniqueness Check**: Ensure email not already registered
4. **User Creation**: Create account with hashed password
5. **Auto-Login**: Generate and return JWT tokens
6. **Audit Logging**: Log registration attempt and success/failure

**Request Schema:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "Jane Doe"  // Optional
}
```

**Response Schema:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Error Handling:**
- `400 Bad Request`: Invalid input data or user already exists
- `429 Too Many Requests`: Rate limit exceeded
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Unexpected server errors

### 🔑 **User Login**

#### `POST /login`
```python
@router.post("/login", response_model=AuthResponse)
async def login(
    data: UserLoginRequest,
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    user_action_limiter: UserActionLimiterProtocol = Depends(get_user_action_limiter),
) -> AuthResponse:
```

**Purpose:** Authenticate user credentials and issue JWT tokens

**Authentication Process:**
1. **Rate Limit Check**: 10 attempts per IP per minute
2. **Credential Validation**: Email and password verification
3. **Account Status Check**: Ensure account is active and not locked
4. **Token Generation**: Create access and refresh tokens
5. **Login Logging**: Log authentication success/failure

**Security Features:**
- **Password Verification**: Timing attack protection with bcrypt
- **Account Lockout**: Protection against brute force attacks
- **Token Security**: Cryptographically signed JWT tokens
- **IP Rate Limiting**: Per-IP request limiting

**Token Details:**
- **Access Token**: 24-hour validity for API requests
- **Refresh Token**: 7-day validity for token renewal
- **Token Type**: Bearer (Authorization header format)

### 🚪 **User Logout**

#### `POST /logout`
```python
@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    blacklist_token: Callable = Depends(get_blacklist_token),
) -> MessageResponse:
```

**Purpose:** Securely log out user and invalidate current session

**Logout Process:**
1. **Token Extraction**: Extract JWT from Authorization header
2. **Token Validation**: Verify token signature and expiration
3. **Token Blacklisting**: Add token to blacklist database
4. **Session Cleanup**: Clear user session data
5. **Audit Logging**: Log logout activity

**Security Measures:**
- **Token Blacklisting**: Prevents token reuse after logout
- **Graceful Degradation**: Handles invalid/expired tokens
- **Session Termination**: Complete user session cleanup

### 🔄 **Token Refresh**

#### `POST /refresh-token`
```python
@router.post("/refresh-token", response_model=AuthResponse)
async def refresh_token(
    body: Mapping[str, object] = Body(...),
    session: AsyncSession = Depends(get_db),
    async_refresh_access_token: Callable = Depends(get_async_refresh_access_token),
) -> AuthResponse:
```

**Purpose:** Refresh expired access tokens using valid refresh tokens

**Refresh Process:**
1. **Token Validation**: Verify refresh token signature and expiration
2. **Blacklist Check**: Ensure token hasn't been revoked
3. **Rate Limiting**: Prevent refresh token abuse
4. **New Token Generation**: Issue new access token
5. **Token Rotation**: Optional refresh token rotation

**Flexible Input Format:**
```json
// Option 1
{"token": "refresh_token_here"}

// Option 2  
{"refresh_token": "refresh_token_here"}
```

**Error Scenarios:**
- `401 Unauthorized`: Invalid/expired/blacklisted refresh token
- `429 Too Many Requests`: Rate limit exceeded
- `422 Unprocessable Entity`: Missing refresh token

### 🔐 **Password Reset Flow**

#### `POST /request-password-reset`
```python
@router.post("/request-password-reset", response_model=MessageResponse)
async def request_password_reset(
    data: PasswordResetRequest,
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    validate_email: Callable = Depends(get_validate_email),
) -> MessageResponse:
```

**Purpose:** Initiate password reset flow with email verification

**Reset Request Process:**
1. **Rate Limiting**: Prevent email flooding attacks
2. **Email Validation**: Validate email format
3. **User Lookup**: Check if email exists (silent for security)
4. **Token Generation**: Create secure reset token
5. **Email Dispatch**: Send reset link to user email
6. **Security Response**: Always return success message

**Security Features:**
- **Information Disclosure Prevention**: Always returns success
- **Token Expiration**: Time-limited reset tokens
- **Rate Limiting**: Prevents email bombing

#### `POST /reset-password`
```python
@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: PasswordResetConfirmRequest = Body(...),
    session: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    get_password_validation_error: Callable = Depends(get_password_validation_error),
) -> MessageResponse:
```

**Purpose:** Complete password reset using valid reset token

**Reset Completion Process:**
1. **Password Validation**: Ensure new password meets requirements
2. **Token Verification**: Validate reset token signature and expiration
3. **Password Update**: Hash and store new password
4. **Token Invalidation**: Mark reset token as used
5. **Audit Logging**: Log password change activity

### 👤 **User Profile**

#### `GET /me`
```python
@router.get("/me", response_model=UserProfile)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserProfile:
```

**Purpose:** Retrieve current authenticated user's profile information

**Profile Response:**
```json
{
  "id": 123,
  "email": "user@example.com",
  "name": "Jane Doe",
  "bio": "Software developer",
  "avatar_url": "https://example.com/avatar.jpg",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T12:30:00Z"
}
```

## Utility Functions

### 🛡️ **Rate Limiting System**

#### `check_rate_limit()`
```python
async def check_rate_limit(
    user_action_limiter: UserActionLimiterProtocol,
    limiter_key: str,
    log_extra: Mapping[str, object],
    action: str = "action",
) -> None:
```

**Purpose:** Centralized rate limiting logic for all endpoints

**Rate Limiting Strategy:**
- **Key-Based Limiting**: User ID, email, or IP-based keys
- **Action-Specific**: Different limits per action type
- **Graceful Handling**: Clear error messages for limit exceeded
- **Logging Integration**: Comprehensive rate limit logging

#### `rate_limit()` Decorator
```python
def rate_limit(action: str, key_func: Callable[[Request], str] | None = None) -> object:
```

**Purpose:** FastAPI dependency for flexible rate limiting

**Rate Limit Configurations:**
```python
# Registration: 5 attempts per email per hour
f"register:{data.email}"

# Login: 10 attempts per IP per minute  
f"login:{data.email}"

# Password Reset: 3 attempts per email per hour
f"pwreset:{data.email}"
```

### ⚙️ **Common Dependencies**

#### `common_auth_deps()`
```python
def common_auth_deps(feature: str) -> tuple[object, object, object]:
    return (
        Depends(get_request_id),
        Depends(require_feature(feature)),
        Depends(require_api_key),
    )
```

**Purpose:** Standardized dependency injection for auth endpoints

**Common Dependencies:**
- **Request ID**: For request tracing and correlation
- **Feature Flags**: Runtime feature control per endpoint
- **API Key**: Service-to-service authentication requirement

## Security Features

### 🔐 **Multi-Layer Authentication**

#### API Key Protection
```python
dependencies=[
    Depends(get_request_id),
    Depends(require_feature("auth:register")),
    Depends(require_api_key),  # Service-level protection
]
```

**Security Layers:**
1. **API Key Validation**: Service-to-service authentication
2. **Feature Flags**: Runtime endpoint control
3. **Rate Limiting**: Abuse prevention
4. **Input Validation**: Strong data validation
5. **JWT Security**: Cryptographic token protection

#### Password Security
```python
get_password_validation_error: Callable[[str], str | None] = Depends(
    get_password_validation_error,
)
```

**Password Requirements:**
- **Minimum Length**: 8 characters minimum
- **Complexity**: Configurable complexity requirements
- **Validation**: Real-time password strength validation
- **Hashing**: bcrypt with appropriate cost factor

### 🛡️ **Rate Limiting Matrix**

| Endpoint | Rate Limit | Key | Duration |
|----------|------------|-----|----------|
| `/register` | 5 attempts | Email | 1 hour |
| `/login` | 10 attempts | Email | 1 minute |
| `/request-password-reset` | 3 attempts | Email | 1 hour |
| `/logout` | 20 attempts | User ID | 1 minute |
| `/refresh-token` | 30 attempts | Token | 1 minute |

### 🔒 **Token Security**

#### JWT Token Structure
```python
payload = {
    "sub": user.id,          # Subject (user ID)
    "email": user.email,     # User email
    "role": user.role,       # User role
    "exp": expiration_time,  # Expiration timestamp
    "iat": issued_at_time,   # Issued at timestamp
    "jti": token_id,         # JWT ID for blacklisting
}
```

**Token Security Features:**
- **Cryptographic Signing**: HMAC-SHA256 signatures
- **Expiration Handling**: Time-based token invalidation
- **Blacklist Support**: Token revocation system
- **Role-Based Access**: User role encoding in tokens

## Error Handling

### 🛠️ **Comprehensive Error Management**

#### Authentication Errors
```python
try:
    access_token, refresh_token = await user_service.authenticate_user(
        session, data.email, data.password
    )
except UserNotFoundError as e:
    http_error(401, "Invalid credentials", logger.warning, {"email": data.email}, e)
except ValidationError as e:
    http_error(401, "Invalid credentials", logger.warning, {"email": data.email}, e)
```

**Error Response Pattern:**
- **Consistent Status Codes**: Standard HTTP status code usage
- **Security-Safe Messages**: No information disclosure
- **Comprehensive Logging**: Detailed server-side logging
- **Error Context**: Rich error context for debugging

#### Rate Limiting Errors
```python
http_error(
    429,
    f"Too many {action} attempts. Please try again later.",
    logger.warning,
    {"limiter_key": key}
)
```

#### Validation Errors
```python
if pw_error is not None:
    http_error(
        400, 
        pw_error, 
        logger.warning, 
        {"token_prefix": data.token[:8]}
    )
```

### 📊 **Error Code Reference**

| Status Code | Scenario | Endpoint | Description |
|-------------|----------|----------|-------------|
| `400` | Invalid input | All | Bad request data or validation failure |
| `401` | Auth failure | Login, Logout, Refresh | Invalid credentials or tokens |
| `409` | Conflict | Register | Email already exists |
| `422` | Validation | All | Input validation errors |
| `429` | Rate limit | All | Too many requests |
| `500` | Server error | All | Unexpected server errors |

## Usage Patterns

### 🔧 **Standard Authentication Flow**

```python
# 1. Register new user
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "Jane Doe"
}
Response: {"access_token": "...", "refresh_token": "..."}

# 2. Use access token for API requests
GET /api/v1/auth/me
Headers: {"Authorization": "Bearer <access_token>"}

# 3. Refresh token when expired
POST /api/v1/auth/refresh-token
{"token": "<refresh_token>"}
Response: {"access_token": "...", "refresh_token": "..."}

# 4. Logout to invalidate tokens
POST /api/v1/auth/logout
Headers: {"Authorization": "Bearer <access_token>"}
```

### 🔐 **Password Reset Flow**

```python
# 1. Request password reset
POST /api/v1/auth/request-password-reset
{"email": "user@example.com"}
Response: {"message": "Password reset link sent."}

# 2. User receives email with reset link
# 3. Complete password reset
POST /api/v1/auth/reset-password
{
  "token": "<reset_token_from_email>",
  "new_password": "NewSecurePass123!"
}
Response: {"message": "Password has been reset."}
```

### 🛡️ **Rate Limiting Handling**

```python
# Handle rate limiting in client code
try:
    response = await client.post("/api/v1/auth/login", json=credentials)
except HTTPException as e:
    if e.status_code == 429:
        # Rate limited - wait and retry
        await asyncio.sleep(60)  # Wait 1 minute
        response = await client.post("/api/v1/auth/login", json=credentials)
```

## Testing Strategies

### 🧪 **Unit Testing**

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_register_success():
    """Test successful user registration."""
    client = TestClient(app)
    
    with patch('src.api.v1.auth.get_user_service') as mock_service:
        mock_service.return_value.register_user = AsyncMock(return_value=mock_user)
        mock_service.return_value.authenticate_user = AsyncMock(
            return_value=("access_token", "refresh_token")
        )
        
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
        })
        
        assert response.status_code == 201
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    client = TestClient(app)
    
    with patch('src.api.v1.auth.get_user_service') as mock_service:
        mock_service.return_value.authenticate_user.side_effect = UserNotFoundError()
        
        response = client.post("/api/v1/auth/login", json={
            "email": "invalid@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert response.json()["message"] == "Invalid credentials"
```

### 🔄 **Integration Testing**

```python
@pytest.mark.asyncio
async def test_auth_flow_integration():
    """Test complete authentication flow."""
    client = TestClient(app)
    
    # Register user
    register_response = client.post("/api/v1/auth/register", json={
        "email": "integration@example.com",
        "password": "TestPass123!",
        "name": "Integration Test"
    })
    assert register_response.status_code == 201
    
    tokens = register_response.json()
    access_token = tokens["access_token"]
    
    # Get profile
    profile_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == "integration@example.com"
    
    # Logout
    logout_response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert logout_response.status_code == 200
```

### 🛡️ **Security Testing**

```python
def test_rate_limiting():
    """Test rate limiting enforcement."""
    client = TestClient(app)
    
    # Attempt login multiple times
    for _ in range(11):  # Exceed limit of 10
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
    
    # Last request should be rate limited
    assert response.status_code == 429
    assert "Too many" in response.json()["message"]

def test_token_blacklisting():
    """Test token blacklisting on logout."""
    client = TestClient(app)
    
    # Login and get token
    login_response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "correctpassword"
    })
    access_token = login_response.json()["access_token"]
    
    # Logout (blacklist token)
    client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # Try to use blacklisted token
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 401
```

## Performance Considerations

### ⚡ **Optimization Strategies**

#### Database Query Optimization
```python
# Efficient user lookup with single query
user = await user_service.get_user_by_email(session, email)
if not user or not user.is_active or user.is_deleted:
    raise UserNotFoundError()
```

#### Token Caching
```python
# Cache frequently accessed settings
settings = get_settings()  # Cached configuration
```

#### Rate Limiting Efficiency
```python
# Efficient rate limit key generation
user_id_or_host = str(getattr(user, "id", client_host))
key = f"{action}:{user_id_or_host}"
```

### 📊 **Performance Metrics**

- **Average Response Time**: < 100ms for authentication endpoints
- **Token Generation**: < 50ms for JWT creation
- **Rate Limit Checks**: < 10ms for limit validation
- **Database Queries**: Single query per authentication attempt

## Best Practices

### ✅ **Do's**

- **Use Strong Passwords**: Enforce password complexity requirements
- **Implement Rate Limiting**: Prevent brute force attacks
- **Log Security Events**: Comprehensive audit logging
- **Validate All Inputs**: Strong input validation and sanitization
- **Use HTTPS**: Always encrypt authentication traffic
- **Rotate Tokens**: Implement token rotation for refresh tokens
- **Handle Errors Gracefully**: Consistent error responses

### ❌ **Don'ts**

- **Don't Log Passwords**: Never log passwords or sensitive data
- **Don't Expose User Existence**: Use generic error messages
- **Don't Skip Rate Limiting**: Always implement abuse prevention
- **Don't Use Weak Tokens**: Use cryptographically secure token generation
- **Don't Ignore Token Expiration**: Always validate token expiration
- **Don't Mix Authentication Methods**: Keep authentication patterns consistent

## Related Files

- **`src/api/deps.py`** - Authentication dependencies and JWT validation
- **`src/services/user.py`** - User service layer with business logic
- **`src/models/user.py`** - User database model definitions
- **`src/schemas/auth.py`** - Authentication request/response schemas
- **`src/core/security.py`** - JWT token utilities and password hashing
- **`src/core/config.py`** - Authentication configuration settings

## Dependencies

- **`fastapi`** - Web framework and dependency injection
- **`jose`** - JWT token processing and validation
- **`loguru`** - Structured logging for security events
- **`sqlalchemy`** - Database ORM for user management
- **`bcrypt`** - Password hashing and verification

---

*This authentication router provides comprehensive, secure, and scalable authentication services for the ReViewPoint application, implementing industry best practices for user authentication, authorization, and security.*
