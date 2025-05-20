# `tests/conftest.py`

| Item | Value |
|------|-------|
| **Layer** | Test Infrastructure |
| **Responsibility** | Provides pytest fixtures for database testing and environment setup |
| **Status** | 🟢 Done |
| **Owner** | @ReViewPointTeam |

## 1. Purpose  
This file sets up the test infrastructure for the application, particularly focusing on providing database fixtures for async SQLAlchemy testing. It ensures that tests run with a clean, isolated database environment and proper environment variables.

## 2. Key Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `set_required_env_vars` | function | Sets test environment variables using monkeypatch |
| `async_engine` | session | Creates a shared SQLAlchemy engine for the test session |
| `async_engine_function` | function | Creates isolated engine instances for each test function |
| `async_session` | function | Provides an AsyncSession for database operations in tests |

## 3. Behaviour & Edge-Cases  

- Environment variables are set for each test function automatically with `autouse=True`
- Database schemas are created/dropped for each test function for isolation
- Unique database identifiers prevent test cross-contamination
- In-memory SQLite databases are used for performance and cleanup
- Test engines use shared cache for session-scoped fixtures but unique IDs for function-scoped fixtures

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
The fixtures handle proper setup and teardown of database connections, ensuring that tests don't leave resources open or leak between test runs.
