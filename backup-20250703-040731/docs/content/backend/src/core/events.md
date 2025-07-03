<!-- filepath: c:\Users\00010654\Documents\Git\ReViewPoint\docs\backend\core\events.md -->

# `core/events.py`

| Item               | Value                                                            |
| ------------------ | ---------------------------------------------------------------- |
| **Layer**          | Core                                                             |
| **Responsibility** | (Stub) Intended for application startup and shutdown event hooks |
| **Status**         | 🟢 DONE                                                          |

## 1. Purpose

This file is a placeholder for FastAPI event hooks. It will register functions to run on app startup and shutdown for resource initialization and cleanup.

## 2. Public API

- `async def on_startup() -> None`: FastAPI startup event handler. Initializes logging, validates configuration, checks DB health, logs pool stats, and (optionally) initializes cache. Logs all steps and errors with loguru.
- `async def on_shutdown() -> None`: FastAPI shutdown event handler. Gracefully disposes DB connections, releases resources, and logs shutdown steps and errors.
- `async def db_healthcheck() -> None`: Runs a DB health check query, raising on failure.
- `async def validate_config() -> None`: Validates required environment variables and config logic, raising on failure.

## 3. Behaviour & Edge-Cases

- **Startup**: Fails fast and logs error if config is invalid or DB is unreachable. Logs pool stats if available. All errors are logged with actionable messages.
- **Shutdown**: Cleans up DB connections and resources, logs all steps. Errors during shutdown are logged.
- **Error Handling**: All exceptions are logged with loguru and re-raised to prevent invalid app state.
- **Health Endpoint**: `/api/v1/health` uses `db_healthcheck` for runtime DB monitoring and returns response time.

## 4. Dependencies

- **Internal**: `core/config.py`, `core/database.py`, `core/logging.py` (and optionally cache module)
- **External**: `loguru`, `sqlalchemy`, `fastapi`

## 5. Tests

| Test file                        | Scenario                                 |
| -------------------------------- | ---------------------------------------- |
| `tests/core/test_events.py`      | Startup/shutdown: valid, invalid, DB down|
| `tests/api/v1/test_health.py`    | Health endpoint: healthy, DB error       |

- Uses `pytest`, `pytest-asyncio`, monkeypatching, and loguru sink fixtures.
- >80% coverage for all event handler branches.

## 6. Open TODOs

- [x] Implement startup and shutdown event hooks
- [x] Add runtime health endpoint
- [x] Add comprehensive tests and error handling

> **This page is now up to date with the current implementation.**
