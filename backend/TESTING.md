# Testing Guide for ReViewPoint Backend

ReViewPoint backend provides two testing modes optimized for different scenarios:

## 🚀 Quick Start

### Fast Tests (for Development)
```bash
# Simple way - use the test runner
python test.py fast

# Or directly with hatch  
hatch run fast:test

# Watch mode for continuous testing
python test.py watch
```

### Full Tests (for CI/Production)
```bash
# Simple way - use the test runner
python test.py full

# Or directly with hatch
hatch run test
```

## 📊 Performance Comparison

| Test Mode | Database | Duration | Use Case |
|-----------|----------|----------|----------|
| **Fast** | SQLite in-memory | ~10-30s | Development, quick feedback |
| **Full** | PostgreSQL (containers) | ~2-5min | CI/CD, integration testing |

## 🎯 Test Modes Explained

### Fast Tests (`testing/fast/`)
- **Purpose**: Rapid development and quick feedback loops
- **Database**: SQLite in-memory (`:memory:`)
- **External Services**: All mocked
- **Parallelization**: Safe for parallel execution
- **Configuration**: Optimized for speed over completeness

### Full Tests (default)
- **Purpose**: Complete integration and regression testing
- **Database**: PostgreSQL via Docker containers
- **External Services**: Real or containerized services
- **Configuration**: Production-like environment

## 🛠️ Available Commands

### Using the Test Runner (Recommended)

```bash
# Fast tests
python test.py fast                    # Run all fast tests
python test.py fast tests/test_auth.py # Run specific test file
python test.py fast -k "test_login"    # Run tests matching pattern

# Full tests  
python test.py full                    # Run complete test suite
python test.py full --cov=src          # With coverage

# Development helpers
python test.py watch                   # Fast tests in watch mode
python test.py coverage                # Fast tests with coverage report
```

### Using Hatch Directly

```bash
# Fast tests
hatch run fast:test
hatch run fast:watch
hatch run fast:coverage

# Full tests
hatch run test
hatch run pytest --cov=src
```

### Using PowerShell (Windows)

```powershell
# Fast tests
.\test.ps1 fast
.\test.ps1 watch

# Full tests
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

The old scattered files have been organized:

- ❌ `conftest_fast.py` → ✅ `testing/fast/conftest.py`
- ❌ `pytest_fast.ini` → ✅ `testing/fast/pytest.ini`  
- ❌ `fast_test_templates.py` → ✅ `testing/fast/templates.py`
- ❌ `run_fast_tests.py` → ✅ `test.py` + hatch environments

**Migration steps:**
1. Old files have been automatically removed
2. Update your workflow to use `python test.py fast` or `hatch run fast:test`
3. Import templates from new location: `from testing.fast.templates import FastAPITestCase`
