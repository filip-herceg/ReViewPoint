<!-- filepath: c:\Users\00010654\Documents\Git\ReViewPoint\docs\backend\main.py.md -->
# `main.py`

| Item | Value |
|------|-------|
| **Layer** | Entry |
| **Responsibility** | Entrypoint for the FastAPI application; configures app, logging (via loguru), middleware, and global error handling. |
| **Status** | 🟢 Done |

## 1. Purpose  
Creates and configures the FastAPI app instance, registers routes, middleware, and event handlers, and starts the ASGI server when run directly.

## 2. Public API  
| Symbol | Type | Description |
|--------|------|-------------|
| `app` | FastAPI instance | The main FastAPI application object |

## 3. Behaviour & Edge-Cases  
- Initializes logging system using loguru before app startup.
- Adds request logging middleware for all HTTP requests (using loguru).
- Registers a global exception handler that logs all unhandled errors and returns structured JSON responses: `{ "status": "error", "feedback": "..." }`.
- Loads configuration from the singleton settings object.
- Designed to be run as `python -m backend.main` or via ASGI server.

## 4. Dependencies  
- **Internal**:
  - `backend.core.config`: For settings
  - `backend.core.logging`: For logging setup
  - `backend.middlewares.logging`: For request logging middleware
- **External**:
  - `fastapi`

## 5. Tests  
| Test file | Scenario |
|-----------|----------|
| _None yet_ | _No direct tests; covered by integration tests for API and middleware_ |

## 6. Open TODOs  
- [ ] Add startup/shutdown event hooks
- [ ] Add more detailed API documentation

> **Update this page whenever the implementation changes.**

## 7. Error Handling
- All unhandled exceptions are caught by a global exception handler, logged via loguru, and returned as structured JSON errors.
