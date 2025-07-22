# Backend Test Suite Documentation

This document provides an overview of the backend test suite for the ReViewPoint project.

## Purpose

The backend test suite ensures the reliability, correctness, and security of all backend modules, including API endpoints, models, utilities, and services.

## Structure

- **api/** — Tests for API endpoints (e.g., user, auth, uploads)
- **models/** — Tests for database models
- **repositories/** — Tests for repository/data access logic
- **services/** — Tests for business logic and service layer
- **utils/** — Tests for utility modules (hashing, validation, etc.)
- **middlewares/** — Tests for middleware components

## Best Practices

- Use descriptive test names and docstrings
- Test both typical and edge cases
- Mock external dependencies where appropriate
- Ensure tests are isolated and repeatable
- Maintain high code coverage

## Running Tests

Run all backend tests with:

```sh
hatch run test
```

Or use `pytest` directly if preferred.

### Controlling Log Levels

You can control the verbosity of test output using pytest CLI flags:

```sh
# Default minimal output (WARNING level)
hatch run pytest

# Debug level for detailed troubleshooting
hatch run pytest --log-level=DEBUG

# Info level for development
hatch run pytest --log-level=INFO

# Convenient scripts
hatch run test-debug    # DEBUG with live output
hatch run test-quiet    # WARNING (minimal)
```

Available log levels: DEBUG, INFO, WARNING (default), ERROR, CRITICAL

## Related Documentation

- [Backend Source Guide](../../backend-source-guide.md)
- [API Reference](../../api-reference.md)
- [Backend Utilities](../../src/utils/README.md)

---

*Keep this document up to date as the test suite evolves.*
