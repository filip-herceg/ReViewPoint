# `schemas/user.py`

| Item               | Value                                |
| ------------------ | ------------------------------------ |
| **Layer**          | Schemas                              |
| **Responsibility** | Pydantic models for user-related API |
| **Status**         | 🟢 Implemented                       |

## 1. Purpose

Defines Pydantic models for user endpoints (profile, update, etc.).

## 2. Public API

- `UserProfile`, `UserUpdateRequest`, etc.

## 3. Behaviour & Edge-Cases

- All fields validated by Pydantic
- Used by FastAPI for request/response validation

## 4. Dependencies

- **External**: Pydantic

## 5. Tests

- Covered indirectly by API endpoint tests
