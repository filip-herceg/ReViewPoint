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

## Notes
- All async and API tests are auto-discovered in `backend/tests/`.
- Coverage configuration is in `pyproject.toml` under `[tool.coverage]`.
- Minimum coverage target is 80%.

## Troubleshooting
- If you encounter import errors, ensure you are in the correct Hatch environment and your dependencies are installed.
- For more details, see [dev-guidelines.md](dev-guidelines.md).
