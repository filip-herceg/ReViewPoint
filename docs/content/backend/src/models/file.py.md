# `models/file.py`

| Item               | Value                                                |
| ------------------ | ---------------------------------------------------- |
| **Layer**          | Models                                               |
| **Responsibility** | Defines the File model for document storage metadata |
| **Status**         | 🟢 Done                                              |

## 1. Purpose

This file defines the File model that tracks metadata for uploaded documents and files. It associates uploaded files with users and stores critical information about the file content without containing the actual file data (which is stored in the filesystem or object storage).

## 2. Public API

| Symbol | Type                   | Description         |
| ------ | ---------------------- | ------------------- |
| `File` | SQLAlchemy model class | File metadata model |

**File Model Fields**:

- `filename`: String(255), non-nullable
- `content_type`: String(128), non-nullable
- `user_id`: Integer, foreign key to users.id, non-nullable
- Plus inherited fields from Base: `id`, `created_at`, `updated_at`

**Relationships**:

- `user`: Many-to-one relationship to the User model

## 3. Behaviour & Edge-Cases

- `user_id` is indexed for performance in filtering files by user
- The relationship to User allows easy access to the file's user (not 'owner')
- The User model has a backref to files, allowing `user.files` access
- The model only stores metadata; actual file content is stored externally
- Content type is stored to allow proper MIME type handling when serving files

## 4. Dependencies

- **Internal**:
  - `backend.models.base`: For Base class inheritance
- **External**:
  - `sqlalchemy.orm`: For ORM mapping and relationship
  - `sqlalchemy`: For column types and constraints

## 5. Tests

| Test file                           | Scenario                       |
| ----------------------------------- | ------------------------------ |
| `backend/tests/models/test_file.py` | CRUD operations for File model |

## 6. Open TODOs

- [ ] Add additional metadata fields (size, checksum, etc.)
- [ ] Consider versioning support for file revisions
- [ ] Add file status field for processing state
