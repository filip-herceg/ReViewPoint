# api/v1/users/test_only_router.py - Test Environment User Utilities

## Purpose

The `api/v1/users/test_only_router.py` module provides test-specific user management endpoints that are only available in test environments. These utilities are designed for test automation, setup scenarios, and development workflows where privileged operations need to be performed without the normal security constraints.

## Key Components

### Core Imports and Test Environment Detection

#### Test-Specific Dependencies

```python
"""
Test-only endpoints for user management (e.g., promote to admin).
"""

from typing import Final

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.routing import APIRouter as APIRouterType
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import TypedDict

from src.core.database import get_async_session
from src.models.user import User
from src.utils.environment import is_test_mode

# Router instance is a constant and should not be mutated
router: Final[APIRouterType] = APIRouter()
```

#### Response Type Definitions

```python
class PromoteAdminResponse(TypedDict):
    detail: str
```

### Admin Promotion Endpoint

#### Test-Only Admin Role Assignment

```python
@router.post(
    "/promote-admin",
    summary="Promote user to admin (TEST ONLY)",
    description="""
    **🚨 TEST ENVIRONMENT ONLY - NOT AVAILABLE IN PRODUCTION 🚨**

    Promote a regular user to admin status by email address.
    This endpoint is restricted to test environments for testing admin functionality.

    **Requirements:**
    - Must be running in test mode (TEST_MODE=true)
    - User must exist in the database
    - No authentication required (test endpoint)

    **Request Body:**
    ```json
    {
        "email": "user@example.com"
    }
    ```

    **Behavior:**
    - Finds user by email address
    - Sets `is_admin` flag to `true`
    - Commits changes to database
    - Returns confirmation message

    **Example Request:**
    ```json
    {
        "email": "john.doe@example.com"
    }
    ```

    **Example Response:**
    ```json
    {
        "detail": "User john.doe@example.com promoted to admin."
    }
    ```

    **Security Notes:**
    - Automatically disabled in production environments
    - Returns 403 Forbidden if not in test mode
    - Use only for test setup and automation
    - Never expose in production APIs
    """,
    responses={
        200: {
            "description": "User promoted to admin successfully",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User john.doe@example.com promoted to admin."
                    }
                }
            },
        },
        403: {"description": "Not allowed in production environment"},
        404: {"description": "User not found"},
        422: {"description": "Invalid email format"},
        500: {"description": "Internal server error"},
    },
    tags=["Test Utilities"],
)
async def promote_user_to_admin_async(
    email: str = Body(..., embed=True, description="Email address of user to promote"),
    session: AsyncSession = Depends(get_async_session),
) -> PromoteAdminResponse:
    """
    Promote a user to admin status - TEST ENVIRONMENT ONLY.

    This endpoint is designed for test automation and setup.
    It's automatically disabled in production environments.
    """
    if not is_test_mode():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed in production."
        )
    user: Result[tuple[User]] = await session.execute(
        select(User).where(User.email == email)
    )
    user_obj: User | None = user.scalars().first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    user_obj.is_admin = True
    await session.commit()
    response: PromoteAdminResponse = {"detail": f"User {email} promoted to admin."}
    return response
```

## Security and Environment Controls

### Test Mode Verification

#### Production Environment Protection

```python
# Environment-based security control:

def enforce_test_mode_only():
    """Ensure endpoint only works in test environments."""
    if not is_test_mode():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not allowed in production."
        )

# Applied to all test-only endpoints:
if not is_test_mode():
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="Not allowed in production."
    )
```

### Direct Database Operations

#### Bypassing Normal Service Layer

```python
# Direct database operations for test scenarios:

# Query user directly by email
user: Result[tuple[User]] = await session.execute(
    select(User).where(User.email == email)
)
user_obj: User | None = user.scalars().first()

# Direct field modification
if user_obj:
    user_obj.is_admin = True
    await session.commit()
```

## Use Case Scenarios

### Test Automation Setup

```python
# Example usage in test automation:

import requests

# Setup admin user for tests
def setup_admin_user(email: str):
    response = requests.post(
        "http://localhost:8000/api/v1/users/promote-admin",
        json={"email": email},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print(f"User {email} promoted to admin successfully")
    elif response.status_code == 403:
        print("Test endpoint not available in production")
    elif response.status_code == 404:
        print(f"User {email} not found")
```

### Development Workflow Integration

```bash
# Example CLI usage for development setup:

# Create a test user and promote to admin
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "name": "Test Admin", "password": "testpass123"}'

curl -X POST http://localhost:8000/api/v1/users/promote-admin \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com"}'
```

### Integration Testing Scenarios

```python
# Integration test example:

async def test_admin_functionality():
    """Test admin-only features."""
    
    # Setup: Create regular user
    user_data = {
        "email": "testuser@example.com",
        "name": "Test User", 
        "password": "testpass123"
    }
    
    # Promote to admin using test endpoint
    promote_response = await client.post(
        "/api/v1/users/promote-admin",
        json={"email": "testuser@example.com"}
    )
    assert promote_response.status_code == 200
    
    # Test admin functionality
    admin_response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_response.status_code == 200
```

## Request/Response Patterns

### Promote Admin Request/Response

```json
// POST /api/v1/users/promote-admin
// Request:
{
    "email": "john.doe@example.com"
}

// Response (200 OK):
{
    "detail": "User john.doe@example.com promoted to admin."
}

// Response (403 Forbidden - Production):
{
    "detail": "Not allowed in production."
}

// Response (404 Not Found):
{
    "detail": "User not found."
}
```

## Integration Patterns

### Environment Detection Integration

```python
# Integration with environment utilities:

from src.utils.environment import is_test_mode

# Environment-based conditional execution
if is_test_mode():
    # Enable test-only endpoints
    app.include_router(test_router, prefix="/test")
else:
    # Test endpoints are not registered in production
    pass
```

### Database Session Integration

```python
# Direct database integration for test scenarios:

async def test_database_operation(
    session: AsyncSession = Depends(get_async_session)
):
    # Direct SQLAlchemy operations
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    # Direct field modification
    user.is_admin = True
    await session.commit()
```

## Best Practices

### Test Environment Security

- Always verify test mode before executing privileged operations
- Use clear warning indicators in API documentation
- Implement automatic disabling in production environments
- Log all test-only operations for audit purposes
- Never include test endpoints in production API documentation

### Development Workflow Automation

- Design test utilities for common development scenarios
- Provide clear examples for test automation integration
- Implement idempotent operations where possible
- Use descriptive response messages for debugging
- Consider rate limiting even for test endpoints

### Error Handling and User Experience

- Provide clear error messages for environment restrictions
- Handle user not found scenarios gracefully
- Return appropriate HTTP status codes
- Log test operations for debugging purposes
- Include helpful examples in API documentation

### Code Organization and Maintenance

- Separate test utilities from production code
- Use clear naming conventions for test-only endpoints
- Document security implications clearly
- Implement consistent error handling patterns
- Consider test data cleanup utilities

This test-only router provides essential development and testing utilities while maintaining strict security controls to prevent accidental exposure in production environments. It enables efficient test automation and development workflows without compromising production security.

## Related Files

- [`utils/environment.py.md`](../../utils/environment.py.md) - Environment detection utilities
- [`models/user.py.md`](../../models/user.py.md) - User data models
- [`core/database.py.md`](../../core/database.py.md) - Database session management
- [`api/v1/users/core.py.md`](core.py.md) - Production user management API
