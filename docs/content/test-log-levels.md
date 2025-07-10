# Test Log Level Control

This guide explains how to control logging verbosity during test execution in the ReViewPoint backend.

## Overview

The ReViewPoint backend test suite provides flexible log level control to help with debugging while keeping CI/CD runs clean. By default, tests use WARNING level to reduce noise, but you can easily override this for debugging purposes.

## Quick Reference

| Command | Log Level | Use Case |
|---------|-----------|----------|
| `hatch run pytest` | WARNING | Default (minimal output) |
| `hatch run pytest --log-level=DEBUG` | DEBUG | Detailed debugging |
| `hatch run pytest --log-level=INFO` | INFO | Development workflow |
| `hatch run test-debug` | DEBUG | Convenient debug script |
| `hatch run test-quiet` | WARNING | Minimal output script |

## Available Log Levels

### DEBUG

- **Shows**: SQL queries, internal state, framework details, all operations
- **Use for**: Deep troubleshooting, understanding test flow, debugging failures
- **Example output**: SQLite operations, fixture setup/teardown, detailed error traces

### INFO

- **Shows**: General test progress, major operations, fixture information
- **Use for**: Development workflow, moderate debugging
- **Example output**: Test setup messages, database operations, API requests

### WARNING (Default)

- **Shows**: Warnings, important messages, test results
- **Use for**: CI/CD, clean test runs, minimal noise
- **Example output**: Deprecation warnings, test skips, basic progress

### ERROR

- **Shows**: Only error messages and test failures
- **Use for**: Focus on failures only
- **Example output**: Exception traces, test errors

### CRITICAL

- **Shows**: Only critical system errors
- **Use for**: Production monitoring, severe issues only
- **Example output**: Application crashes, critical failures

## Usage Methods

### 1. CLI Flags (Recommended)

Use pytest's built-in log level flags:

```bash
# Basic log level control
pytest --log-level=DEBUG
pytest --log-level=INFO  
pytest --log-level=WARNING

# With hatch (recommended)
hatch run pytest --log-level=DEBUG
hatch run pytest --log-level=INFO

# Live log output during test execution
hatch run pytest --log-cli-level=DEBUG -s
hatch run pytest --log-cli-level=INFO -v
```

### 2. Convenient Hatch Scripts

Pre-configured scripts for common scenarios:

```bash
# Debug testing with detailed logs
hatch run test-debug
# Equivalent to: pytest --log-cli-level=DEBUG

# Quiet testing with minimal output
hatch run test-quiet  
# Equivalent to: pytest --log-cli-level=WARNING

# Default testing (INFO level in most scripts)
hatch run test
```

### 3. Environment Variables (Legacy)

Still supported for backward compatibility:

```powershell
# PowerShell
$env:REVIEWPOINT_LOG_LEVEL = 'DEBUG'
hatch run pytest

# Bash/Linux
export REVIEWPOINT_LOG_LEVEL=DEBUG
hatch run pytest
```

## Practical Examples

### Debugging a Failing Test

```bash
# Run specific test with detailed logs
hatch run pytest tests/test_auth.py::test_login_failure --log-level=DEBUG -s

# Debug database issues
hatch run pytest tests/test_user_creation.py --log-level=DEBUG -v
```

### Development Workflow

```bash
# Balanced output for active development
hatch run pytest --log-level=INFO tests/

# Quick feedback with minimal noise
hatch run test-quiet tests/test_api/
```

### CI/CD Pipeline

```bash
# Minimal output for clean CI logs
hatch run pytest --log-level=WARNING

# Or use the quiet script
hatch run test-quiet
```

## Technical Implementation

The log level control works through:

1. **Default Setting**: WARNING level set in `conftest.py` for minimal noise
2. **CLI Detection**: `pytest_configure` function detects `--log-level` and `--log-cli-level` flags
3. **Environment Override**: CLI flags automatically set `REVIEWPOINT_LOG_LEVEL` environment variable
4. **Application Config**: The application's logging system respects the environment variable

### Key Features

- **No Manual Environment Setup**: CLI flags are automatically converted to environment variables
- **Backward Compatible**: Still supports manual environment variable setting
- **Fast/Slow Mode Compatible**: Works with both SQLite (fast) and PostgreSQL (slow) test modes
- **Hatch Integration**: Convenient scripts for common log levels

## Troubleshooting

### Common Issues

**Issue**: Log level changes don't take effect
**Solution**: Ensure you're using the CLI flags correctly and not overriding with environment variables

**Issue**: Too much output even with WARNING level
**Solution**: Some third-party libraries may log at WARNING level; use ERROR level for minimal output

**Issue**: Not seeing expected debug information
**Solution**: Use `--log-cli-level=DEBUG -s` for live output or check that the application code is using the logger correctly

### Getting Help

- Check the current log level: Look for `[ENV_SETUP]` messages in test output
- Verify CLI flag parsing: Run with `-v` to see pytest configuration
- Review test configuration: See `backend/tests/conftest.py` for implementation details

## Related Documentation

- [Test Instructions](test-instructions.md) - General testing guide
- [Development Guidelines](dev-guidelines.md) - Development workflow
- [Backend Testing Guide](backend/TESTING.md) - Comprehensive testing documentation
