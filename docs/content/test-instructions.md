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

## Controlling Log Levels During Testing

You can control the log verbosity using pytest CLI flags without manually setting environment variables:

### Using CLI Flags (Recommended)

```powershell
# Debug level - detailed SQL queries and internal state
hatch run pytest --log-level=DEBUG

# Info level - general test progress (default in most hatch scripts)
hatch run pytest --log-level=INFO

# Warning level - minimal output (default for fast tests)
hatch run pytest --log-level=WARNING

# Using log-cli-level for live log output
hatch run pytest --log-cli-level=DEBUG -s
```

### Using Convenient Hatch Scripts

```powershell
# Debug testing with detailed logs
hatch run test-debug

# Quiet testing with minimal logs
hatch run test-quiet

# Default testing (INFO level)
hatch run test
```

### Available Log Levels

- **DEBUG**: Detailed debugging (SQL queries, internal state, all framework logs)
- **INFO**: General information (default for most development testing)
- **WARNING**: Minimal output (default for fast tests, recommended for CI/CD)
- **ERROR**: Only error messages
- **CRITICAL**: Only critical errors

**Note**: The default log level is WARNING to reduce test noise, but you can override it anytime using the CLI flags above.


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
