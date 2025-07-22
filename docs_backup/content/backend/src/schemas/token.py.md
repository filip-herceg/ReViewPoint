# `schemas/token.py`

| Item               | Value                                         |
| ------------------ | --------------------------------------------- |
| **Layer**          | Schemas                                       |
| **Responsibility** | Pydantic models for JWT and token-related API |
| **Status**         | 🟢 Implemented                                |

## 1. Purpose

Defines Pydantic models for JWT and token responses (access, refresh, etc.).

## 2. Public API

- `TokenResponse`, `RefreshTokenRequest`, etc.

## 3. Behaviour & Edge-Cases

- All fields validated by Pydantic
- Used by FastAPI for request/response validation

## 4. Dependencies

- **External**: Pydantic

## 5. Tests

- Covered indirectly by API endpoint tests
