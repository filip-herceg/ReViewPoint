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
| Core         | `core/config.py`            | Global settings singleton               |
|              | `core/database.py`          | Async SQLAlchemy engine & session factory |
|              | `core/logging.py`           | Central logger bootstrap                |
|              | `core/security.py`          | JWT + password hashing helpers          |
|              | `core/events.py`            | Startup / shutdown hooks                |
| Models       | `models/base.py`            | Declarative base class                  |
|              | `models/user.py`            | `User` table schema                     |
|              | `models/file.py`            | `File` upload metadata table            |
| Repositories | `repositories/user.py`      | CRUD & queries for users                |
|              | `repositories/file.py`      | CRUD for uploaded files                 |
| Services     | `services/user.py`          | Registration & auth logic               |
|              | `services/upload.py`        | File-upload workflow                    |
| API          | `api/deps.py`               | Dependency-injection helpers            |
|              | `api/v1/auth.py`            | `/auth/*` endpoints                     |
|              | `api/v1/uploads.py`         | `/uploads/*` endpoints                  |
| Middleware   | `middlewares/logging.py`    | Request/response logger                 |
| Utils        | `utils/hashing.py`          | Thin passlib wrapper                    |
|              | `utils/file.py`             | File-path helpers                       |
| Migrations   | `alembic/env.py`            | Alembic configuration for database migrations |
|              | `alembic/versions/...`      | Initial schema creation                 |
| Entry        | `main.py`                   | FastAPI app entrypoint                  |
| Tests        | `tests/conftest.py`         | Test fixtures and setup                 |
|              | `tests/core/test_database.py`| Database connectivity and session tests |
|              | `tests/models/test_*.py`    | Model CRUD and relationship tests       |

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
