# `core/config.py`

| Item               | Value                                                                                                                                            |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Layer**          | Core                                                                                                                                             |
| **Responsibility** | Provides a singleton Settings object that reads environment variables, validates types, and exposes helper properties for backend configuration. |
| **Status**         | 🟢 Done                                                                                                                                          |

## 1. Purpose

Centralizes all runtime configuration for the backend, loading from environment variables or `.env` files, and providing type-safe access to settings like DB URL, JWT secret, and log level.

## 2. Public API

| Symbol               | Type        | Description                                                                            |
| -------------------- | ----------- | -------------------------------------------------------------------------------------- |
| `Settings`           | class       | Subclass of `pydantic_settings.BaseSettings`; holds all config fields                  |
| `get_settings()`     | function    | `@lru_cache` factory that returns a singleton instance of `Settings`                   |
| `settings`           | variable    | Shortcut alias: `settings = get_settings()` for easy import                            |
| `auth_enabled`       | bool        | Enable or disable authentication features (env: REVIEWPOINT_AUTH_ENABLED)              |
| `jwt_secret_key`     | str         | Secret key for JWT signing (env: REVIEWPOINT_JWT_SECRET_KEY)                           |
| `jwt_algorithm`      | str         | JWT signing algorithm (env: REVIEWPOINT_JWT_ALGORITHM)                                 |
| `jwt_expire_minutes` | int         | JWT expiration in minutes (env: REVIEWPOINT_JWT_EXPIRE_MINUTES)                        |
| `jwt_secret`         | str \| None | [DEPRECATED] Use `jwt_secret_key` instead. Still supported for backward compatibility. |

## 3. Behaviour & Edge-Cases

- Reads `.env` automatically, but real env vars take precedence.
- Fails fast on missing or malformed critical values.
- Provides helper properties (e.g., `async_db_url`, `upload_path`).
- Supports deterministic overrides for tests.
- Uses `SettingsConfigDict(env_prefix=ENV_PREFIX)` for namespacing.
- Protects against accidental double-instantiation with `@lru_cache`.
- If `jwt_secret_key` is not set but `jwt_secret` is, the latter is used for backward compatibility.
- Auth can be toggled on/off via `auth_enabled`.

## 4. Dependencies

- **Internal**: None
- **External**:
  - `pydantic-settings` (for BaseSettings)
  - `functools.lru_cache`
  - `pathlib.Path`

## 5. Tests

| Test file                           | Scenario                                            |
| ----------------------------------- | --------------------------------------------------- |
| `backend/tests/core/test_config.py` | Tests config loading, overrides, and error handling |

## 6. Open TODOs

- [ ] Add support for dynamic reload of settings
- [ ] Document all config fields in detail

## Authentication Toggle

The system supports completely disabling authentication for development and testing purposes.

### Usage

Set the environment variable:

```bash
# Disable authentication
$env:REVIEWPOINT_AUTH_ENABLED = "false"  # PowerShell

# Enable authentication (default)
$env:REVIEWPOINT_AUTH_ENABLED = "true"
```

### Behavior When Disabled

- All JWT token validation is bypassed
- Protected endpoints return a default development admin user
- Warning logs are generated to prevent accidental use in production
- Token creation still works but is not required for access

### Security Warning

**Never disable authentication in production environments.** This feature is intended for development and testing only.

> **Update this page whenever the implementation changes.**
