<!-- filepath: c:\Users\00010654\Documents\Git\ReViewPoint\docs\backend\core\logging.py.md -->
# `core/logging.py`

| Item | Value |
|------|-------|
| **Layer** | Core |
| **Responsibility** | Sets up and configures the application's logging system, providing colorized and JSON log formatting, and safe re-initialization. |
| **Status** | 🟢 Done |

## 1. Purpose  
Provides a repeat-safe logging initializer for the backend, supporting both human-readable and JSON log formats, color output, and file logging. Ensures consistent logging across all modules and environments.

## 2. Public API  

| Symbol | Type | Description |
|--------|------|-------------|
| `init_logging` | function | Initializes root logger with color/JSON/file options |
| `ColorFormatter` | class | Formatter for colorized, single-line log output |
| `JsonFormatter` | class | Formatter for JSON Lines log output |

## 3. Behaviour & Edge-Cases  
- Calling `init_logging` multiple times is safe; only handlers created by this module are purged and replaced.
- Supports both colorized and JSON log output, selectable via arguments.
- File logging is optional and will create parent directories as needed.
- All log output is formatted consistently, including for third-party handlers (e.g., pytest caplog).
- Uvicorn access logs are not propagated to avoid duplicate logging.

## 4. Dependencies  
- **Internal**: None
- **External**:
  - `logging` (standard library)
  - `sys`, `pathlib.Path`, `datetime`, `json` (standard library)

## 5. Tests  
| Test file | Scenario |
|-----------|----------|
| `backend/tests/middlewares/test_logging.py` | Indirectly verifies logging output via middleware tests |

## 6. Open TODOs  
- [ ] Add log rotation support for file handlers
- [ ] Expose log level and format via environment/config

> **Update this page whenever the implementation changes.**
