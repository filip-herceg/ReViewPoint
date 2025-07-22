# `schemas/auth.py`

| Item               | Value                                                                 |
| ------------------ | --------------------------------------------------------------------- |
| **Layer**          | Schemas                                                               |
| **Responsibility** | Pydantic models for authentication-related API requests and responses |
| **Status**         | 🟢 Implemented                                                        |

## 1. Purpose

Defines Pydantic models for authentication endpoints (register, login, password reset, etc.). Ensures type safety and validation for incoming/outgoing data.

## 2. Public API

- `RegisterRequest`, `LoginRequest`, `PasswordResetRequest`, etc.: request models
- `TokenResponse`, `UserProfileResponse`, etc.: response models

## 3. Behaviour & Edge-Cases

- All fields validated by Pydantic
- Used by FastAPI for request/response validation

## 4. Dependencies

- **External**: Pydantic

## 5. Tests

- Covered indirectly by API endpoint tests
