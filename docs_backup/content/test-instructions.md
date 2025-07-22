# Comprehensive Testing Guide

This guide provides complete instructions for running, debugging, and maintaining the test suite across the entire ReViewPoint platform, including backend unit tests, frontend tests, integration tests, and end-to-end testing.

## Testing Architecture Overview

ReViewPoint implements a comprehensive testing strategy with multiple layers:

- **Backend Unit Tests**: Fast, isolated tests for individual components
- **Backend Integration Tests**: Database and API integration testing
- **Frontend Unit Tests**: Component and utility function testing with Vitest
- **End-to-End Tests**: Complete user workflow testing with Playwright
- **Cross-Project Integration**: Full-stack integration testing

## Prerequisites & Setup

### Backend Testing Prerequisites
- Python 3.11.9+ with Hatch environment management
- All dependencies installed via `hatch env create`
- Required pytest plugins (automatically installed):
  - `pytest-asyncio` - Async test support
  - `pytest-httpx` - HTTP client testing
  - `pytest-mock` - Mocking and fixtures
  - `pytest-cov` - Coverage reporting
- Database: SQLite (auto-configured for tests) or PostgreSQL

### Frontend Testing Prerequisites  
- Node.js 18+ with PNPM package manager
- Dependencies installed via `pnpm install`
- Testing frameworks:
  - **Vitest** - Unit and integration testing
  - **Playwright** - End-to-end testing
  - **Testing Library** - Component testing utilities

### Environment Setup
```bash
# Backend environment setup
cd backend
hatch env create
hatch shell

# Frontend environment setup  
cd frontend
pnpm install

# Full project setup
pnpm run install:all
```

## Running Backend Tests

### Quick Test Commands

```bash
# Run all backend tests
hatch run pytest

# Run with verbose output
hatch run pytest -v

# Run fast tests only (excludes slow integration tests)
python run-fast-tests.py

# Run specific test file
hatch run pytest backend/tests/core/test_database.py

# Run specific test function
hatch run pytest backend/tests/core/test_database.py::test_async_session_creation

# Run tests matching pattern
hatch run pytest -k "test_user"
```

### Coverage Reporting

```bash
# Generate coverage report (terminal + HTML)
hatch run pytest --cov=src --cov-report=html --cov-report=term

# Coverage with XML output (for CI/CD)
hatch run pytest --cov=src --cov-report=xml --cov-report=term

# Coverage excluding slow tests
python run-fast-tests.py --cov=src --cov-report=html
```

### Test Categories & Filtering

```bash
# Run only database tests
hatch run pytest backend/tests/core/

# Run only API tests  
hatch run pytest backend/tests/api/

# Run only unit tests (fast)
hatch run pytest -m "not slow"

# Run integration tests
hatch run pytest -m "integration"

# Run async tests specifically
hatch run pytest -m "asyncio"
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
