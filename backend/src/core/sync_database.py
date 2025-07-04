from collections.abc import Generator

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.database import engine

# Only create SessionLocal if engine is a synchronous Engine (not AsyncEngine)
SessionLocal: sessionmaker[Session] | None = None
if engine is not None and isinstance(engine, Engine):
    SessionLocal = sessionmaker(bind=engine)


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
    if SessionLocal is None:
        raise RuntimeError(
            "SessionLocal is not initialized. Ensure a synchronous SQLAlchemy Engine is available."
        )
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
