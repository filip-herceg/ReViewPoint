from sqlalchemy.orm import sessionmaker

from src.core.database import engine

SessionLocal = sessionmaker(bind=engine)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
