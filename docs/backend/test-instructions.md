# Backend Test Running Instructions

This guide explains how to run all backend tests, including unit, async, API, and integration tests, and how to generate coverage reports.

## Prerequisites
- All dependencies installed (see `pyproject.toml`)
- Activate your Poetry environment: `poetry shell`

## Running All Tests
```powershell
poetry run pytest
```

## Running Tests with Coverage Report
```powershell
poetry run pytest --cov=backend --cov-report=term --cov-report=xml
```

## Running Specific Tests (Async/API)
```powershell
poetry run pytest backend/tests/core/test_database.py
poetry run pytest backend/tests/middlewares/test_logging.py
```

## Notes
- All async and API tests are auto-discovered in `backend/tests/`.
- Coverage configuration is in `pyproject.toml` under `[tool.coverage]`.
- Minimum coverage target is 80%.

## Troubleshooting
- If you encounter import errors, ensure you are in the correct Poetry shell and your dependencies are installed.
- For more details, see `docs/dev-guidelines.md`.
