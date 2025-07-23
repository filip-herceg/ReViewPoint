# core/sync_database.py - Synchronous Database Session Management

## Purpose

The `core/sync_database.py` module provides synchronous database session management utilities for the ReViewPoint platform. It handles the creation and management of synchronous SQLAlchemy sessions, offering compatibility for code that requires blocking database operations while maintaining proper session lifecycle management and error handling.

## Key Components

### Engine Validation and Safety

#### Synchronous Engine Validation

```python
from collections.abc import Generator

from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import Session, sessionmaker


def _validate_sync_engine(engine: Engine | AsyncEngine | None) -> Engine:
    """
    Helper function to validate and return a sync engine.

    Args:
        engine: SQLAlchemy engine instance to validate

    Returns:
        Validated synchronous Engine instance

    Raises:
        RuntimeError: If engine is None or is an AsyncEngine
    """
    if engine is None:
        raise RuntimeError("No SQLAlchemy engine is configured.")

    if isinstance(engine, AsyncEngine):
        raise RuntimeError(
            "Synchronous session requested, but engine is an AsyncEngine. "
            "Use async session for AsyncEngine."
        )

    return engine
```

### Session Factory Management

#### Synchronous Session Factory Creation

````python
def get_sync_session_factory() -> sessionmaker[Session]:
    """
    Returns a sessionmaker for synchronous SQLAlchemy engines.

    This function creates a session factory configured for synchronous
    database operations. It validates that the configured engine is
    synchronous and raises appropriate errors if misconfigured.

    Returns:
        sessionmaker[Session]: Configured session factory for sync operations

    Raises:
        RuntimeError: If the engine is not a synchronous Engine or not configured

    Example:
        ```python
        # Get session factory
        SessionLocal = get_sync_session_factory()

        # Create session
        session = SessionLocal()
        try:
            # Perform database operations
            users = session.query(User).all()
        finally:
            session.close()
        ```
    """
    from src.core.database import engine

    # Validate and get sync engine
    sync_engine = _validate_sync_engine(engine)

    # Create and return sessionmaker
    return sessionmaker(bind=sync_engine)
````

### Session Context Management

#### Session Lifecycle Management

````python
def get_session() -> Generator[Session, None, None]:
    """
    Yields a SQLAlchemy Session object with automatic cleanup.

    This function provides a context-managed session that automatically
    closes after use, ensuring proper resource cleanup. It's designed
    for use with dependency injection or context managers.

    Yields:
        Session: The SQLAlchemy session object for database operations

    Raises:
        Exception: Any exception raised during session usage is propagated
        RuntimeError: If SessionLocal is not initialized or engine is not sync

    Example:
        ```python
        # Using as generator
        for session in get_session():
            users = session.query(User).all()
            break  # Session automatically closed

        # Using with dependency injection
        def process_users(session: Session = Depends(get_session)):
            return session.query(User).all()
        ```
    """
    SessionLocal = get_sync_session_factory()
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
````

### Advanced Session Management

#### Enhanced Session Utilities

````python
from typing import Optional, Any, Dict, Callable, TypeVar, Generic
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class SyncDatabaseManager:
    """Enhanced synchronous database session management"""

    def __init__(self, engine: Optional[Engine] = None):
        """
        Initialize database manager.

        Args:
            engine: Optional SQLAlchemy engine. If None, uses global engine.
        """
        if engine is None:
            from src.core.database import engine as global_engine
            engine = global_engine

        self.engine = _validate_sync_engine(engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope around a series of operations.

        This context manager handles session creation, transaction management,
        and cleanup automatically. It commits on success and rolls back on error.

        Yields:
            Session: Database session within transaction scope

        Example:
            ```python
            manager = SyncDatabaseManager()

            with manager.session_scope() as session:
                user = User(name="John Doe", email="john@example.com")
                session.add(user)
                # Transaction committed automatically on exit
            ```
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def execute_with_session(self, operation: Callable[[Session], T]) -> T:
        """
        Execute an operation with a managed session.

        Args:
            operation: Function that takes a session and returns a result

        Returns:
            Result of the operation

        Example:
            ```python
            def get_user_count(session: Session) -> int:
                return session.query(User).count()

            manager = SyncDatabaseManager()
            count = manager.execute_with_session(get_user_count)
            ```
        """
        with self.session_scope() as session:
            return operation(session)

    def bulk_execute(
        self,
        operations: list[Callable[[Session], Any]],
        stop_on_error: bool = True
    ) -> list[Any]:
        """
        Execute multiple operations in a single transaction.

        Args:
            operations: List of functions that take a session
            stop_on_error: Whether to stop on first error

        Returns:
            List of operation results

        Raises:
            SQLAlchemyError: If any operation fails and stop_on_error is True
        """
        results = []

        with self.session_scope() as session:
            for i, operation in enumerate(operations):
                try:
                    result = operation(session)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Operation {i} failed: {e}")

                    if stop_on_error:
                        raise
                    else:
                        results.append(None)

        return results

    def health_check(self) -> Dict[str, Any]:
        """
        Perform database health check.

        Returns:
            Health check results including connectivity and basic metrics
        """
        try:
            with self.session_scope() as session:
                # Test basic connectivity
                result = session.execute("SELECT 1 as test").fetchone()

                if result and result[0] == 1:
                    return {
                        "status": "healthy",
                        "engine_info": {
                            "driver": self.engine.driver,
                            "dialect": str(self.engine.dialect),
                            "pool_size": getattr(self.engine.pool, 'size', 'unknown'),
                            "pool_checked_out": getattr(self.engine.pool, 'checkedout', 'unknown')
                        }
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": "Failed to execute test query"
                    }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Global database manager instance
_database_manager: Optional[SyncDatabaseManager] = None

def get_database_manager() -> SyncDatabaseManager:
    """
    Get or create the global database manager instance.

    Returns:
        Configured SyncDatabaseManager instance
    """
    global _database_manager

    if _database_manager is None:
        _database_manager = SyncDatabaseManager()

    return _database_manager

def reset_database_manager() -> None:
    """Reset the global database manager (useful for testing)"""
    global _database_manager
    _database_manager = None
````

### Repository Pattern Support

#### Base Repository Implementation

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

T = TypeVar('T')

class SyncBaseRepository(Generic[T], ABC):
    """Base repository class for synchronous database operations"""

    def __init__(self, model_class: Type[T], session_factory: sessionmaker[Session]):
        """
        Initialize repository with model class and session factory.

        Args:
            model_class: SQLAlchemy model class
            session_factory: Session factory for database operations
        """
        self.model_class = model_class
        self.session_factory = session_factory

    @contextmanager
    def _get_session(self):
        """Get session with automatic cleanup"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create(self, **kwargs) -> T:
        """
        Create new entity.

        Args:
            **kwargs: Entity attributes

        Returns:
            Created entity instance
        """
        with self._get_session() as session:
            entity = self.model_class(**kwargs)
            session.add(entity)
            session.flush()
            session.refresh(entity)
            return entity

    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """
        Get entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Entity instance or None if not found
        """
        with self._get_session() as session:
            return session.query(self.model_class).get(entity_id)

    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """
        Get all entities with optional pagination.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of entity instances
        """
        with self._get_session() as session:
            query = session.query(self.model_class)

            if offset > 0:
                query = query.offset(offset)

            if limit is not None:
                query = query.limit(limit)

            return query.all()

    def update(self, entity_id: Any, **kwargs) -> Optional[T]:
        """
        Update entity by ID.

        Args:
            entity_id: Entity identifier
            **kwargs: Updated attributes

        Returns:
            Updated entity instance or None if not found
        """
        with self._get_session() as session:
            entity = session.query(self.model_class).get(entity_id)

            if entity is None:
                return None

            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            session.flush()
            session.refresh(entity)
            return entity

    def delete(self, entity_id: Any) -> bool:
        """
        Delete entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            True if entity was deleted, False if not found
        """
        with self._get_session() as session:
            entity = session.query(self.model_class).get(entity_id)

            if entity is None:
                return False

            session.delete(entity)
            return True

    def count(self) -> int:
        """
        Count total number of entities.

        Returns:
            Total entity count
        """
        with self._get_session() as session:
            return session.query(self.model_class).count()

    def exists(self, entity_id: Any) -> bool:
        """
        Check if entity exists by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            True if entity exists, False otherwise
        """
        with self._get_session() as session:
            return session.query(self.model_class).filter(
                self.model_class.id == entity_id
            ).first() is not None

    def find_by(self, **criteria) -> List[T]:
        """
        Find entities by criteria.

        Args:
            **criteria: Search criteria as keyword arguments

        Returns:
            List of matching entities
        """
        with self._get_session() as session:
            query = session.query(self.model_class)

            for key, value in criteria.items():
                if hasattr(self.model_class, key):
                    column = getattr(self.model_class, key)
                    query = query.filter(column == value)

            return query.all()

    def find_one_by(self, **criteria) -> Optional[T]:
        """
        Find single entity by criteria.

        Args:
            **criteria: Search criteria as keyword arguments

        Returns:
            First matching entity or None
        """
        entities = self.find_by(**criteria)
        return entities[0] if entities else None

class SyncRepositoryFactory:
    """Factory for creating repository instances"""

    def __init__(self, session_factory: sessionmaker[Session]):
        """
        Initialize factory with session factory.

        Args:
            session_factory: SQLAlchemy session factory
        """
        self.session_factory = session_factory
        self._repositories: Dict[Type, SyncBaseRepository] = {}

    def get_repository(self, model_class: Type[T]) -> SyncBaseRepository[T]:
        """
        Get or create repository for model class.

        Args:
            model_class: SQLAlchemy model class

        Returns:
            Repository instance for the model class
        """
        if model_class not in self._repositories:
            self._repositories[model_class] = SyncBaseRepository(
                model_class,
                self.session_factory
            )

        return self._repositories[model_class]

    def clear_cache(self) -> None:
        """Clear repository cache"""
        self._repositories.clear()

# Global repository factory
_repository_factory: Optional[SyncRepositoryFactory] = None

def get_repository_factory() -> SyncRepositoryFactory:
    """
    Get or create the global repository factory.

    Returns:
        Configured SyncRepositoryFactory instance
    """
    global _repository_factory

    if _repository_factory is None:
        session_factory = get_sync_session_factory()
        _repository_factory = SyncRepositoryFactory(session_factory)

    return _repository_factory

def get_repository(model_class: Type[T]) -> SyncBaseRepository[T]:
    """
    Get repository for model class.

    Args:
        model_class: SQLAlchemy model class

    Returns:
        Repository instance for the model class
    """
    factory = get_repository_factory()
    return factory.get_repository(model_class)
```

### Migration and Maintenance Utilities

#### Database Migration Support

```python
from alembic import command
from alembic.config import Config
from pathlib import Path
import os

class SyncDatabaseMigrator:
    """Synchronous database migration utilities"""

    def __init__(self, alembic_config_path: Optional[str] = None):
        """
        Initialize migrator with Alembic configuration.

        Args:
            alembic_config_path: Path to alembic.ini file
        """
        if alembic_config_path is None:
            # Try to find alembic.ini in common locations
            possible_paths = [
                "alembic.ini",
                "backend/alembic.ini",
                "../alembic.ini"
            ]

            for path in possible_paths:
                if Path(path).exists():
                    alembic_config_path = path
                    break

            if alembic_config_path is None:
                raise RuntimeError("Could not find alembic.ini configuration file")

        self.config = Config(alembic_config_path)

        # Set SQLAlchemy URL if not already set
        if not self.config.get_main_option("sqlalchemy.url"):
            from src.core.database import engine
            sync_engine = _validate_sync_engine(engine)
            self.config.set_main_option("sqlalchemy.url", str(sync_engine.url))

    def upgrade_to_head(self) -> None:
        """
        Upgrade database to the latest migration.

        Raises:
            Exception: If migration fails
        """
        try:
            command.upgrade(self.config, "head")
            logger.info("Database upgraded to head successfully")
        except Exception as e:
            logger.error(f"Database upgrade failed: {e}")
            raise

    def downgrade_by_steps(self, steps: int = 1) -> None:
        """
        Downgrade database by specified number of steps.

        Args:
            steps: Number of migration steps to downgrade

        Raises:
            Exception: If migration fails
        """
        try:
            revision = f"-{steps}"
            command.downgrade(self.config, revision)
            logger.info(f"Database downgraded by {steps} steps successfully")
        except Exception as e:
            logger.error(f"Database downgrade failed: {e}")
            raise

    def create_migration(
        self,
        message: str,
        autogenerate: bool = True
    ) -> str:
        """
        Create new migration file.

        Args:
            message: Migration message/description
            autogenerate: Whether to auto-generate migration content

        Returns:
            Generated migration revision ID

        Raises:
            Exception: If migration creation fails
        """
        try:
            if autogenerate:
                revision = command.revision(
                    self.config,
                    message=message,
                    autogenerate=True
                )
            else:
                revision = command.revision(self.config, message=message)

            logger.info(f"Migration created: {revision}")
            return revision
        except Exception as e:
            logger.error(f"Migration creation failed: {e}")
            raise

    def get_current_revision(self) -> Optional[str]:
        """
        Get current database revision.

        Returns:
            Current revision ID or None if no migrations applied
        """
        try:
            from alembic.runtime.migration import MigrationContext
            from src.core.database import engine

            sync_engine = _validate_sync_engine(engine)

            with sync_engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return None

    def check_migration_status(self) -> Dict[str, Any]:
        """
        Check database migration status.

        Returns:
            Migration status information
        """
        try:
            current_revision = self.get_current_revision()

            # Get head revision
            from alembic.script import ScriptDirectory
            script = ScriptDirectory.from_config(self.config)
            head_revision = script.get_current_head()

            return {
                "current_revision": current_revision,
                "head_revision": head_revision,
                "is_up_to_date": current_revision == head_revision,
                "migrations_pending": current_revision != head_revision
            }
        except Exception as e:
            logger.error(f"Failed to check migration status: {e}")
            return {
                "error": str(e),
                "status": "unknown"
            }

def get_migrator() -> SyncDatabaseMigrator:
    """
    Get database migrator instance.

    Returns:
        Configured SyncDatabaseMigrator instance
    """
    return SyncDatabaseMigrator()
```

### Testing and Development Utilities

#### Testing Support

```python
import pytest
from unittest.mock import Mock, patch
from typing import Generator, Any

class TestDatabaseManager:
    """Database manager for testing with isolation"""

    def __init__(self, test_engine: Engine):
        """
        Initialize test database manager.

        Args:
            test_engine: SQLAlchemy engine for testing (usually in-memory)
        """
        self.engine = test_engine
        self.SessionLocal = sessionmaker(bind=test_engine)

    @contextmanager
    def isolated_session(self):
        """
        Create isolated session for testing.

        Each test gets a fresh session with automatic rollback.
        """
        session = self.SessionLocal()
        transaction = session.begin()
        try:
            yield session
        finally:
            transaction.rollback()
            session.close()

    def create_test_data(self, model_class: Type[T], **kwargs) -> T:
        """
        Create test data instance.

        Args:
            model_class: Model class to create
            **kwargs: Model attributes

        Returns:
            Created test instance
        """
        with self.isolated_session() as session:
            instance = model_class(**kwargs)
            session.add(instance)
            session.flush()
            session.refresh(instance)
            return instance

    def cleanup_test_data(self, model_class: Type[T]) -> None:
        """
        Clean up test data for model class.

        Args:
            model_class: Model class to clean up
        """
        with self.isolated_session() as session:
            session.query(model_class).delete()

@pytest.fixture
def sync_session() -> Generator[Session, None, None]:
    """Pytest fixture for synchronous database session"""
    for session in get_session():
        yield session

@pytest.fixture
def test_database_manager() -> TestDatabaseManager:
    """Pytest fixture for test database manager"""
    from sqlalchemy import create_engine
    from src.models.base import Base

    # Create in-memory test database
    test_engine = create_engine("sqlite:///:memory:", echo=False)

    # Create all tables
    Base.metadata.create_all(test_engine)

    return TestDatabaseManager(test_engine)

# Usage example in tests
def test_user_creation(test_database_manager):
    """Example test using test database manager"""
    from src.models.user import User

    # Create test user
    user = test_database_manager.create_test_data(
        User,
        email="test@example.com",
        name="Test User"
    )

    assert user.id is not None
    assert user.email == "test@example.com"

    # Cleanup happens automatically

def test_repository_pattern():
    """Example test for repository pattern"""
    from src.models.user import User

    # Get repository
    user_repo = get_repository(User)

    # Test create
    user = user_repo.create(
        email="test@example.com",
        name="Test User"
    )

    assert user.id is not None

    # Test get by id
    retrieved_user = user_repo.get_by_id(user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"

    # Test update
    updated_user = user_repo.update(user.id, name="Updated Name")
    assert updated_user.name == "Updated Name"

    # Test delete
    deleted = user_repo.delete(user.id)
    assert deleted is True

    # Verify deletion
    assert user_repo.get_by_id(user.id) is None
```

## Dependencies

### Required Packages

- `sqlalchemy` - Core ORM functionality and session management
- `alembic` - Database migration support

### Internal Dependencies

- `src.core.database` - Main database configuration and engine
- Database models for repository pattern support
- Configuration system for database settings

## Usage Patterns

### Basic Session Usage

```python
# Simple session usage
for session in get_session():
    users = session.query(User).all()
    break

# With dependency injection (FastAPI)
from fastapi import Depends

def get_users(session: Session = Depends(get_session)):
    return session.query(User).all()
```

### Advanced Session Management

```python
# Using database manager
manager = get_database_manager()

with manager.session_scope() as session:
    user = User(name="John", email="john@example.com")
    session.add(user)
    # Transaction committed automatically

# Using repository pattern
user_repo = get_repository(User)
user = user_repo.create(name="John", email="john@example.com")
users = user_repo.get_all(limit=10)
```

## Performance Considerations

- **Session Lifecycle**: Automatic session cleanup prevents connection leaks
- **Transaction Management**: Proper transaction scoping with automatic rollback on errors
- **Connection Pooling**: Leverages SQLAlchemy's connection pooling for efficiency
- **Repository Pattern**: Provides consistent data access patterns with optimized queries

## Security Features

- **Engine Validation**: Prevents mixing async and sync operations
- **Safe Session Management**: Automatic cleanup and error handling
- **Transaction Isolation**: Proper transaction boundaries for data consistency

This synchronous database module provides comprehensive session management for scenarios where blocking database operations are required, while maintaining the same safety and reliability standards as the asynchronous database system.
