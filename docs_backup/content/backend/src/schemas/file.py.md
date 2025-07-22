# `schemas/file.py`

| Item               | Value                                        |
| ------------------ | -------------------------------------------- |
| **Layer**          | Schemas                                      |
| **Responsibility** | Pydantic models for file upload/download API |
| **Status**         | 🟢 Implemented                               |

## 1. Purpose

Defines Pydantic models for file upload/download endpoints. Ensures type safety and validation for file metadata and requests.

## 2. Public API

- `FileUploadRequest`, `FileMetadataResponse`, etc.

## 3. Behaviour & Edge-Cases

- All fields validated by Pydantic
- Used by FastAPI for request/response validation

## 4. Dependencies

- **External**: Pydantic

## 5. Tests

- Covered indirectly by API endpoint tests
