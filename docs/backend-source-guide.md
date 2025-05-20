<!-- docs/backend/backend-source-guide.md  – Backend Gateway -->
# Backend Source Guide 🐍

One-liners for every source file plus a link to its detailed spec page.

| Layer | File | Responsibility (1-liner) |
|-------|------|--------------------------|
| Core | [`core/config.py`](file-details/core-config.md) | Global settings singleton |
|  | [`core/database.py`](backend/core/database.py.md) | Async SQLAlchemy engine & session factory |
|  | [`core/logging.py`](file-details/core-logging.md) | Central logger bootstrap |
|  | [`core/security.py`](file-details/core-security.md) | JWT + password hashing helpers |
|  | [`core/events.py`](file-details/core-events.md) | Startup / shutdown hooks |
| Models | [`models/base.py`](backend/models/base.py.md) | Declarative base class |
|  | [`models/user.py`](backend/models/user.py.md) | `User` table schema |
|  | [`models/file.py`](backend/models/file.py.md) | `File` upload metadata table |
| Repositories | [`repositories/user.py`](file-details/repositories-user.md) | CRUD & queries for users |
|  | [`repositories/file.py`](file-details/repositories-file.md) | CRUD for uploaded files |
| Services | [`services/user.py`](file-details/services-user.md) | Registration & auth logic |
|  | [`services/upload.py`](file-details/services-upload.md) | File-upload workflow |
| API | [`api/deps.py`](file-details/api-deps.md) | Dependency-injection helpers |
|  | [`api/v1/auth.py`](file-details/api-auth.md) | `/auth/*` endpoints |
|  | [`api/v1/uploads.py`](file-details/api-uploads.md) | `/uploads/*` endpoints |
| Middleware | [`middlewares/logging.py`](file-details/middlewares-logging.md) | Request/response logger |
| Utils | [`utils/hashing.py`](file-details/utils-hashing.md) | Thin passlib wrapper |
|  | [`utils/file.py`](file-details/utils-file.md) | File-path helpers |
| Migrations | [`alembic/env.py`](backend/alembic/env.py.md) | Alembic configuration for database migrations |
|  | [`alembic/versions/...`](backend/alembic/versions/initial_migration.md) | Initial schema creation |
| Entry | [`main.py`](file-details/main.md) | FastAPI app entrypoint |
| Tests | [`tests/conftest.py`](backend/tests/conftest.md) | Test fixtures and setup |
|  | [`tests/core/test_database*.py`](backend/tests/core/database_tests.md) | Database connectivity and session tests |
|  | [`tests/models/test_*.py`](backend/tests/models/model_tests.md) | Model CRUD and relationship tests |

_Add new rows when you add new files. Keep descriptions to one concise sentence._
