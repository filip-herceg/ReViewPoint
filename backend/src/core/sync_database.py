from collections.abc import Generator

from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import Session, sessionmaker


def _validate_sync_engine(engine: Engine | AsyncEngine | None) -> Engine:
    """Helper function to validate and return a sync engine."""
    if engine is None:
        raise RuntimeError("No SQLAlchemy engine is configured.")

    if isinstance(engine, AsyncEngine):
        raise RuntimeError(
            "Synchronous session requested, but engine is an AsyncEngine. Use async session for AsyncEngine."
        )

    return engine


def get_sync_session_factory() -> sessionmaker[Session]:
    """
    Returns a sessionmaker for synchronous SQLAlchemy engines.
    Raises RuntimeError if the engine is not a synchronous Engine.
    """
    from src.core.database import engine

    # Validate and get sync engine
    sync_engine = _validate_sync_engine(engine)

    # Create and return sessionmaker
    return sessionmaker(bind=sync_engine)


def get_session() -> Generator[Session, None, None]:
    """
    Yields a SQLAlchemy Session object.
    Closes the session after use.

    Yields:
        Session: The SQLAlchemy session object.

    Raises:
        Exception: Any exception raised during session usage is propagated.
        RuntimeError: If SessionLocal is not initialized or engine is not a sync Engine.
    """
    SessionLocal = get_sync_session_factory()
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
