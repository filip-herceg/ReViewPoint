# `core/database.py`

| Item | Value |
|------|-------|
| **Layer** | Core |
| **Responsibility** | Async SQLAlchemy engine configuration and session management |
| **Status** | 🟢 Done |
| **Owner** | @ReViewPointTeam |

## 1. Purpose  
This file provides the database connectivity layer for the application using SQLAlchemy's async ORM. It configures database connections, manages sessions, and offers health checking functionality. The implementation supports both PostgreSQL for production and SQLite for development/testing.

## 2. Public API  

| Symbol | Type | Description |
|--------|------|-------------|
| `engine` | AsyncEngine | The configured SQLAlchemy async engine instance |
| `AsyncSessionLocal` | async_sessionmaker | Factory for creating new SQLAlchemy AsyncSession objects |
| `get_async_session` | async context manager | Dependency for FastAPI routes that provides a managed AsyncSession |
| `db_healthcheck` | async function | Checks database connectivity for health endpoints |

## 3. Behaviour & Edge-Cases  

- Connection pooling is configured differently based on environment:
  - Production: Larger pool (size=10, max_overflow=20)
  - Development: Smaller pool (size=5, max_overflow=10)
  - SQLite: No pooling (not supported by SQLite)
  
- The session context manager (`get_async_session`) provides automatic:
  - Session acquisition
  - Error handling and logging
  - Automatic rollback on exceptions
  - Proper session closure

- All database operations use async/await patterns for non-blocking I/O
- The health check returns a boolean indicating database connectivity status

## 4. Dependencies  

- **Internal**:
  - `backend.core.config`: For application settings
  
- **External**:
  - `sqlalchemy.ext.asyncio`: For async database operations
  - `sqlalchemy.engine.url`: For URL parsing
  - `sqlalchemy.exc`: For error handling

## 5. Tests  

| Test file | Scenario |
|-----------|----------|
| `backend/tests/core/test_database.py` | Basic health check test |
| `backend/tests/core/test_db_coverage_simple.py` | Session context manager, session error handling |

Current test coverage: 86%

## 6. Open TODOs  
- [ ] Add connection retry logic for production environments
- [ ] Consider connection pooling metrics for monitoring
- [ ] Add more comprehensive error handling for specific database errors
