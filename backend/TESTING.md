# Backend Testing Guide

> **Comprehensive testing documentation for the ReViewPoint backend.**

---

## Overview

The ReViewPoint backend uses a comprehensive testing strategy with pytest, covering unit tests, integration tests, and API endpoint testing. All tests are designed to run in isolation with proper database cleanup.

## Test Structure

```
backend/tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_*.py               # Root-level integration tests
├── api/                    # API endpoint tests
│   └── v1/                # Version 1 API tests
├── core/                   # Core functionality tests
├── models/                 # Database model tests
├── repositories/           # Data access layer tests
├── services/               # Business logic tests
└── utils/                  # Utility function tests
```

## Running Tests

### Quick Commands
```bash
# All tests
hatch run pytest

# Fast tests only (excludes slow integration tests)
python run-fast-tests.py

# Specific test module
hatch run pytest tests/core/test_database.py

# With coverage
hatch run pytest --cov=src --cov-report=html
```

### Test Categories
- **Unit Tests**: Fast, isolated tests for individual functions
- **Integration Tests**: Database and external service integration
- **API Tests**: Full HTTP endpoint testing
- **Performance Tests**: Load and timing validation

## Test Database

### Configuration
- Uses in-memory SQLite for speed
- Each test gets isolated database instance
- Automatic cleanup after each test
- Real schema with migrations applied

### Fixtures
```python
@pytest.fixture
async def async_session():
    """Provides isolated database session for tests"""
    # Creates new in-memory database
    # Applies all migrations
    # Yields session for test use
    # Cleans up automatically
```

## Test Writing Guidelines

### Test Structure
```python
@pytest.mark.asyncio
async def test_example_functionality(async_session):
    # 1. Arrange - Set up test data
    user = User(email="test@example.com")
    async_session.add(user)
    await async_session.commit()
    
    # 2. Act - Execute the functionality
    result = await get_user_by_email(async_session, "test@example.com")
    
    # 3. Assert - Verify results
    assert result.email == "test@example.com"
    assert result.id is not None
```

### Naming Conventions
- Test files: `test_*.py`
- Test functions: `test_<functionality>`
- Test classes: `Test<ClassName>`
- Descriptive names explaining what is being tested

### Markers
```python
@pytest.mark.slow          # For slow integration tests
@pytest.mark.asyncio       # For async tests
@pytest.mark.integration   # For integration tests
@pytest.mark.api          # For API endpoint tests
```

## Mocking and Fixtures

### Database Fixtures
- `async_engine`: Session-scoped database engine
- `async_session`: Function-scoped database session
- `test_user`: Pre-created test user
- `test_file`: Pre-created test file

### External Service Mocking
```python
@pytest.fixture
def mock_redis(mocker):
    """Mock Redis cache for testing"""
    return mocker.patch("backend.core.cache.redis_client")

@pytest.fixture  
def mock_storage(mocker):
    """Mock S3/MinIO storage for testing"""
    return mocker.patch("backend.services.storage.storage_client")
```

## Coverage Requirements

- **Minimum Coverage**: 80% overall
- **Critical Modules**: 90%+ coverage required
- **New Code**: Must include tests
- **Coverage Reports**: Generated in `htmlcov/`

### Viewing Coverage
```bash
# Generate and view HTML coverage report
hatch run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Performance Testing

### Database Performance
```python
@pytest.mark.slow
async def test_bulk_user_creation(async_session):
    """Test performance of bulk operations"""
    start_time = time.time()
    
    users = [User(email=f"user{i}@test.com") for i in range(1000)]
    async_session.add_all(users)
    await async_session.commit()
    
    duration = time.time() - start_time
    assert duration < 5.0  # Should complete in under 5 seconds
```

### API Performance
```python
async def test_api_response_time(test_client, auth_headers):
    """Test API endpoint response times"""
    start_time = time.time()
    
    response = await test_client.get("/api/v1/users/me", headers=auth_headers)
    
    duration = time.time() - start_time
    assert response.status_code == 200
    assert duration < 0.5  # Should respond in under 500ms
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run Backend Tests
  run: |
    cd backend
    hatch run pytest --cov=src --cov-report=xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: backend/coverage.xml
```

### Pre-commit Hooks
- Run fast tests before commit
- Lint and format code
- Type checking with mypy

## Debugging Tests

### Verbose Output
```bash
# Verbose test output
hatch run pytest -v

# Show print statements
hatch run pytest -s

# Stop on first failure
hatch run pytest -x

# Run specific test
hatch run pytest tests/core/test_database.py::test_async_session_creation
```

### Test Debugging
```python
import pytest

def test_debug_example():
    # Use pytest.set_trace() for debugging
    pytest.set_trace()
    
    # Or use print statements with -s flag
    print("Debug information here")
```

## Common Issues

### Database Connection Errors
- Ensure test database is properly configured
- Check for connection leaks
- Verify isolation between tests

### Async/Await Issues
- All database operations must be awaited
- Use `@pytest.mark.asyncio` for async tests
- Proper session management in fixtures

### Test Isolation
- Don't rely on test execution order
- Clean up all test data
- Use fresh database for each test

## Best Practices

1. **Test Independence**: Each test should run independently
2. **Fast Tests**: Keep unit tests under 100ms
3. **Realistic Data**: Use realistic test data
4. **Edge Cases**: Test error conditions and edge cases
5. **Documentation**: Comment complex test logic
6. **Maintenance**: Keep tests updated with code changes

---

For specific testing examples, see the test files in the `backend/tests/` directory.
