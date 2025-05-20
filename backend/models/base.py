from sqlalchemy.orm import declarative_base, mapped_column  # type: ignore[attr-defined]
from sqlalchemy import Integer, DateTime, func


Base = declarative_base()


class BaseModel(Base):  # type: ignore[misc, valid-type]
    __abstract__ = True
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
