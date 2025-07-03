# Fast Testing Setup for ReViewPoint Backend

This directory contains the optimized testing configuration for rapid development and testing cycles.

## Quick Start

The easiest way to run fast tests is using hatch environments:

```bash
# Run fast tests (from backend directory)
hatch run fast:test

# Run fast tests with specific pattern
hatch run fast:test tests/test_auth.py

# Run fast tests in watch mode
hatch run fast:watch

# Run specific test function
hatch run fast:test -k "test_user_creation"
```

## What Makes These Tests Fast?

1. **SQLite In-Memory Database**: Uses `:memory:` instead of PostgreSQL containers
2. **Optimized Fixtures**: Reduced fixture scopes and cached test data
3. **Mocked External Services**: All slow external calls are mocked
4. **Reduced Logging**: Minimal log output to reduce I/O overhead
5. **Parallel Execution**: Tests can run in parallel safely
6. **Skip Slow Tests**: Automatically skips tests marked as `@pytest.mark.slow`

## File Structure

```
testing/
├── fast/
│   ├── conftest.py      # Fast test configuration and fixtures
│   ├── pytest.ini      # Fast test pytest configuration
│   ├── templates.py     # Base classes and utilities for fast tests
│   └── README.md        # This file
```

## Performance Comparison

- **Full test suite (PostgreSQL)**: ~2-5 minutes
- **Fast test suite (SQLite)**: ~10-30 seconds

## Configuration Details

### Environment Variables (Auto-set)
- `REVIEWPOINT_DB_URL=sqlite+aiosqlite:///:memory:`
- `REVIEWPOINT_LOG_LEVEL=WARNING`
- `FAST_TESTS=1`
- All feature flags enabled
- External services disabled/mocked

### Test Markers
- `@pytest.mark.fast` - Optimized tests
- `@pytest.mark.slow` - Skipped in fast mode  
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests

## Writing Fast Tests

### Use the Base Classes

```python
from testing.fast.templates import FastAPITestCase

class TestAuth(FastAPITestCase):
    async def test_login(self, client, auth_headers):
        response = await self.assert_success(
            client, "POST", "/auth/login", 
            json={"email": "test@example.com", "password": "password123"}
        )
```

### Mark Slow Tests

```python
@pytest.mark.slow
def test_expensive_operation():
    # This test will be skipped in fast mode
    pass
```

### Use Fast Fixtures

The fast conftest provides optimized fixtures:
- `db_session` - Clean SQLite session per test
- `client` - HTTP test client
- `test_user` - Pre-created test user
- `auth_headers` - Authentication headers
- All external services mocked automatically

## Switching Between Test Modes

### Fast Tests (Development)
```bash
hatch run fast:test
```

### Full Tests (CI/Integration)
```bash
hatch run test  # or simply: pytest
```

## Troubleshooting

### "Import not found" errors
Make sure you're running from the `backend/` directory and using the hatch environments.

### Tests still slow
Check that you're using the fast environment and that slow tests are properly marked:
```bash
hatch run fast:test -v  # Shows which tests are running
```

### Database issues
Fast tests use SQLite which has some differences from PostgreSQL. Mark PostgreSQL-specific tests as slow:
```python
@pytest.mark.slow  # Will use PostgreSQL in full test suite
def test_postgresql_specific_feature():
    pass
```
