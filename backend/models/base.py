from sqlalchemy.orm import declarative_base, mapped_column
from sqlalchemy import Integer

Base = declarative_base()


class BaseModel(Base):  # type: ignore[misc, valid-type]
    __abstract__ = True
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
