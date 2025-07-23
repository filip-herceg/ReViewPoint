# User Management Core API

**File:** `backend/src/api/v1/users/core.py`  
**Purpose:** Complete CRUD operations for user management with admin controls and validation  
**Lines of Code:** 606  
**Type:** FastAPI Router Module  

## Overview

The User Management Core API provides comprehensive Create, Read, Update, Delete (CRUD) operations for user accounts in the ReViewPoint system. This module implements secure user management with admin-level access controls, comprehensive validation, feature flag protection, and detailed error handling. It serves as the administrative interface for user account lifecycle management with full audit trails and security measures.

## Architecture

### Core Design Principles

1. **Admin-Only Access**: All operations require admin privileges for security
2. **Feature Flag Protection**: Each endpoint protected by configurable feature flags
3. **Comprehensive Validation**: Input validation with detailed error responses
4. **Audit Logging**: Complete audit trail for all user operations
5. **Idempotent Operations**: Safe retry behavior for critical operations
6. **Error Handling**: Detailed error responses with security considerations

### User Management Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin User    │    │   Validation    │    │   User Service  │
│   Request       │────┤   & Security    │────┤   Layer         │
│                 │    │                 │    │                 │
│ • Authentication│    │ • Input Validate│    │ • Business Logic│
│ • Authorization │    │ • Feature Flags │    │ • Data Access   │
│ • Request Data  │    │ • Admin Check   │    │ • Error Handling│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │   Operations    │
                    │                 │
                    │ • User CRUD     │
                    │ • Transactions  │
                    │ • Constraints   │
                    │ • Audit Trail   │
                    └─────────────────┘
```

## API Endpoints

### 👤 **Create User**

#### `POST /api/v1/users`

**Purpose:** Create a new user account with validation and security checks

**Requirements:**
- Valid API key in Authorization header
- Feature flag `users:create` must be enabled
- Admin privileges required

**Request Schema:**
```python
class UserCreateRequest:
    email: str          # Valid email address (unique)
    password: str       # Secure password (minimum 8 characters)  
    name: str          # User's display name
```

**Example Request:**
```json
POST /api/v1/users
Authorization: Bearer your-api-key

{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
}
```

**Example Response (201 Created):**
```json
{
    "id": 123,
    "email": "newuser@example.com",
    "name": "John Doe",
    "bio": null,
    "avatar_url": null,
    "created_at": "2025-01-08T10:30:00Z",
    "updated_at": "2025-01-08T10:30:00Z"
}
```

**Implementation Details:**
```python
async def create_user(
    user: UserCreateRequest,
    session: AsyncSession,
    user_service: UserService,
) -> UserResponse:
    """Create new user with comprehensive validation."""
    
    try:
        # Register user through service layer
        db_user = await user_service.register_user(session, {
            "email": user.email,
            "password": user.password,
            "name": user.name,
        })
        
        # Log successful creation
        logger.info("user_created", extra={
            "user_id": db_user.id, 
            "email": db_user.email
        })
        
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name
        )
        
    except UserAlreadyExistsError:
        # Handle email conflicts with detailed logging
        raise HTTPException(409, "Email already exists.")
```

**Response Codes:**
- **201 Created**: User created successfully
- **400 Bad Request**: Invalid user data
- **401 Unauthorized**: Invalid API key
- **403 Forbidden**: Admin access required
- **409 Conflict**: Email already exists
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Unexpected error

### 📋 **List Users**

#### `GET /api/v1/users`

**Purpose:** Retrieve paginated list of users with comprehensive filtering

**Requirements:**
- Valid API key in Authorization header
- Feature flag `users:list` must be enabled
- Admin privileges required

**Query Parameters:**
```python
offset: int = 0                    # Records to skip (pagination)
limit: int = 50                    # Max records (max: 100)
email: str | None = None           # Filter by email (partial match)
name: str | None = None            # Filter by name (partial match)
created_after: str | None = None   # Filter by creation date (ISO format)
```

**Example Request:**
```
GET /api/v1/users?offset=0&limit=10&name=john&created_after=2025-01-01T00:00:00Z
Authorization: Bearer your-api-key
```

**Example Response (200 OK):**
```json
{
    "users": [
        {
            "id": 123,
            "email": "john.doe@example.com",
            "name": "John Doe",
            "bio": "Software developer",
            "avatar_url": "https://example.com/avatar.jpg",
            "created_at": "2025-01-08T10:30:00Z",
            "updated_at": "2025-01-08T10:30:00Z"
        }
    ],
    "total": 1
}
```

**Implementation Features:**
```python
async def list_users(
    params: PaginationParams,
    email: str | None,
    name: str | None,
    created_after: str | None,
    session: AsyncSession,
    user_service: UserService,
) -> UserListResponse:
    """List users with advanced filtering and pagination."""
    
    # Parse date filter if provided
    created_after_dt = None
    if created_after:
        created_after_dt = parse_flexible_datetime(created_after)
    
    # Query with filters
    users = await user_service.list_users(
        session,
        offset=params.offset,
        limit=params.limit,
        email=email,
        name=name,
        created_after=created_after_dt,
    )
    
    # Log operation
    logger.info("users_listed", extra={
        "offset": params.offset,
        "limit": params.limit,
        "filters": {"email": email, "name": name}
    })
    
    return UserListResponse(
        users=[UserResponse(**user.dict()) for user in users],
        total=len(users)
    )
```

**Filtering Capabilities:**
- **Email Filtering**: Partial email address matching
- **Name Filtering**: Partial name matching (case-insensitive)
- **Date Filtering**: Users created after specified date
- **Pagination**: Offset/limit with configurable max limit
- **Combined Filters**: Multiple filters can be applied together

### 🔍 **Get User by ID**

#### `GET /api/v1/users/{user_id}`

**Purpose:** Retrieve detailed information for a specific user

**Requirements:**
- Valid API key in Authorization header
- Feature flag `users:read` must be enabled
- Admin privileges required

**Path Parameters:**
```python
user_id: int    # User unique identifier (positive integer)
```

**Example Request:**
```
GET /api/v1/users/123
Authorization: Bearer your-api-key
```

**Example Response (200 OK):**
```json
{
    "id": 123,
    "email": "john.doe@example.com",
    "name": "John Doe",
    "bio": "Software developer passionate about clean code",
    "avatar_url": "https://example.com/avatars/123.jpg",
    "created_at": "2025-01-08T10:30:00Z",
    "updated_at": "2025-01-08T15:45:00Z"
}
```

**Implementation:**
```python
async def get_user_by_id(
    user_id: int,
    session: AsyncSession,
    user_service: UserService,
) -> UserResponse:
    """Get user by ID with comprehensive error handling."""
    
    try:
        user = await user_service.get_user_by_id(session, user_id)
        if not user:
            raise HTTPException(404, "User not found")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_user_by_id: {e}")
        raise HTTPException(500, "Unexpected error.")
```

**Response Codes:**
- **200 OK**: User retrieved successfully
- **401 Unauthorized**: Invalid API key
- **403 Forbidden**: Admin access required
- **404 Not Found**: User not found
- **500 Internal Server Error**: Unexpected error

### ✏️ **Update User**

#### `PUT /api/v1/users/{user_id}`

**Purpose:** Update existing user information with validation

**Requirements:**
- Valid API key in Authorization header
- Admin privileges required

**Path Parameters:**
```python
user_id: int    # User ID to update (positive integer)
```

**Request Schema:**
```python
class UserCreateRequest:
    email: str          # New email address (must be unique)
    password: str       # New password (will be hashed)
    name: str          # Updated display name
```

**Example Request:**
```json
PUT /api/v1/users/123
Authorization: Bearer your-api-key

{
    "email": "updated@example.com",
    "password": "NewSecurePass123!",
    "name": "Updated Name"
}
```

**Example Response (200 OK):**
```json
{
    "id": 123,
    "email": "updated@example.com", 
    "name": "Updated Name",
    "bio": null,
    "avatar_url": null,
    "created_at": "2025-01-08T10:30:00Z",
    "updated_at": "2025-01-08T16:20:00Z"
}
```

**Implementation:**
```python
async def update_user(
    user_id: int,
    user: UserCreateRequest,
    session: AsyncSession,
    user_service: UserService,
) -> UserResponse:
    """Update user with comprehensive validation."""
    
    try:
        updated_user = await user_service.update_user(
            session, user_id, user.model_dump()
        )
        
        logger.info("user_updated", extra={"user_id": user_id})
        
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            name=updated_user.name
        )
        
    except UserNotFoundError:
        raise HTTPException(404, "User not found.")
    except UserAlreadyExistsError:
        raise HTTPException(409, "Email already exists.")
    except InvalidDataError:
        raise HTTPException(400, "Invalid user data.")
```

**Validation Features:**
- **Email Uniqueness**: Ensures email isn't already taken
- **Password Security**: Automatic secure hashing
- **Data Validation**: Input format and constraint validation
- **Atomic Updates**: Database transaction safety
- **Conflict Resolution**: Handles concurrent update scenarios

### 🗑️ **Delete User**

#### `DELETE /api/v1/users/{user_id}`

**Purpose:** Permanently delete a user account from the system

**Requirements:**
- Valid API key in Authorization header
- Admin privileges required

**Path Parameters:**
```python
user_id: int    # User ID to delete (positive integer)
```

**Example Request:**
```
DELETE /api/v1/users/123
Authorization: Bearer your-api-key
```

**Example Response (204 No Content):**
```
HTTP/1.1 204 No Content
```

**Implementation:**
```python
async def delete_user(
    user_id: int,
    session: AsyncSession,
    user_service: UserService,
) -> Response:
    """Delete user with proper cleanup."""
    
    try:
        await user_service.delete_user(session, user_id)
        logger.info("user_deleted", extra={"user_id": user_id})
        return Response(status_code=204)
        
    except UserNotFoundError:
        logger.warning("User not found.", extra={"user_id": user_id})
        return Response(status_code=404, content="User not found.")
    except Exception as e:
        logger.error("Unexpected error.", extra={
            "user_id": user_id, 
            "error": str(e)
        })
        return Response(status_code=500, content="Unexpected error.")
```

**Deletion Behavior:**
- **Permanent Removal**: User is permanently deleted from database
- **Cascade Operations**: Related records are handled according to constraints
- **Audit Trail**: Deletion is logged for compliance
- **Irreversible**: Operation cannot be undone
- **Clean Response**: Returns 204 No Content on success

## Security Features

### 🔐 **Authentication & Authorization**

#### API Key Authentication
```python
dependencies=[
    Depends(require_api_key),      # Validates API key
    Depends(require_admin),        # Requires admin privileges
]
```

#### Feature Flag Protection
```python
dependencies=[
    Depends(require_feature("users:create")),  # Feature must be enabled
    Depends(require_feature("users:list")),    # Per-operation flags
    Depends(require_feature("users:read")),    # Granular control
]
```

### 🛡️ **Input Validation**

#### Request Validation
```python
class UserCreateRequest(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX)
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)
```

#### Path Parameter Validation
```python
user_id: int = Path(..., description="User ID", gt=0)
```

## Error Handling

### 🚨 **Comprehensive Error Responses**

#### User Creation Errors
```python
try:
    db_user = await user_service.register_user(session, user_data)
except UserAlreadyExistsError:
    raise HTTPException(409, "Email already exists.")
except InvalidDataError:
    raise HTTPException(400, "Invalid user data.")
except CustomValidationError as e:
    raise HTTPException(422, str(e))
except Exception as e:
    logger.error(f"Unexpected error in create_user: {e}")
    raise HTTPException(500, "Unexpected error.")
```

#### Error Response Format
```json
{
    "detail": "Email already exists.",
    "status_code": 409,
    "timestamp": "2025-01-08T10:30:00Z"
}
```

### 📝 **Audit Logging**

#### Operation Logging
```python
# Successful operations
logger.info("user_created", extra={
    "user_id": db_user.id,
    "email": db_user.email,
    "operator": current_user.id
})

# Warning conditions
logger.warning("User not found.", extra={
    "user_id": user_id,
    "operation": "delete"
})

# Error conditions
logger.error("Unexpected error.", extra={
    "user_id": user_id,
    "error": str(e),
    "stack_trace": traceback.format_exc()
})
```

## Usage Patterns

### 📊 **Administrative Operations**

#### Complete User Management Workflow
```python
# 1. Create a new user
user_data = {
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
}

response = await client.post(
    "/api/v1/users",
    json=user_data,
    headers={"Authorization": f"Bearer {api_key}"}
)
new_user = response.json()

# 2. List users with filtering
response = await client.get(
    "/api/v1/users?name=john&limit=10",
    headers={"Authorization": f"Bearer {api_key}"}
)
users_list = response.json()

# 3. Get specific user details
user_id = new_user["id"]
response = await client.get(
    f"/api/v1/users/{user_id}",
    headers={"Authorization": f"Bearer {api_key}"}
)
user_details = response.json()

# 4. Update user information
update_data = {
    "email": "updated@example.com",
    "password": "NewPassword123!",
    "name": "Updated Name"
}

response = await client.put(
    f"/api/v1/users/{user_id}",
    json=update_data,
    headers={"Authorization": f"Bearer {api_key}"}
)
updated_user = response.json()

# 5. Delete user (when necessary)
response = await client.delete(
    f"/api/v1/users/{user_id}",
    headers={"Authorization": f"Bearer {api_key}"}
)
# Returns 204 No Content on success
```

### 🔍 **Advanced Filtering Examples**

```python
# Filter by email pattern
response = await client.get(
    "/api/v1/users?email=@company.com",
    headers={"Authorization": f"Bearer {api_key}"}
)

# Filter by name and date range
response = await client.get(
    "/api/v1/users?name=admin&created_after=2025-01-01T00:00:00Z",
    headers={"Authorization": f"Bearer {api_key}"}
)

# Pagination with large datasets
response = await client.get(
    "/api/v1/users?offset=100&limit=50",
    headers={"Authorization": f"Bearer {api_key}"}
)
```

## Testing Strategies

### 🧪 **Unit Testing**

```python
import pytest
from fastapi.testclient import TestClient

class TestUserManagement:
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, client, admin_api_key):
        """Test successful user creation."""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
        }
        
        response = client.post(
            "/api/v1/users",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_api_key}"}
        )
        
        assert response.status_code == 201
        user = response.json()
        assert user["email"] == user_data["email"]
        assert user["name"] == user_data["name"]
        assert "id" in user
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, client, admin_api_key):
        """Test email uniqueness validation."""
        user_data = {
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "name": "User One"
        }
        
        # Create first user
        response1 = client.post(
            "/api/v1/users",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_api_key}"}
        )
        assert response1.status_code == 201
        
        # Attempt to create duplicate
        response2 = client.post(
            "/api/v1/users",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_api_key}"}
        )
        assert response2.status_code == 409
        assert "Email already exists" in response2.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_list_users_pagination(self, client, admin_api_key):
        """Test user listing with pagination."""
        response = client.get(
            "/api/v1/users?offset=0&limit=5",
            headers={"Authorization": f"Bearer {admin_api_key}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert len(data["users"]) <= 5
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client, admin_api_key):
        """Test handling of non-existent user."""
        response = client.get(
            "/api/v1/users/99999",
            headers={"Authorization": f"Bearer {admin_api_key}"}
        )
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
```

### 🔄 **Integration Testing**

```python
@pytest.mark.asyncio
async def test_complete_user_lifecycle(client, admin_api_key):
    """Test complete user management lifecycle."""
    
    # 1. Create user
    user_data = {
        "email": "lifecycle@example.com",
        "password": "SecurePass123!",
        "name": "Lifecycle User"
    }
    
    create_response = client.post(
        "/api/v1/users",
        json=user_data,
        headers={"Authorization": f"Bearer {admin_api_key}"}
    )
    assert create_response.status_code == 201
    user = create_response.json()
    user_id = user["id"]
    
    # 2. Retrieve user
    get_response = client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_api_key}"}
    )
    assert get_response.status_code == 200
    retrieved_user = get_response.json()
    assert retrieved_user["email"] == user_data["email"]
    
    # 3. Update user
    update_data = {
        "email": "updated@example.com",
        "password": "NewPassword123!",
        "name": "Updated User"
    }
    
    update_response = client.put(
        f"/api/v1/users/{user_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_api_key}"}
    )
    assert update_response.status_code == 200
    updated_user = update_response.json()
    assert updated_user["email"] == update_data["email"]
    
    # 4. Delete user
    delete_response = client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_api_key}"}
    )
    assert delete_response.status_code == 204
    
    # 5. Verify deletion
    verify_response = client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_api_key}"}
    )
    assert verify_response.status_code == 404
```

## Best Practices

### ✅ **Do's**

- **Use Feature Flags**: Protect all endpoints with appropriate feature flags
- **Validate Input**: Comprehensive input validation and sanitization
- **Log Operations**: Complete audit trail for all user operations
- **Handle Errors**: Detailed error handling with appropriate HTTP codes
- **Secure Passwords**: Always hash passwords before storage
- **Check Permissions**: Verify admin privileges for all operations
- **Pagination**: Use pagination for list operations to prevent resource exhaustion
- **Atomic Operations**: Use database transactions for data consistency

### ❌ **Don'ts**

- **Don't Expose Passwords**: Never return password hashes in responses
- **Don't Skip Validation**: Always validate email format and uniqueness
- **Don't Ignore Errors**: Handle all exception scenarios gracefully
- **Don't Allow Self-Deletion**: Prevent admins from deleting themselves
- **Don't Skip Logging**: Log all administrative operations for audit
- **Don't Hard-Code Limits**: Use configurable pagination limits
- **Don't Trust Client Data**: Validate all client input server-side

## Related Files

- **`src/services/user.py`** - User business logic and data operations
- **`src/schemas/user.py`** - User request/response schemas and validation
- **`src/models/user.py`** - User database model definition
- **`src/api/deps.py`** - Authentication and authorization dependencies
- **`src/repositories/user.py`** - User data access layer

## Dependencies

- **`fastapi`** - Web framework and routing
- **`sqlalchemy`** - Database ORM and session management
- **`loguru`** - Structured logging for audit trails
- **`pydantic`** - Data validation and serialization

---

*This User Management Core API provides comprehensive, secure, and auditable user account management capabilities with admin-level controls and enterprise-grade validation.*
