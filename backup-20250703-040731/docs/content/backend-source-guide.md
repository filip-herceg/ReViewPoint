<!-- docs/backend-source-guide.md  – Backend Gateway -->

# Backend Source Guide

This guide provides an overview of the backend source code structure, conventions, and best practices for the ReViewPoint project.

## Directory Structure

- `src/` — Main backend source code
- `src/api/` — API endpoint implementations
- `src/models/` — Database models and schemas
- `src/utils/` — Utility modules (hashing, validation, etc.)
- `src/repositories/` — Data access and repository logic
- `src/services/` — Business logic and service layer
- `src/middlewares/` — Middleware for request/response processing
- `tests/` — Backend test suite

## Key Conventions

- Follows PEP8 and project-specific linting rules
- Uses dependency injection for services and repositories
- All API endpoints are versioned (e.g., `/api/v1/`)
- Error handling is centralized and consistent

## Running Backend Tests

To run backend tests:

```sh
hatch run test
```

Or use your preferred test runner (e.g., pytest).

## Related Documentation

- [API Reference](api-reference.md)
- [Backend Models](src/models/README.md)
- [Backend Utilities](src/utils/README.md)
- [Backend Tests](backend/tests/README.md)

---

*Update this guide as the backend evolves to keep documentation accurate and helpful.*
