# backend/src/api/v1/users/core.py - User API Endpoints

## Purpose

The `users/core.py` module implements the FastAPI REST endpoints for user management operations. This module provides a comprehensive API for user registration, authentication, profile management, administrative operations, and user statistics, following RESTful principles and modern API design patterns.

## Key Components

### Router Configuration

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)],  # Global auth requirement
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"}
    }
)

# Security scheme for API documentation
security = HTTPBearer()
```

### User Registration and Profile Management

#### User Registration Endpoint

```python
@router.post(
    "/register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email verification",
    dependencies=[]  # Override global auth for public registration
)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(get_user_service),
    rate_limiter: RateLimiter = Depends(get_rate_limiter("registration", 5, 3600))
) -> User:
    """
    Register a new user account.
    
    This endpoint allows public registration of new users with:
    - Email validation and uniqueness checking
    - Password strength validation
    - Optional email verification
    - Rate limiting to prevent abuse
    
    Args:
        user_data: User registration information
        background_tasks: For sending verification emails
        user_service: User business logic service
        rate_limiter: Rate limiting dependency
        
    Returns:
        Created user information (without sensitive data)
        
    Raises:
        HTTPException: 400 if email already exists
        HTTPException: 422 if validation fails
        HTTPException: 429 if rate limit exceeded
    """
    try:
        # Check if user already exists
        existing_user = await user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        new_user = await user_service.create_user(user_data)
        
        # Send verification email in background
        if get_setting("SEND_VERIFICATION_EMAILS", True):
            background_tasks.add_task(
                send_verification_email,
                email=new_user.email,
                user_id=new_user.id
            )
        
        logger.info(f"New user registered: {new_user.email}")
        return new_user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )
```

#### Get Current User Profile

```python
@router.get(
    "/me",
    response_model=UserWithStats,
    summary="Get current user profile",
    description="Retrieve current user's profile with statistics"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> UserWithStats:
    """
    Get current user's profile information with statistics.
    
    Returns comprehensive user information including:
    - Basic profile data
    - File upload statistics
    - Account activity metrics
    - Computed fields for analytics
    
    Args:
        current_user: Current authenticated user
        user_service: User business logic service
        
    Returns:
        User profile with statistics
    """
    try:
        user_with_stats = await user_service.get_user_with_stats(current_user.id)
        return user_with_stats
        
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve user profile"
        )
```

#### Update User Profile

```python
@router.patch(
    "/me",
    response_model=User,
    summary="Update current user profile",
    description="Update current user's profile information"
)
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Update current user's profile information.
    
    Allows users to update their own profile data including:
    - Full name
    - Email address (with verification)
    - Other non-sensitive profile fields
    
    Note: Role and admin fields cannot be self-updated
    
    Args:
        update_data: Fields to update
        current_user: Current authenticated user
        user_service: User business logic service
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: 400 if email already in use
        HTTPException: 422 if validation fails
    """
    try:
        # Prevent self-role modification
        if hasattr(update_data, 'role') and update_data.role is not None:
            if not current_user.is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot modify your own role"
                )
        
        updated_user = await user_service.update_user(current_user.id, update_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User profile updated: {current_user.email}")
        return updated_user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )
```

### Password Management

#### Change Password

```python
@router.post(
    "/me/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change user password",
    description="Change current user's password with verification"
)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    rate_limiter: RateLimiter = Depends(get_rate_limiter("password_change", 3, 3600))
) -> Dict[str, str]:
    """
    Change current user's password.
    
    Requires:
    - Current password verification
    - New password strength validation
    - Password confirmation matching
    - Rate limiting to prevent brute force
    
    Args:
        password_data: Password change information
        current_user: Current authenticated user
        user_service: User business logic service
        rate_limiter: Rate limiting dependency
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 400 if current password incorrect
        HTTPException: 422 if validation fails
        HTTPException: 429 if rate limit exceeded
    """
    try:
        # Verify current password
        is_valid = await user_service.verify_password(
            current_user.id,
            password_data.current_password
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Change password
        await user_service.change_password(
            current_user.id,
            password_data.new_password
        )
        
        # Invalidate all existing tokens
        await user_service.invalidate_all_tokens(current_user.id)
        
        logger.info(f"Password changed for user: {current_user.email}")
        return {"message": "Password changed successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )
```

#### Request Password Reset

```python
@router.post(
    "/reset-password/request",
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Request password reset email",
    dependencies=[]  # Public endpoint
)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(get_user_service),
    rate_limiter: RateLimiter = Depends(get_rate_limiter("password_reset", 3, 3600))
) -> Dict[str, str]:
    """
    Request password reset email.
    
    Always returns success for security reasons, even if email doesn't exist.
    This prevents email enumeration attacks.
    
    Args:
        reset_request: Password reset request data
        background_tasks: For sending reset emails
        user_service: User business logic service
        rate_limiter: Rate limiting dependency
        
    Returns:
        Success message (always, for security)
    """
    try:
        # Always return success, send email only if user exists
        user = await user_service.get_user_by_email(reset_request.email)
        
        if user and user.is_active:
            # Generate reset token
            reset_token = await user_service.generate_password_reset_token(user.id)
            
            # Send reset email in background
            background_tasks.add_task(
                send_password_reset_email,
                email=user.email,
                reset_token=reset_token,
                user_name=user.full_name
            )
            
            logger.info(f"Password reset requested for: {user.email}")
        
        # Always return same response for security
        return {
            "message": "If the email exists, a password reset link has been sent"
        }
        
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        # Still return success to prevent information disclosure
        return {
            "message": "If the email exists, a password reset link has been sent"
        }
```

### Administrative Operations

#### List Users (Admin Only)

```python
@router.get(
    "/",
    response_model=UserList,
    summary="List users",
    description="Get paginated list of users (admin only)",
    dependencies=[Depends(require_admin)]
)
async def list_users(
    search_params: UserSearch = Depends(),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> UserList:
    """
    Get paginated list of users with search and filtering.
    
    Admin-only endpoint that provides:
    - Full user list with pagination
    - Search by name or email
    - Filter by role and status
    - Sort by various fields
    
    Args:
        search_params: Search and pagination parameters
        current_user: Current authenticated admin user
        user_service: User business logic service
        
    Returns:
        Paginated list of users
        
    Raises:
        HTTPException: 403 if not admin
    """
    try:
        users_result = await user_service.search_users(
            query=search_params.query,
            role=search_params.role,
            is_active=search_params.is_active,
            created_after=search_params.created_after,
            created_before=search_params.created_before,
            page=search_params.page,
            size=search_params.size,
            sort_by=search_params.sort_by,
            sort_order=search_params.sort_order
        )
        
        return users_result
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve users"
        )
```

#### Get User by ID (Admin Only)

```python
@router.get(
    "/{user_id}",
    response_model=UserWithStats,
    summary="Get user by ID",
    description="Get specific user information (admin only)",
    dependencies=[Depends(require_admin)]
)
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> UserWithStats:
    """
    Get specific user by ID with statistics.
    
    Admin-only endpoint for retrieving detailed user information
    including statistics and activity data.
    
    Args:
        user_id: User UUID identifier
        current_user: Current authenticated admin user
        user_service: User business logic service
        
    Returns:
        User information with statistics
        
    Raises:
        HTTPException: 403 if not admin
        HTTPException: 404 if user not found
    """
    try:
        user = await user_service.get_user_with_stats(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve user"
        )
```

#### Update User (Admin Only)

```python
@router.patch(
    "/{user_id}",
    response_model=User,
    summary="Update user",
    description="Update user information (admin only)",
    dependencies=[Depends(require_admin)]
)
async def update_user(
    user_id: UUID,
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Update user information (admin only).
    
    Allows admins to update any user's information including:
    - Profile information
    - Role assignments
    - Account status
    - Administrative flags
    
    Args:
        user_id: User UUID identifier
        update_data: Fields to update
        current_user: Current authenticated admin user
        user_service: User business logic service
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: 403 if not admin
        HTTPException: 404 if user not found
        HTTPException: 400 if validation fails
    """
    try:
        # Prevent self-demotion from admin
        if user_id == current_user.id and update_data.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote yourself from admin role"
            )
        
        updated_user = await user_service.update_user(user_id, update_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User {user_id} updated by admin {current_user.email}")
        return updated_user
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User update failed"
        )
```

### Bulk Operations

#### Bulk User Operations (Admin Only)

```python
@router.post(
    "/bulk",
    response_model=UserBulkResult,
    summary="Bulk user operations",
    description="Perform bulk operations on multiple users (admin only)",
    dependencies=[Depends(require_admin)]
)
async def bulk_user_operations(
    bulk_operation: UserBulkOperation,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> UserBulkResult:
    """
    Perform bulk operations on multiple users.
    
    Supported operations:
    - activate: Activate user accounts
    - deactivate: Deactivate user accounts
    - delete: Soft delete user accounts
    - update_role: Update user roles
    
    Args:
        bulk_operation: Bulk operation parameters
        current_user: Current authenticated admin user
        user_service: User business logic service
        
    Returns:
        Results of bulk operation
        
    Raises:
        HTTPException: 403 if not admin
        HTTPException: 400 if invalid operation
    """
    try:
        # Prevent self-modification in bulk operations
        if current_user.id in bulk_operation.user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot include yourself in bulk operations"
            )
        
        result = await user_service.bulk_user_operation(
            user_ids=bulk_operation.user_ids,
            operation=bulk_operation.operation,
            data=bulk_operation.data
        )
        
        logger.info(
            f"Bulk operation {bulk_operation.operation} performed by "
            f"{current_user.email} on {len(bulk_operation.user_ids)} users"
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Bulk operation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bulk operation failed"
        )
```

### Statistics and Analytics

#### User Statistics (Admin Only)

```python
@router.get(
    "/stats",
    response_model=UserStatistics,
    summary="Get user statistics",
    description="Get comprehensive user statistics (admin only)",
    dependencies=[Depends(require_admin)]
)
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> UserStatistics:
    """
    Get comprehensive user statistics and analytics.
    
    Provides admin dashboard data including:
    - Total user counts
    - User distribution by role
    - Activity metrics
    - Registration trends
    
    Args:
        current_user: Current authenticated admin user
        user_service: User business logic service
        
    Returns:
        User statistics and analytics data
    """
    try:
        stats = await user_service.get_user_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error retrieving user statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve user statistics"
        )
```

### User Deactivation and Deletion

#### Deactivate Account

```python
@router.delete(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Deactivate current user account",
    description="Deactivate current user's account (soft delete)"
)
async def deactivate_current_user(
    confirmation: Dict[str, bool],
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> Dict[str, str]:
    """
    Deactivate current user's account.
    
    Performs soft delete by marking account as inactive.
    Requires explicit confirmation to prevent accidental deletion.
    
    Args:
        confirmation: Must contain {"confirm": true}
        current_user: Current authenticated user
        user_service: User business logic service
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 400 if confirmation not provided
    """
    try:
        # Require explicit confirmation
        if not confirmation.get("confirm"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account deactivation requires confirmation"
            )
        
        # Prevent admin self-deletion if they're the only admin
        if current_user.role == UserRole.ADMIN:
            admin_count = await user_service.count_users_by_role(UserRole.ADMIN)
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot deactivate the only admin account"
                )
        
        await user_service.deactivate_user(current_user.id)
        
        # Invalidate all tokens
        await user_service.invalidate_all_tokens(current_user.id)
        
        logger.info(f"User account deactivated: {current_user.email}")
        return {"message": "Account deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Account deactivation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deactivation failed"
        )
```

## Dependencies

### Core Dependencies

```python
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from fastapi.security import HTTPBearer
from typing import Dict, List, Any
from uuid import UUID
import logging

# Internal Dependencies
from src.schemas.user import (
    User, UserCreate, UserUpdate, UserWithStats, UserList,
    UserSearch, PasswordChange, PasswordResetRequest, 
    UserBulkOperation, UserBulkResult, UserStatistics
)
from src.services.user import UserService
from src.api.deps import (
    get_current_user, get_user_service, require_admin,
    get_rate_limiter
)
from src.core.config import get_setting
from src.utils.email import send_verification_email, send_password_reset_email
from src.models.user import UserRole
```

### Security Dependencies

- **HTTPBearer**: JWT token authentication
- **get_current_user**: Current user extraction from JWT
- **require_admin**: Admin role verification
- **RateLimiter**: Rate limiting for sensitive operations

## Error Handling

### Comprehensive Error Responses

```python
# Standard error response format
{
    "detail": "Error message",
    "error_code": "USER_NOT_FOUND",
    "timestamp": "2024-01-22T10:30:00Z",
    "path": "/api/v1/users/123e4567-e89b-12d3-a456-426614174000"
}

# Validation error response
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

### Rate Limiting Responses

```python
# Rate limit exceeded
{
    "detail": "Too many requests",
    "retry_after": 3600,
    "limit": 5,
    "window": 3600
}
```

## Usage Examples

### User Registration

```bash
# Register new user
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "full_name": "John Doe",
    "password": "SecurePass123!",
    "role": "user"
  }'
```

### Authentication Required Operations

```bash
# Get current user profile
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Update profile
curl -X PATCH "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Smith"
  }'
```

### Admin Operations

```bash
# List users (admin only)
curl -X GET "http://localhost:8000/api/v1/users/?page=1&size=50&role=user" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"

# Bulk deactivate users
curl -X POST "http://localhost:8000/api/v1/users/bulk" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": ["123e4567-e89b-12d3-a456-426614174000"],
    "operation": "deactivate"
  }'
```

## Testing

### Unit Test Examples

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_register_user_success(client: TestClient):
    """Test successful user registration."""
    user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "SecurePass123!",
        "role": "user"
    }
    
    response = client.post("/api/v1/users/register", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_current_user_profile(client: TestClient, auth_headers):
    """Test retrieving current user profile."""
    response = client.get("/api/v1/users/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "full_name" in data
    assert "file_count" in data

@pytest.mark.asyncio
async def test_admin_required_endpoints(client: TestClient, user_headers):
    """Test admin-only endpoints reject regular users."""
    response = client.get("/api/v1/users/", headers=user_headers)
    
    assert response.status_code == 403
    assert "admin" in response.json()["detail"].lower()
```

### Integration Test Examples

```python
@pytest.mark.asyncio
async def test_user_registration_workflow(client: TestClient):
    """Test complete user registration workflow."""
    # Register user
    user_data = {
        "email": "workflow@example.com",
        "full_name": "Workflow Test",
        "password": "SecurePass123!"
    }
    
    register_response = client.post("/api/v1/users/register", json=user_data)
    assert register_response.status_code == 201
    
    # Login to get token
    login_response = client.post("/api/v1/auth/login", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get profile
    profile_response = client.get("/api/v1/users/me", headers=headers)
    assert profile_response.status_code == 200
    
    profile_data = profile_response.json()
    assert profile_data["email"] == user_data["email"]
```

## Related Files

- [User Service](../../../services/user.py.md) - Business logic for user operations
- [User Repository](../../../repositories/user.py.md) - Data access layer
- [User Schemas](../../../schemas/user.py.md) - Pydantic schemas for validation
- [User Model](../../../models/user.py.md) - SQLAlchemy user model
- [Authentication API](../auth.py.md) - Login and token management endpoints
- [API Dependencies](../../deps.py.md) - Shared API dependencies and utilities
- [Security Utils](../../../core/security.py.md) - JWT and password utilities

## Security Considerations

- All sensitive operations require authentication
- Admin operations require explicit admin role verification
- Rate limiting prevents abuse of registration and password operations
- Password reset uses secure token-based flow
- Self-modification restrictions prevent privilege escalation
- Bulk operations exclude the current user for safety
- Email enumeration attacks are prevented in password reset
- All passwords are securely hashed before storage
- JWT tokens are properly validated and can be invalidated
