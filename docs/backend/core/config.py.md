# `core/config.py`

| Item | Value |
|------|-------|
| **Layer** | Core |
| **Responsibility** | Provide a **singleton Settings object** that reads environment variables / `.env`, performs type-safe validation and exposes helper properties used across the entire backend. |
| **Status** | 🔴 TODO |
| **Owner** | @filip |

---

## 1. Purpose
Create a single source-of-truth for runtime configuration:
* Centralise all tunables (DB URL, JWT secret, log level …) in one file.
* Fail fast on missing or malformed critical values.
* Offer convenient helper properties (e.g. `async_db_url`, `upload_path`) that other modules import instead of hand-crafting strings.
* Ensure deterministic overrides for tests via `Settings(testing=True, **overrides)`.

## 2. Public API

| Symbol | Type | Description |
|--------|------|-------------|
| `Settings` | class | Subclass of `pydantic_settings.BaseSettings`; holds all config fields. |
| `get_settings()` | function | `@lru_cache` factory that returns a **singleton** instance of `Settings`. |
| `settings` | variable | Shortcut alias: `settings = get_settings()` so callers can simply `from core.config import settings`. |

### Constants (internal, but documented)

| Name | Description |
|------|-------------|
| `ENV_PREFIX` | Prefix for ENV overrides (defaults to `REVIEWPOINT_`). |

## 3. Behaviour & Edge-Cases
- Reads `.env` automatically, but real env vars win (12-factor rule).
- Critical secrets (`jwt_secret`, database password) are marked `repr=False` so they never appear in logs.
- If `environment == "test"` → force an in-memory SQLite URL and lower log level to WARNING.
- URL validation with `@field_validator` – only `postgresql+asyncpg://` or `sqlite+aiosqlite://` accepted.
- Derived helpers are lazily evaluated properties to avoid compute on startup.
- Raises `RuntimeError` on missing mandatory fields *before* FastAPI app boots.
- Uses `SettingsConfigDict(env_prefix=ENV_PREFIX)` for clear namespacing.
- Supports nested JSON values via `pydantic.Json` for complex flags.
- Protects against accidental double-instantiation with `@lru_cache`.

## 4. Dependencies
- `pydantic-settings` v2 (for BaseSettings)
- `functools.lru_cache`
- Standard lib `pathlib.Path`

## 5. Tests

| Test file | Scenario |
|-----------|----------|
| `tests/core/test_config_env_loading.py` | `.env` vs. real env precedence |
| `tests/core/test_config_missing_values.py` | Missing `JWT_SECRET` raises ValidationError |
| `tests/core/test_config_derived.py` | `settings.async_db_url` returns expected postfix |
| `tests/core/test_config_repr.py` | `repr(settings)` doesn’t leak secrets |

## 6. Open TODOs
- [ ] Implement `Settings` class with all fields listed in the roadmap.
- [ ] Add helper `to_public_dict()` that filters secrets for docs.
- [ ] Wire automatic log-level adjustment based on `debug` flag.
