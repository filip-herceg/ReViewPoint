# Testing Guide for ReViewPoint Backend

ReViewPoint backend provides multiple testing modes optimized for different scenarios. We recently enhanced the fast test suite to run ALL tests by default while maintaining the speed benefits of the SQLite in-memory database.

## 📋 Quick Reference

| Command | Environment | Database | Tests Included | Duration | Use Case |
|---------|-------------|----------|----------------|----------|----------|
| `hatch run fast:test` | Fast | SQLite (memory) | All (~526) | 30-60s | **Default development** |
| `hatch run fast:fast-only` | Fast | SQLite (memory) | Non-slow (~525) | 10-30s | Quick feedback, TDD |
| `hatch run pytest` | Full | PostgreSQL | All (~526) | 2-5min | CI/CD, production validation |

**🎯 For most development work, use `hatch run fast:test` - it gives you complete test coverage with fast database setup.**

**🔧 Need different log levels?** Use `pytest --log-level=DEBUG` for detailed output or `--log-level=WARNING` for minimal noise. See [Logging Configuration](#logging-configuration) below.

## 🚀 Quick Start

### TL;DR - For Developers

```bash
# ✅ RECOMMENDED: Complete test coverage with fast environment
hatch run fast:test

# ⚡ MAXIMUM SPEED: Skip slow tests for quick feedback
hatch run fast:fast-only

# 🔧 PRODUCTION TESTING: Full PostgreSQL integration
hatch run pytest
```

### Fast Tests (for Development) - UPDATED

```bash
# Run ALL tests with fast environment (NEW DEFAULT - recommended for development)
hatch run fast:test
python run-fast-tests.py

# Run only non-slow tests (classic fast mode, when you need maximum speed)
hatch run fast:fast-only
python run-fast-tests.py --fast-only

# Other options
hatch run fast:watch          # Watch mode for continuous testing
hatch run fast:coverage       # With coverage report
```

### Full Tests (for CI/Production)

```bash
# Complete test suite with PostgreSQL
hatch run pytest
hatch run pytest --cov=src

# Alternative full test runners
python test.py full           # If test.py is available
```

## 📊 Performance Comparison

| Test Mode | Database | Test Count | Duration | Use Case |
|-----------|----------|------------|----------|----------|
| **Fast (All)** | SQLite in-memory | ~526 tests | ~30-60s | Development, complete test coverage |
| **Fast (Fast-only)** | SQLite in-memory | ~525 tests | ~10-30s | Quick feedback, TDD, CI checks |
| **Full** | PostgreSQL (containers) | ~526 tests | ~2-5min | CI/CD, production validation |

## 📝 What Changed (Migration Notes)

**OLD BEHAVIOR** (before update):

- `hatch run fast:test` → Ran only fast tests (skipped `@pytest.mark.slow`)
- Required separate command for complete test coverage

**NEW BEHAVIOR** (current):

- `hatch run fast:test` → Runs ALL tests with fast environment (SQLite in-memory)
- `hatch run fast:fast-only` → Runs only fast tests (skips `@pytest.mark.slow`)
- Better default behavior for development workflow

## 🎯 Test Modes Explained

### Fast Tests (`testing/fast/`)

- **Purpose**: Rapid development with complete or selective test coverage
- **Database**: SQLite in-memory (`:memory:`)
- **External Services**: All mocked
- **Parallelization**: Safe for parallel execution
- **Configuration**: Optimized for speed over completeness

**Two modes available:**

1. **All Tests (Default)**: `hatch run fast:test` or `python run-fast-tests.py`
   - Runs ALL tests including those marked with `@pytest.mark.slow`
   - Uses fast environment (SQLite in-memory) for speed
   - Best for development when you want complete test coverage
   - Duration: ~30-60 seconds

2. **Fast-Only**: `hatch run fast:fast-only` or `python run-fast-tests.py --fast-only`
   - Skips tests marked with `@pytest.mark.slow`
   - Maximum speed for quick feedback loops
   - Best for TDD or when making frequent changes  
   - Duration: ~10-30 seconds

### Full Tests (default environment)

- **Purpose**: Complete integration and regression testing
- **Database**: PostgreSQL via Docker containers
- **External Services**: Real or containerized services
- **Configuration**: Production-like environment
- **Duration**: ~2-5 minutes

## 🛠️ Available Commands

### Using Hatch (Recommended)

```bash
# Fast tests - ALL tests with fast environment (SQLite in-memory)
hatch run fast:test                           # Run all tests
hatch run fast:test tests/test_auth.py        # Run specific test file
hatch run fast:test -k "test_login"           # Run tests matching pattern

# Fast tests - Only non-slow tests (maximum speed)
hatch run fast:fast-only                      # Run fast subset only
hatch run fast:fast-only -k "test_user"       # Fast subset with pattern

# Other fast test options
hatch run fast:watch                          # Watch mode for continuous testing
hatch run fast:coverage                       # With coverage report

# Full tests with PostgreSQL
hatch run pytest                             # Complete test suite
hatch run pytest --cov=src                   # With coverage
```

### Using the Fast Test Script Directly

```bash
# All tests with fast environment
python run-fast-tests.py                     # All tests, fast environment
python run-fast-tests.py tests/test_auth.py  # Specific file
python run-fast-tests.py -k "test_login"     # Pattern matching

# Fast-only tests (skip slow tests)
python run-fast-tests.py --fast-only         # Fast subset only
python run-fast-tests.py --fast-only -v      # With verbose output
```

### Legacy Test Runner (if available)

```bash
# Alternative commands (may not be available in all setups)
python test.py fast                           # Fast tests
python test.py full                           # Full tests
```

### Using PowerShell (Windows)

```powershell
# If PowerShell scripts are available
.\test.ps1 fast
.\test.ps1 full
```

## 📁 File Organization

```
backend/
├── testing/
│   └── fast/                    # Fast test configuration
│       ├── conftest.py          # Fast fixtures and config
│       ├── pytest.ini          # Fast pytest settings
│       ├── templates.py         # Base classes for fast tests
│       └── README.md            # Fast testing documentation
├── tests/                       # All test files
│   ├── conftest.py             # Full test configuration
│   ├── test_auth.py
│   ├── test_users.py
│   └── ...
├── test.py                      # Cross-platform test runner
├── test.ps1                     # PowerShell test runner
└── pyproject.toml              # Environment configurations
```

## ✅ Writing Tests

### For Fast Tests

Use the optimized base classes:

```python
from testing.fast.templates import FastAPITestCase

class TestUserEndpoints(FastAPITestCase):
    async def test_create_user(self, client, db_session):
        response = await self.assert_success(
            client, "POST", "/users",
            json={"email": "test@example.com", "name": "Test User"}
        )
        assert response.json()["email"] == "test@example.com"
```

### For Full Tests

Use standard pytest patterns:

```python
import pytest

class TestUserIntegration:
    @pytest.mark.slow  # Will be skipped in fast mode
    async def test_user_with_external_service(self, client):
        # This test uses real external services
        pass
```

## 🏷️ Test Markers

Use markers to categorize your tests:

```python
@pytest.mark.fast       # Optimized for speed
@pytest.mark.slow       # Skipped in fast mode
@pytest.mark.unit       # Unit tests
@pytest.mark.integration # Integration tests
@pytest.mark.auth       # Authentication tests
@pytest.mark.database   # Database tests
```

## ⚙️ Configuration

### Environment Variables

Fast tests automatically set:
- `FAST_TESTS=1`
- `REVIEWPOINT_DB_URL=sqlite+aiosqlite:///:memory:`
- `REVIEWPOINT_LOG_LEVEL=WARNING`
- All feature flags enabled
- External services mocked

### Hatch Environments

The project defines these environments in `pyproject.toml`:

- **default**: Full test suite with PostgreSQL
- **fast**: Optimized for speed with SQLite
- **types**: Type checking with mypy

## 🔧 Troubleshooting

### Common Issues

**"Import not found" errors**
```bash
# Make sure you're in the backend directory
cd backend
hatch run fast:test
```

**Tests still slow in fast mode**
```bash
# Check if slow tests are properly marked
hatch run fast:test -v  # Shows which tests run

# Mark slow tests
@pytest.mark.slow
def test_expensive_operation():
    pass
```

**Database differences between SQLite and PostgreSQL**
```python
# Mark PostgreSQL-specific tests as slow
@pytest.mark.slow  
def test_postgresql_specific_feature():
    # This will use PostgreSQL in full mode
    pass
```

### Getting Help

1. Check the fast testing README: `testing/fast/README.md`
2. Run tests with verbose output: `python test.py fast -v`
3. Check the test configuration: `testing/fast/pytest.ini`

## 🎯 Best Practices

1. **Use fast tests for TDD**: Quick feedback during development
2. **Use full tests for integration**: Before merging/deploying
3. **Mark expensive tests**: Use `@pytest.mark.slow` for tests that need real services
4. **Leverage base classes**: Use `FastAPITestCase` and `DatabaseTestCase` from templates
5. **Mock external dependencies**: Keep fast tests isolated and predictable

## 📈 Migration from Old Setup

### Recent Test Suite Updates

The fast test suite behavior has been updated for better development workflow:

**Key Changes:**

- ✅ `hatch run fast:test` now runs ALL tests (including slow ones) with fast environment
- ✅ Added `hatch run fast:fast-only` for the old behavior (skip slow tests)
- ✅ `run-fast-tests.py` updated with `--fast-only` flag
- ✅ Better default behavior for complete test coverage during development

### File Organization Updates

The old scattered files have been consolidated into a unified conftest approach:

- ❌ `conftest_fast.py` → ✅ Unified `tests/conftest.py` with conditional logic
- ❌ `testing/environments/fast/` → ✅ Functionality merged into main conftest
- ❌ `pytest_fast.ini` → ✅ `testing/fast/pytest.ini`  
- ❌ `fast_test_templates.py` → ✅ `testing/fast/templates.py`
- ✅ `run-fast-tests.py` enhanced with environment variable setup

**Migration Completed:**

The new unified approach uses a single `tests/conftest.py` file that conditionally switches between fast (SQLite in-memory) and slow (PostgreSQL container) test modes based on the `FAST_TESTS` environment variable. This eliminates the old file-swapping mechanism and provides a more maintainable solution.
3. Update CI/CD scripts if needed to use the new command structure

## Logging Configuration

### Overview

Test logging is now configurable via pytest CLI flags. The default log level is WARNING to reduce test noise, but you can easily override it for debugging purposes without manually setting environment variables.

### Available Log Levels

| Level    | What it shows | When to use |
|----------|---------------|-------------|
| **CRITICAL** | Only critical errors (application crashes) | Production monitoring |
| **ERROR**    | Error messages (failed operations, exceptions) | Error-only output |
| **WARNING**  | Warning messages (deprecated features, recoverable issues) | **Default (minimal noise)** |
| **INFO**     | General information (test progress, basic operations) | Development debugging |
| **DEBUG**    | Detailed debugging information (SQL queries, internal state) | Deep troubleshooting |

### CLI Flag Method (Recommended)

```bash
# Override log level via pytest CLI flags
pytest --log-level=DEBUG               # Detailed troubleshooting
pytest --log-level=INFO                # General information
pytest --log-level=WARNING             # Minimal output (default)

# With hatch (recommended for development)
hatch run pytest --log-level=DEBUG     # Detailed logs
hatch run pytest --log-level=INFO      # Balanced output
hatch run pytest --log-level=WARNING   # Minimal output

# Live log output during test execution
hatch run pytest --log-cli-level=DEBUG -s    # Show logs in real-time
```

### Convenient Hatch Scripts

```bash
hatch run test-debug    # Uses --log-cli-level=DEBUG for detailed output
hatch run test-quiet    # Uses --log-cli-level=WARNING for minimal output  
hatch run test          # Uses default INFO level
```

### Environment Variable Method (Legacy)

```bash
# PowerShell (still supported)
$env:REVIEWPOINT_LOG_LEVEL = 'DEBUG'
hatch run pytest

# Bash/Linux (still supported)
export REVIEWPOINT_LOG_LEVEL=DEBUG
hatch run pytest
```

### Key Features

- **Default**: WARNING level reduces test noise
- **CLI Override**: Use `--log-level` or `--log-cli-level` flags
- **No Manual Env Vars**: CLI flags are automatically detected and converted
- **Hatch Integration**: Convenient scripts for common log levels
- **Fast/Slow Compatible**: Works with both SQLite and PostgreSQL test modes

### Tips for Log Levels

- **Start with WARNING**: Default minimal output for clean test runs
- **Use INFO for development**: Good balance when actively working on features
- **Use DEBUG when stuck**: Shows SQL queries, detailed request/response data
- **Use CLI flags**: Easier than setting environment variables manually

### Examples

```bash
# Debug a specific test with detailed logs
hatch run pytest tests/test_auth.py::test_login --log-level=DEBUG -s

# Run all tests quietly (CI-style)
hatch run pytest --log-level=WARNING

# Development workflow with balanced output
hatch run test-debug tests/test_user_creation.py
```
