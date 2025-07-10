# Test Logging Configuration

This document explains the logging configuration and options available when running tests in the ReViewPoint backend.

## Overview

The ReViewPoint backend uses a sophisticated logging system that can be controlled during test execution to provide the right level of detail for different scenarios.

## Default Configuration

By default, tests run with **WARNING** level logging to minimize noise while still capturing important information. This provides a clean test output suitable for CI/CD environments.

## Log Level Control

### Using CLI Flags (Recommended)

```bash
# Set log level for test execution
hatch run pytest --log-level=DEBUG    # Maximum detail
hatch run pytest --log-level=INFO     # Moderate detail
hatch run pytest --log-level=WARNING  # Minimal detail (default)
hatch run pytest --log-level=ERROR    # Errors only

# Live log output during tests
hatch run pytest --log-cli-level=DEBUG -s
```

### Using Hatch Scripts

```bash
# Predefined test scripts with appropriate log levels
hatch run test-debug    # DEBUG level with live output
hatch run test-quiet    # WARNING level, minimal noise
hatch run test          # INFO level, balanced output
```

### Using Environment Variables (Legacy)

```bash
# PowerShell
$env:REVIEWPOINT_LOG_LEVEL = 'DEBUG'
hatch run pytest

# Bash/Linux
export REVIEWPOINT_LOG_LEVEL=DEBUG
hatch run pytest
```

## Log Level Details

### DEBUG Level
- SQL queries and database operations
- Internal application state
- Framework debugging information
- Complete request/response cycles
- Fixture setup and teardown details

### INFO Level
- Test execution progress
- Major application operations
- Database connection status
- API endpoint access
- Cache operations

### WARNING Level (Default)
- Deprecation warnings
- Configuration issues
- Performance warnings
- Test skips and important notices

### ERROR Level
- Test failures and exceptions
- Application errors
- Database connection issues
- Critical validation failures

### CRITICAL Level
- System-level failures
- Application crashes
- Critical security issues

## Fast Tests Integration

When running fast tests (`FAST_TESTS=1` environment variable), the logging system automatically defaults to WARNING level to optimize performance while still capturing essential information.

```bash
# Fast tests with custom log level
FAST_TESTS=1 hatch run pytest --log-level=INFO
```

## Configuration Files

The logging configuration is managed through:

- `backend/tests/conftest.py` - Test-specific logging setup
- `backend/src/core/logging.py` - Application logging configuration
- `backend/pyproject.toml` - Default logging settings for different environments

## Troubleshooting

### Common Issues

1. **Log level not taking effect**: Ensure environment variables are not overriding CLI flags
2. **Too much output**: Use ERROR level for minimal output, or check third-party library log levels
3. **Missing expected logs**: Verify the application code is using the correct logger instances

### Debugging Tips

- Use `--log-cli-level=DEBUG -s` for real-time log output during test execution
- Check the `[ENV_SETUP]` messages at the start of test runs to verify log level configuration
- Review individual test files for logger usage patterns

## Related Documentation

- [Testing Guide](TESTING.md) - General testing information
- [Development Guidelines](../docs/content/dev-guidelines.md) - Development workflow
- [Test Log Levels](../docs/content/test-log-levels.md) - Detailed log level guide

## Examples

### Debugging a Failed Test

```bash
# Run specific test with maximum logging
hatch run pytest tests/test_specific.py::test_function --log-level=DEBUG -v -s

# Run with live output for real-time debugging
hatch run pytest tests/test_specific.py --log-cli-level=DEBUG -s
```

### CI/CD Optimization

```bash
# Minimal output for fast CI runs
FAST_TESTS=1 hatch run pytest --log-level=WARNING
```

### Development Workflow

```bash
# Balanced output for development
hatch run pytest --log-level=INFO
```
