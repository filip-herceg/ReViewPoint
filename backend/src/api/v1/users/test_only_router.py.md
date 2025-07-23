# User Test Utilities API

**File:** `backend/src/api/v1/users/test_only_router.py`  
**Purpose:** Test-only endpoints for user management (admin promotion) restricted to test environments  
**Lines of Code:** 117  
**Type:** FastAPI Router Module  

## Overview

The User Test Utilities API provides specialized endpoints designed exclusively for test environments to facilitate automated testing and development workflows. This module contains administrative utilities that are automatically disabled in production environments for security. The primary functionality includes promoting regular users to admin status for testing admin-restricted features and workflows.

## Architecture

### Core Design Principles

1. **Test Environment Only**: Automatically disabled in production environments
2. **Security First**: Environment-based restrictions prevent production misuse
3. **Testing Support**: Facilitates automated test setup and teardown
4. **Simple Operations**: Minimal, focused functionality for test scenarios
5. **Error Handling**: Comprehensive error responses for development debugging

### Test Environment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Test Runner   │    │   Environment   │    │   Database      │
│   Request       │────┤   Validation    │────┤   Operations    │
│                 │    │                 │    │                 │
│ • Admin Setup   │    │ • Test Mode     │    │ • User Update   │
│ • Test Data     │    │ • Security Check│    │ • Role Change   │
│ • Automation    │    │ • Production    │    │ • Commit        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Error         │
                    │   Handling      │
                    │                 │
                    │ • 403 Forbidden │
                    │ • 404 Not Found │
                    │ • 422 Validation│
                    │ • 500 Server    │
                    └─────────────────┘
```

## API Endpoints

### 👑 **Promote User to Admin**

#### `POST /api/v1/users/promote-admin`

**Purpose:** Promote a regular user to admin status (TEST ENVIRONMENT ONLY)

**Environment Restrictions:**
- **Test Mode Required**: Must be running with `TEST_MODE=true`
- **Production Blocked**: Automatically returns 403 Forbidden in production
- **No Authentication**: Test endpoint doesn't require authentication

**Request Schema:**
```python
{
    "email": str    # Email address of user to promote (embedded in body)
}
```

**Response Schema:**
```python
class PromoteAdminResponse(TypedDict):
    detail: str     # Confirmation message with email
```

**Example Request:**
```json
POST /api/v1/users/promote-admin

{
    "email": "john.doe@example.com"
}
```

**Example Response (200 OK):**
```json
{
    "detail": "User john.doe@example.com promoted to admin."
}
```

**Implementation:**
```python
async def promote_user_to_admin_async(
    email: str,
    session: AsyncSession,
) -> PromoteAdminResponse:
    """Promote user to admin status - TEST ENVIRONMENT ONLY."""
    
    # Security: Check test mode first
    if not is_test_mode():
        raise HTTPException(
            status_code=403,
            detail="Not allowed in production."
        )
    
    # Find user by email
    user_query = await session.execute(
        select(User).where(User.email == email)
    )
    user_obj = user_query.scalars().first()
    
    if not user_obj:
        raise HTTPException(404, "User not found.")
    
    # Promote to admin
    user_obj.is_admin = True
    await session.commit()
    
    return {"detail": f"User {email} promoted to admin."}
```

**Security Features:**
```python
# Environment validation
if not is_test_mode():
    raise HTTPException(403, "Not allowed in production.")

# Production environment detection
def is_test_mode() -> bool:
    """Check if running in test environment."""
    return os.getenv("TEST_MODE", "false").lower() == "true"
```

**Response Codes:**
- **200 OK**: User promoted successfully
- **403 Forbidden**: Not allowed in production environment
- **404 Not Found**: User not found
- **422 Unprocessable Entity**: Invalid email format
- **500 Internal Server Error**: Database or unexpected error

## Environment Management

### 🔒 **Production Protection**

#### Environment Detection
```python
from src.utils.environment import is_test_mode

# Automatic production protection
if not is_test_mode():
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not allowed in production."
    )
```

#### Test Mode Configuration
```bash
# Environment variable configuration
TEST_MODE=true          # Enables test endpoints
TEST_MODE=false         # Disables test endpoints (production)
```

#### Security Validation
```python
# Multiple layers of protection
1. Environment variable check (TEST_MODE)
2. HTTP 403 Forbidden in production
3. No authentication bypass in production
4. Automatic endpoint disabling
```

### 🧪 **Test Environment Features**

#### User Promotion Workflow
```python
# Test setup workflow
1. Create test user with regular privileges
2. Use promote-admin endpoint for elevation
3. Test admin-restricted functionality
4. Clean up test data after tests
```

#### Database Operations
```python
# Direct database manipulation for testing
user_obj.is_admin = True
await session.commit()

# Immediate effect on user privileges
# No caching or delay considerations
```

## Usage Patterns

### 🔧 **Test Automation**

#### Pytest Integration
```python
import pytest
import requests

class TestAdminFunctionality:
    
    @pytest.fixture
    async def admin_user(self, test_client, regular_user_email):
        """Fixture to create admin user for testing."""
        
        # Promote regular user to admin
        response = test_client.post(
            "/api/v1/users/promote-admin",
            json={"email": regular_user_email}
        )
        
        assert response.status_code == 200
        assert "promoted to admin" in response.json()["detail"]
        
        return regular_user_email
    
    async def test_admin_required_endpoint(self, test_client, admin_user):
        """Test endpoint that requires admin privileges."""
        
        # Get authentication token for admin user
        auth_response = test_client.post("/api/v1/auth/login", json={
            "email": admin_user,
            "password": "test_password"
        })
        token = auth_response.json()["access_token"]
        
        # Test admin-only endpoint
        response = test_client.get(
            "/api/v1/admin/sensitive-data",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
```

#### Test Setup and Teardown
```python
async def setup_test_admin():
    """Set up admin user for testing."""
    
    # Create regular test user
    user_data = {
        "email": "test_admin@example.com",
        "password": "test_password",
        "name": "Test Admin"
    }
    
    create_response = await client.post("/api/v1/users", json=user_data)
    assert create_response.status_code == 201
    
    # Promote to admin
    promote_response = await client.post(
        "/api/v1/users/promote-admin",
        json={"email": "test_admin@example.com"}
    )
    assert promote_response.status_code == 200
    
    return "test_admin@example.com"

async def cleanup_test_data():
    """Clean up test data after testing."""
    
    # Remove test admin user
    await client.delete("/api/v1/users/test_admin@example.com")
```

### 🚀 **CI/CD Integration**

#### GitHub Actions Example
```yaml
name: Test Admin Functionality

jobs:
  test:
    runs-on: ubuntu-latest
    env:
      TEST_MODE: true
      DATABASE_URL: postgresql://test:test@localhost:5432/test_db
    
    steps:
      - name: Setup Test Environment
        run: |
          export TEST_MODE=true
          python -m pytest tests/test_admin_features.py
      
      - name: Test Admin Promotion
        run: |
          # Test endpoint is available in test mode
          curl -X POST http://localhost:8000/api/v1/users/promote-admin \
               -H "Content-Type: application/json" \
               -d '{"email": "test@example.com"}'
```

#### Docker Test Environment
```dockerfile
FROM python:3.11-slim

# Test environment configuration
ENV TEST_MODE=true
ENV ENVIRONMENT=test

# Application setup
COPY . /app
WORKDIR /app

# Test dependencies
RUN pip install -r requirements-test.txt

# Run tests with admin functionality
CMD ["python", "-m", "pytest", "tests/", "-v"]
```

## Error Handling

### 🚨 **Comprehensive Error Responses**

#### Production Environment Error
```json
{
    "detail": "Not allowed in production.",
    "status_code": 403
}
```

#### User Not Found Error
```json
{
    "detail": "User not found.",
    "status_code": 404
}
```

#### Invalid Email Format Error
```json
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "Invalid email format",
            "type": "value_error.email"
        }
    ],
    "status_code": 422
}
```

#### Database Error
```json
{
    "detail": "Database connection error.",
    "status_code": 500
}
```

### 🔍 **Error Debugging**

#### Test Environment Debugging
```python
# Check environment configuration
import os
print(f"TEST_MODE: {os.getenv('TEST_MODE')}")
print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT')}")

# Verify test mode detection
from src.utils.environment import is_test_mode
print(f"Test mode active: {is_test_mode()}")

# Check database connectivity
try:
    response = await client.post("/api/v1/users/promote-admin", 
                               json={"email": "test@example.com"})
    print(f"Response: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
```

## Testing Strategies

### 🧪 **Unit Testing**

```python
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

class TestPromoteAdmin:
    
    def test_promote_admin_success(self, client, test_user):
        """Test successful admin promotion."""
        
        with patch('src.utils.environment.is_test_mode', return_value=True):
            response = client.post(
                "/api/v1/users/promote-admin",
                json={"email": test_user.email}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert f"User {test_user.email} promoted to admin" in data["detail"]
    
    def test_promote_admin_production_blocked(self, client):
        """Test that endpoint is blocked in production."""
        
        with patch('src.utils.environment.is_test_mode', return_value=False):
            response = client.post(
                "/api/v1/users/promote-admin",
                json={"email": "test@example.com"}
            )
            
            assert response.status_code == 403
            assert "Not allowed in production" in response.json()["detail"]
    
    def test_promote_admin_user_not_found(self, client):
        """Test handling of non-existent user."""
        
        with patch('src.utils.environment.is_test_mode', return_value=True):
            response = client.post(
                "/api/v1/users/promote-admin",
                json={"email": "nonexistent@example.com"}
            )
            
            assert response.status_code == 404
            assert "User not found" in response.json()["detail"]
    
    def test_promote_admin_invalid_email(self, client):
        """Test validation of email format."""
        
        with patch('src.utils.environment.is_test_mode', return_value=True):
            response = client.post(
                "/api/v1/users/promote-admin",
                json={"email": "invalid-email"}
            )
            
            assert response.status_code == 422
```

### 🔄 **Integration Testing**

```python
@pytest.mark.asyncio
async def test_admin_promotion_workflow(client, database_session):
    """Test complete admin promotion workflow."""
    
    # Ensure test mode
    with patch('src.utils.environment.is_test_mode', return_value=True):
        
        # 1. Create regular user
        user_data = {
            "email": "workflow@example.com",
            "password": "test_password",
            "name": "Workflow User"
        }
        
        create_response = client.post("/api/v1/users", json=user_data)
        assert create_response.status_code == 201
        
        # 2. Verify user is not admin
        user = await get_user_by_email(database_session, "workflow@example.com")
        assert not user.is_admin
        
        # 3. Promote to admin
        promote_response = client.post(
            "/api/v1/users/promote-admin",
            json={"email": "workflow@example.com"}
        )
        assert promote_response.status_code == 200
        
        # 4. Verify admin status
        updated_user = await get_user_by_email(database_session, "workflow@example.com")
        assert updated_user.is_admin
        
        # 5. Test admin functionality
        login_response = client.post("/api/v1/auth/login", json={
            "email": "workflow@example.com",
            "password": "test_password"
        })
        token = login_response.json()["access_token"]
        
        admin_response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert admin_response.status_code == 200
```

## Best Practices

### ✅ **Do's**

- **Always Check Test Mode**: Verify environment before any operations
- **Use in Test Automation**: Integrate with test setup and teardown
- **Handle Errors Gracefully**: Provide clear error messages for debugging
- **Clean Up Test Data**: Remove test users after testing
- **Document Test Usage**: Clear documentation for test scenarios
- **Validate Email Input**: Ensure proper email format validation
- **Use with Fixtures**: Integrate with pytest fixtures for reusability

### ❌ **Don'ts**

- **Don't Use in Production**: Never enable in production environments
- **Don't Skip Environment Checks**: Always validate test mode first
- **Don't Hard-Code Emails**: Use parameterized test data
- **Don't Leave Test Data**: Clean up after test completion
- **Don't Bypass Security**: Respect environment-based restrictions
- **Don't Ignore Errors**: Handle all error conditions properly
- **Don't Mix with Production Code**: Keep test utilities separate

## Environment Configuration

### 🔧 **Environment Variables**

```bash
# Test environment
TEST_MODE=true
ENVIRONMENT=test
DATABASE_URL=postgresql://test:test@localhost:5432/test_db

# Production environment (endpoint disabled)
TEST_MODE=false
ENVIRONMENT=production
DATABASE_URL=postgresql://prod:prod@localhost:5432/prod_db
```

### 🛡️ **Security Considerations**

```python
# Production safety checks
def is_test_mode() -> bool:
    """Secure test mode detection."""
    return (
        os.getenv("TEST_MODE", "false").lower() == "true" and
        os.getenv("ENVIRONMENT", "production") != "production"
    )

# Multiple validation layers
if not is_test_mode():
    raise HTTPException(403, "Not allowed in production.")
```

## Related Files

- **`src/utils/environment.py`** - Environment detection and validation
- **`src/models/user.py`** - User model with admin flag
- **`src/core/database.py`** - Database session management
- **`tests/conftest.py`** - Test configuration and fixtures

## Dependencies

- **`fastapi`** - Web framework and routing
- **`sqlalchemy`** - Database ORM for user operations
- **`typing_extensions`** - Type hints for response schemas

---

*This User Test Utilities API provides secure, environment-restricted testing capabilities for admin functionality while maintaining strict production safety controls.*
