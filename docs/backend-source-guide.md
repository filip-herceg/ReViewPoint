<!-- docs/backend/backend-source-guide.md  – Backend Gateway -->
# Backend Source Guide 🐍

One-liners for every source file plus a link to its detailed spec page.

| Layer | File | Responsibility (1-liner) |
|-------|------|--------------------------|
| Core | [`core/config.py`](file-details/core-config.md) | Global settings singleton |
|  | [`core/database.py`](file-details/core-database.md) | Async SQLAlchemy engine & session factory |
|  | [`core/logging.py`](file-details/core-logging.md) | Central logger bootstrap |
|  | [`core/security.py`](file-details/core-security.md) | JWT + password hashing helpers |
|  | [`core/events.py`](file-details/core-events.md) | Startup / shutdown hooks |
| Models | [`models/base.py`](file-details/models-base.md) | Declarative base class |
|  | [`models/user.py`](file-details/models-user.md) | `User` table schema |
|  | [`models/file.py`](file-details/models-file.md) | `File` upload metadata table |
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
| Entry | [`main.py`](file-details/main.md) | FastAPI app entrypoint |

_Add new rows when you add new files. Keep descriptions to one concise sentence._
