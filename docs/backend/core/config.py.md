# `core/config.py`

| Item | Value |
|------|-------|
| **Layer** | Core |
| **Responsibility** | Provides a singleton Settings object that reads environment variables, validates types, and exposes helper properties for backend configuration. |
| **Status** | 🟢 Done |

## 1. Purpose  
Centralizes all runtime configuration for the backend, loading from environment variables or `.env` files, and providing type-safe access to settings like DB URL, JWT secret, and log level.

## 2. Public API  
| Symbol | Type | Description |
|--------|------|-------------|
| `Settings` | class | Subclass of `pydantic_settings.BaseSettings`; holds all config fields |
| `get_settings()` | function | `@lru_cache` factory that returns a singleton instance of `Settings` |
| `settings` | variable | Shortcut alias: `settings = get_settings()` for easy import |

## 3. Behaviour & Edge-Cases  
- Reads `.env` automatically, but real env vars take precedence.
- Fails fast on missing or malformed critical values.
- Provides helper properties (e.g., `async_db_url`, `upload_path`).
- Supports deterministic overrides for tests.
- Uses `SettingsConfigDict(env_prefix=ENV_PREFIX)` for namespacing.
- Protects against accidental double-instantiation with `@lru_cache`.

## 4. Dependencies  
- **Internal**: None
- **External**:
  - `pydantic-settings` (for BaseSettings)
  - `functools.lru_cache`
  - `pathlib.Path`

## 5. Tests  
| Test file | Scenario |
|-----------|----------|
| `backend/tests/core/test_config.py` | Tests config loading, overrides, and error handling |

## 6. Open TODOs  
- [ ] Add support for dynamic reload of settings
- [ ] Document all config fields in detail

> **Update this page whenever the implementation changes.**
