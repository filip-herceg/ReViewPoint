<!-- docs/backend-source-guide.md  – Backend Gateway -->

# Backend Source Guide

<!-- anchor: running-backend-tests -->

> **This guide provides a complete, navigable, and layered overview of the backend codebase.**

---

## Navigation

- [Architecture](architecture.md)
- [Setup Guide](setup.md)
- [Development Guidelines](dev-guidelines.md)
- [CI/CD](ci-cd.md)
- [Module Guide](module-guide.md)
- [LLM Integration](llm-integration.md)

---

## Backend Structure Overview

### Backend

#### Directory Map & Roles

- **alembic_migrations/**: Database migration scripts and versioning
- **api/**: All API endpoints and dependency injection
- **core/**: Core configuration, database, logging, security, and events
- **middlewares/**: Request/response middleware (e.g., logging)
- **models/**: SQLAlchemy ORM models (database tables)
- **repositories/**: Data access and CRUD logic
- **schemas/**: Pydantic models for API validation
- **services/**: Business logic for users, uploads, etc.
- **utils/**: Utility helpers (hashing, file ops, validation, etc.)
- `main.py`: FastAPI app entrypoint
- `*about*.py`, `*init*.py`: Metadata and package init

#### Directory Interactions

- **api/** depends on **core/**, **services/**, **schemas/**
- **services/** use **repositories/**, **models/**, **utils/**
- **repositories/** use **models/**
- **middlewares/** and **core/logging.py** ensure consistent logging
- **alembic_migrations/** manages DB schema for **models/**

---

### Directory & File Details

### alembic_migrations/

- _Purpose_: Handles DB schema migrations
- _Files_:
  - [env.py](backend/src/alembic/env.py.md): Alembic config
  - [versions/initial_migration.py](backend/src/alembic/versions/initial_migration.md): Initial schema

### api/

- _Purpose_: API endpoints and dependency injection
- _Files_:
  - [deps.py](backend/src/api/deps.py.md): Dependency-injection helpers
  - **v1/**: Versioned API endpoints
    - [auth.py](backend/src/api/v1/auth.py.md): Auth endpoints ([test](backend/tests/api/v1/test_auth.py.md))
    - [uploads.py](backend/src/api/v1/uploads.py.md): Upload endpoints
    - [users.py](backend/src/api/v1/users.py.md): User endpoints ([test](backend/tests/api/v1/test_users.py.md))

### core/

- _Purpose_: Core backend config, DB, logging, security
- _Files_:
  - [config.py](backend/src/core/config.py.md): Settings singleton
  - [database.py](backend/src/core/database.py.md): Async DB engine ([test](backend/tests/core/database_tests.md))
  - [logging.py](backend/src/core/logging.py.md): Loguru logger
  - [security.py](backend/src/core/security.py.md): JWT/password helpers
  - [events.py](backend/src/core/events.md): Startup/shutdown hooks

### middlewares/

- _Purpose_: Middleware for requests/responses
- _Files_:
  - [logging.py](backend/src/middlewares/logging.py.md): Logging middleware ([test](backend/tests/middlewares/test_logging.py.md))

### models/

- _Purpose_: SQLAlchemy ORM models
- _Files_:
  - [base.py](backend/src/models/base.py.md): Declarative base
  - [user.py](backend/src/models/user.py.md): User table ([test](backend/tests/models/test_user.py.md))
  - [file.py](backend/src/models/file.py.md): File table ([test](backend/tests/models/test_file.py.md))

### repositories/

- _Purpose_: CRUD/data access
- _Files_:
  - [user.py](backend/src/repositories/user.py.md): User repo ([test](backend/tests/repositories/test_user.py.md))
  - [file.py](backend/src/repositories/file.py.md): File repo

### schemas/

- _Purpose_: Pydantic models for API validation
- _Files_:
  - [auth.py](backend/src/schemas/auth.py.md)
  - [file.py](backend/src/schemas/file.py.md)
  - [token.py](backend/src/schemas/token.py.md)
  - [user.py](backend/src/schemas/user.py.md)

### services/

- _Purpose_: Business logic
- _Files_:
  - [user.py](backend/src/services/user.py.md): User logic ([test](backend/tests/services/test_user.py.md))
  - [upload.py](backend/src/services/upload.py.md): Upload logic

### utils/

- _Purpose_: Utility helpers
- _Files_:
  - [hashing.py](backend/src/utils/hashing.py.md): Password hashing ([test](backend/tests/utils/test_hashing.py.md))
  - [file.py](backend/src/utils/file.py.md): File helpers
  - [cache.py](backend/src/utils/cache.py.md): Caching helpers ([test](backend/tests/utils/test_cache.py.md))
  - [errors.py](backend/src/utils/errors.py.md): Error helpers ([test](backend/tests/utils/test_errors.py.md))
  - [rate_limit.py](backend/src/utils/rate_limit.py.md): Rate limiting ([test](backend/tests/utils/test_rate_limit.py.md))
  - [validation.py](backend/src/utils/validation.py.md): Validation helpers ([test](backend/tests/utils/test_validation.py.md))
  - [**init**.py](backend/src/utils/__init__.py.md): Package marker

### main.py

- _Purpose_: FastAPI app entrypoint

### `*about*.py`, `*init*.py`

- _Purpose_: Metadata and package init

---

## Test Mapping & Coverage

- Every source file has a dedicated test file (see links above), except for stubs or files where testing is not applicable.
- All tests are in `backend/tests/` and documented in the corresponding `docs/content/backend/tests/` directory.
- Minimum 80% coverage enforced.

---

## How to Navigate

- Use the directory map above to find the area of interest.
- Click file links for detailed documentation (purpose, API, methods, tests, etc.).
- For API endpoints, see the API file docs for endpoint/method/response details.
- For test details, see the linked test `.md` files.

---

## Frontend Navigation

- For the frontend structure, see the [Frontend Overview](frontend/overview.md) and [System Architecture](architecture.md#file--directory-structure-frontend-example).

---

_This structure ensures every file is documented, mapped, and easy to find. All documentation files exist and are cross-referenced. If you add a new file, add its documentation and update this guide._
