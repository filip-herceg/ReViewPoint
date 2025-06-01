# `tests/conftest.py`

| Item | Value |
|------|-------|
| **Layer** | Test Infrastructure |
| **Responsibility** | Provides pytest fixtures for database testing and environment setup |
| **Status** | 🟢 Done |

## 1. Purpose  
This file sets up the test infrastructure for the application, focusing on providing database fixtures for async SQLAlchemy testing. **All tests now use a real test database (e.g., `test.db` or a dedicated test Postgres instance), not in-memory.** It ensures that tests run with a clean, isolated database environment and proper environment variables.

## 2. Key Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `set_required_env_vars` | function | Sets test environment variables using monkeypatch |
| `async_engine` | session | Creates a shared SQLAlchemy engine for the test session, using the real test DB |
| `async_session` | function | Provides an AsyncSession for database operations in tests |
| `cleanup_db` | function | Truncates all tables after each test for isolation |

## 3. Behaviour & Edge-Cases  

- Environment variables are set for each test function automatically with `autouse=True`
- Database schemas are created for the test session
- **A real test database is used for all tests**
- After each test, all tables are truncated to ensure isolation
- No in-memory databases are used

## 4. Dependencies  

- **Internal**:
  - `backend.models.base`: For Base metadata to create tables
  
- **External**:
  - `pytest`: For test infrastructure
  - `pytest_asyncio`: For async fixture support
  - `sqlalchemy.ext.asyncio`: For async database testing

## 5. Usage in Tests  
Tests can use these fixtures by simply declaring them as parameters:

```python
@pytest.mark.asyncio
async def test_example(async_session):
    # Use async_session for database operations
    result = await async_session.execute(...)
```

## 6. Notes
- The fixtures handle proper setup and teardown of database connections.
- **All tests now use a real test database, and cleanup is handled automatically after each test.**
- Remove any references to in-memory DBs in new or existing tests.
