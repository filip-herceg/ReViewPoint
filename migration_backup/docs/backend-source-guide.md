<!-- docs/backend-source-guide.md  – Backend Gateway -->
# Backend Source Guide

> **This guide merges the previous File Overview and Test Instructions for clarity and ease of use.**

---

## Quick Links

- [Architecture](architecture.md)  
  *High-level system design & component diagram*
- [CI/CD](ci-cd.md)  
  *Build-and-deploy pipeline details*
- [Developer Guidelines](dev-guidelines.md)  
  *Coding style, branching, commit rules*
- [Module Guide](module-guide.md)  
  *How to create / integrate new modules*
- [LLM Integration](llm-integration.md)  
  *External & internal LLM setups*
- [Setup](setup.md)  
  *Local dev environment bootstrap*

---

## Backend File Responsibilities

| Layer        | File                        | Responsibility (1-liner)                |
|--------------|-----------------------------|-----------------------------------------|
| Core         | [core/config.py](backend/core/config.py.md)            | Global settings singleton               |
|              | [core/database.py](backend/core/database.py.md)          | Async SQLAlchemy engine & session factory |
|              | [core/logging.py](backend/core/logging.py.md)           | Central logger bootstrap                |
|              | [core/security.py](backend/core/security.py.md)          | JWT + password hashing helpers          |
|              | [core/events.py](backend/core/events.md)            | Startup / shutdown hooks                |
| Models       | [models/base.py](backend/models/base.py.md)            | Declarative base class                  |
|              | [models/user.py](backend/models/user.py.md)            | `User` table schema                     |
|              | [models/file.py](backend/models/file.py.md)            | `File` upload metadata table            |
| Repositories | [repositories/user.py](backend/repositories/user.py.md)      | CRUD & queries for users                |
|              | [repositories/file.py](backend/repositories/file.py.md)      | CRUD for uploaded files                 |
| Services     | [services/user.py](backend/services/user.py.md)          | Registration & auth logic               |
|              | [services/upload.py](backend/services/upload.py.md)        | File-upload workflow                    |
| API          | [api/deps.py](backend/api/deps.py.md)               | Dependency-injection helpers            |
|              | [api/v1/auth.py](backend/api/v1/auth.py.md)            | `/auth/*` endpoints                     |
|              | [api/v1/uploads.py](backend/api/v1/uploads.py.md)         | `/uploads/*` endpoints                  |
| Middleware   | [middlewares/logging.py](backend/middlewares/logging.py.md)    | Request/response logger                 |
| Utils        | [utils/hashing.py](backend/utils/hashing.py.md)          | Thin passlib wrapper                    |
|              | [utils/file.py](backend/utils/file.py.md)             | File-path helpers                       |
| Migrations   | [alembic_migrations/env.py](backend/alembic_migrations/env.py.md)            | Alembic configuration for database migrations |
|              | [alembic_migrations/versions/...](backend/alembic_migrations/versions/initial_migration.md)      | Initial schema creation                 |
| Entry        | [main.py](backend/main.py.md)                   | FastAPI app entrypoint                  |
| Tests        | [tests/conftest.py](backend/tests/conftest.md)         | Test fixtures and setup                 |
|              | [tests/core/test_database.py](backend/tests/core/database_tests.md) | Database connectivity and session tests |
|              | [tests/models/test_*.py](backend/tests/models/model_tests.md)    | Model CRUD and relationship tests       |

_Add new rows when you add new files. Keep descriptions to one concise sentence._

---

## Running Backend Tests

**All Tests**
```shell
poetry run pytest
```

**With Coverage Report**
```shell
poetry run pytest --cov=backend --cov-report=term --cov-report=xml
```

**Specific Tests (Async/API)**
```shell
poetry run pytest backend/tests/core/test_database.py
poetry run pytest backend/tests/middlewares/test_logging.py
```

- All async and API tests are auto-discovered in `backend/tests/`.
- Coverage configuration is in `pyproject.toml` under `[tool.coverage]`.
- Minimum coverage target is 80%.

**Troubleshooting**
- If you encounter import errors, ensure you are in the correct Poetry shell and your dependencies are installed.
- For more details, see [dev-guidelines.md](dev-guidelines.md).
