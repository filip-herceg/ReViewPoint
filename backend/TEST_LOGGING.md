# Test Logging Configuration

This document explains how to configure logging levels for pytest runs in the ReViewPoint backend.

## Quick Start

```bash
# Show available log levels and current configuration
python set-test-log-level.py

# Set to DEBUG for detailed output (PowerShell)
.\set-log-level.ps1 DEBUG

# Run tests with the configured level
python run-fast-tests.py
hatch run test
```

## Available Log Levels

| Level    | What it shows |
|----------|---------------|
| CRITICAL | Only critical errors (application crashes) |
| ERROR    | Error messages (failed operations, exceptions) |
| WARNING  | Warning messages (deprecated features, recoverable issues) |
| INFO     | General information (test progress, basic operations) |
| DEBUG    | Detailed debugging information (SQL queries, internal state) |

## Default Configuration

- **Main tests**: INFO level (changed from DEBUG to reduce noise)
- **Fast tests**: INFO level (configurable via environment variable)
- **Log file**: Always DEBUG level for complete debugging information

## How to Change Log Levels

### 1. Using the Helper Script (Recommended)

```bash
# Show current configuration and available levels
python set-test-log-level.py

# Set to DEBUG for detailed output
python set-test-log-level.py DEBUG

# Set to WARNING for minimal output
python set-test-log-level.py WARNING
```

### 2. Using Environment Variables

#### For PowerShell (Windows)

```powershell
# Set for current session
$env:REVIEWPOINT_TEST_LOG_LEVEL = 'DEBUG'

# Run fast tests with DEBUG logging
$env:REVIEWPOINT_TEST_LOG_LEVEL = 'DEBUG'; python run-fast-tests.py

# Run main tests with DEBUG logging
$env:REVIEWPOINT_TEST_LOG_LEVEL = 'DEBUG'; hatch run test
```

#### For Bash (Linux/Mac)

```bash
# Set for current session
export REVIEWPOINT_TEST_LOG_LEVEL=DEBUG

# Run fast tests with DEBUG logging
REVIEWPOINT_TEST_LOG_LEVEL=DEBUG python run-fast-tests.py

# Run main tests with DEBUG logging
REVIEWPOINT_TEST_LOG_LEVEL=DEBUG hatch run test
```

### 3. Direct pytest Arguments

```bash
# Override log level directly with pytest
python -m pytest --log-cli-level=DEBUG tests/
hatch run pytest --log-cli-level=WARNING tests/
```

## Configuration Files

### Main Tests (pyproject.toml)

- Default log level set to INFO in `[tool.pytest.ini_options]`
- Can be overridden with `REVIEWPOINT_TEST_LOG_LEVEL` environment variable
- Log file always captures DEBUG level information

### Fast Tests (run-fast-tests.py)

- Reads `REVIEWPOINT_TEST_LOG_LEVEL` environment variable
- Defaults to INFO if not set
- Applies the level via `--log-cli-level` argument

## Examples

### Development Workflow

```bash
# Normal development - minimal logging
python run-fast-tests.py

# Debugging a specific issue - verbose logging
python set-test-log-level.py DEBUG
python run-fast-tests.py tests/test_problematic_feature.py

# Reset to normal after debugging
python set-test-log-level.py INFO
```

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Run tests with minimal logging
  run: |
    export REVIEWPOINT_TEST_LOG_LEVEL=WARNING
    python run-fast-tests.py
```

## Tips

1. **Start with INFO**: Good balance of information without overwhelming output
2. **Use DEBUG when troubleshooting**: Shows SQL queries, detailed request/response data
3. **Use WARNING in CI**: Faster runs with only important messages
4. **Check log files**: The `tests/test_debug.log` file always contains DEBUG information
5. **Use the helper script**: `python set-test-log-level.py` for easy level management

## Implementation Details

The logging configuration works by:

1. Setting a default level in `pyproject.toml`
2. Reading `REVIEWPOINT_TEST_LOG_LEVEL` environment variable
3. Passing the level to pytest via `--log-cli-level` argument
4. Maintaining full DEBUG logging in log files for troubleshooting
