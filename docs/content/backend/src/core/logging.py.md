<!-- filepath: c:\Users\00010654\Documents\Git\ReViewPoint\docs\backend\core\logging.py.md -->
# `core/logging.py`

| Item | Value |
|------|-------|
| **Layer** | Core |
| **Responsibility** | Sets up and configures the application's logging system using [loguru](https://loguru.readthedocs.io/), providing colorized and JSON log formatting, and safe re-initialization. |
| **Status** | 🟢 Done |

## 1. Purpose  
Provides a repeat-safe logging initializer for the backend, supporting both human-readable and JSON log formats, color output, and file logging. Ensures consistent logging across all modules and environments.

## 2. Public API  

| Symbol | Type | Description |
|--------|------|-------------|
| `init_logging` | function | Initializes loguru as the main logger with color/JSON/file options |

> **Note:** As of May 2025, all logging is handled via [loguru](https://loguru.readthedocs.io/). Use `from loguru import logger` in all backend modules. The previous `ColorFormatter` and `JsonFormatter` are deprecated and no longer used.

## 3. Behaviour & Edge-Cases  
- Calling `init_logging` multiple times is safe; only handlers created by this module are purged and replaced.
- Supports both colorized and JSON log output, selectable via arguments.
- File logging is optional and will create parent directories as needed.
- All log output is handled by loguru, which supports structured logging, color, and JSON output natively.
- Standard logging calls are patched to route through loguru for compatibility.
- Uvicorn access logs are not propagated to avoid duplicate logging.

## 4. Dependencies  
- **Internal**: None
- **External**:
  - `loguru` (third-party)
  - `logging` (standard library, patched for compatibility)
  - `sys`, `pathlib.Path` (standard library)

## 5. Tests  
| Test file | Scenario |
|-----------|----------|
| `backend/tests/middlewares/test_logging.py` | Indirectly verifies logging output via middleware tests |

## 6. Security Considerations
- All authentication events (register, login, logout, password reset, failures) are logged using loguru with structured context.
- Sensitive data such as passwords and tokens are never logged.
- Middleware and service logging filter sensitive fields from logs.
- Tests verify that no secrets are leaked in logs.

## 7. Migration Notes
- All modules should use `from loguru import logger` instead of `logging.getLogger()`.
- Example usage:
  ```python
  from loguru import logger
  logger.info("message")
  ```
- Standard logging calls will still work but are routed through loguru.
- When adding new authentication or sensitive endpoints, ensure no secrets are ever logged and add/extend tests as needed.

> **Update this page whenever the implementation changes.**

## 8. Open TODOs  
- [ ] Add log rotation support for file handlers
- [ ] Expose log level and format via environment/config
