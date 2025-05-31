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
| Core         | [backend/src/core/config.py.md](backend/src/core/config.py.md)            | Global settings singleton               |
|              | [backend/src/core/database.py.md](backend/src/core/database.py.md)          | Async SQLAlchemy engine & session factory |
|              | [backend/src/core/logging.py.md](backend/src/core/logging.py.md)           | Central logger bootstrap                |
|              | [backend/src/core/security.py.md](backend/src/core/security.py.md)          | JWT + password hashing helpers          |
|              | [backend/src/core/events.md](backend/src/core/events.md)            | Startup / shutdown hooks                |
| Models       | [backend/src/models/base.py.md](backend/src/models/base.py.md)            | Declarative base class                  |
|              | [backend/src/models/user.py.md](backend/src/models/user.py.md)            | `User` table schema                     |
|              | [backend/src/models/file.py.md](backend/src/models/file.py.md)            | `File` upload metadata table            |
| Repositories | [backend/src/repositories/user.py.md](backend/src/repositories/user.py.md)      | CRUD & queries for users                |
|              | [backend/src/repositories/file.py.md](backend/src/repositories/file.py.md)      | CRUD for uploaded files                 |
| Services     | [backend/src/services/user.py.md](backend/src/services/user.py.md)          | Registration & auth logic               |
|              | [backend/src/services/upload.py.md](backend/src/services/upload.py.md)        | File-upload workflow                    |
| API          | [backend/src/api/deps.py.md](backend/src/api/deps.py.md)               | Dependency-injection helpers            |
|              | [backend/src/api/v1/auth.py.md](backend/src/api/v1/auth.py.md)            | `/auth/*` endpoints                     |
|              | [backend/src/api/v1/uploads.py.md](backend/src/api/v1/uploads.py.md)         | `/uploads/*` endpoints                  |
| Middleware   | [backend/src/middlewares/logging.py.md](backend/src/middlewares/logging.py.md)    | Request/response logger                 |
| Utils        | [backend/src/utils/hashing.py.md](backend/src/utils/hashing.py.md)          | Thin passlib wrapper                    |
|              | [backend/src/utils/file.py.md](backend/src/utils/file.py.md)             | File-path helpers                       |
| Migrations   | [backend/src/alembic/env.py.md](backend/src/alembic/env.py.md)            | Alembic configuration for database migrations |
|              | [backend/src/alembic/versions/initial_migration.md](backend/src/alembic/versions/initial_migration.md)      | Initial schema creation                 |
| Entry        | main.py.md                   | FastAPI app entrypoint                  |
| Tests        | [backend/tests/conftest.md](backend/tests/conftest.md)         | Test fixtures and setup                 |
|              | [backend/tests/core/database_tests.md](backend/tests/core/database_tests.md) | Database connectivity and session tests |
|              | [backend/tests/models/model_tests.md](backend/tests/models/model_tests.md)    | Model CRUD and relationship tests       |

_Add new rows when you add new files. Keep descriptions to one concise sentence._

---

## Running Backend Tests

**All Tests**
```shell
hatch run pytest
```

**With Coverage Report**
```shell
hatch run pytest --cov=backend --cov-report=term --cov-report=xml
```

**Specific Tests (Async/API)**
```shell
hatch run pytest backend/tests/core/test_database.py
hatch run pytest backend/tests/middlewares/test_logging.py
```

- All async and API tests are auto-discovered in `backend/tests/`.
- Coverage configuration is in `pyproject.toml` under `[tool.coverage]`.
- Minimum coverage target is 80%.

**Troubleshooting**
- If you encounter import errors, ensure you are in the correct Hatch environment and your dependencies are installed.
- For more details, see [dev-guidelines.md](dev-guidelines.md).
