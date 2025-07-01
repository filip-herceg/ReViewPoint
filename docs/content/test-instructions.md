# Backend Test Running Instructions

This guide explains how to run all backend tests, including unit, async, API, and integration tests, and how to generate coverage reports.

## Prerequisites

- All dependencies installed (see `pyproject.toml`)
- Required pytest plugins:
  - `pytest-asyncio`
  - `pytest-httpx`
  - `pytest-mock`
- Activate your Hatch environment: `hatch shell`

## Running All Tests

```powershell
hatch run pytest
```

## Running Tests with Coverage Report

```powershell
hatch run pytest --cov=backend --cov-report=term --cov-report=xml
```

## Running Specific Tests (Async/API)

```powershell
hatch run pytest backend/tests/core/test_database.py
hatch run pytest backend/tests/middlewares/test_logging.py
```


## Parallel and Database Test Safety

- All async and API tests are auto-discovered in `backend/tests/`.
- **Parallel test safety:** The test infrastructure is now fully compatible with parallel test execution. Each test function gets its own isolated database engine and connection pool, preventing conflicts and asyncpg errors.
- **Writing parallel-safe DB tests:**
  - Use the provided `async_session` fixture for all DB access in tests. It is function-scoped and parallel-safe.
  - For tests that need to run multiple concurrent DB operations, use the helpers in `DatabaseTestTemplate`:
    - `get_independent_session()` to get a new session for each concurrent operation.
    - `run_concurrent_operations()` to run multiple DB operations in parallel, each with its own session.
- **Legacy/Sequential tests:** The session-scoped engine fixture is still available for legacy or sequential tests.
- Coverage configuration is in `pyproject.toml` under `[tool.coverage]`.
- Minimum coverage target is 80%.

## Troubleshooting

- If you encounter import errors, ensure you are in the correct Hatch environment and your dependencies are installed.
- For more details, see [dev-guidelines.md](dev-guidelines.md).
