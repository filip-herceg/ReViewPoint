# type: ignore
from backend.models.base import Base
import datetime
from typing import Any

mapped_column = None  # type: ignore[attr-defined]
Mapped = Any  # type: ignore


# Use a real mapped column for the Dummy model
def test_base_to_dict():
    class DummyToDict(Base):
        __tablename__ = "dummy_to_dict"
        name: Mapped[str] = mapped_column(nullable=True)

    dummy = DummyToDict()
    dummy.id = 1
    dummy.created_at = datetime.datetime.now()
    dummy.updated_at = datetime.datetime.now()
    dummy.name = "test"
    d = dummy.to_dict()
    assert "id" in d
    assert "created_at" in d
    assert "updated_at" in d
    assert "name" in d


def test_base_repr():
    class DummyRepr(Base):
        __tablename__ = "dummy_repr"
        name: Mapped[str] = mapped_column(nullable=True)

    dummy = DummyRepr()
    dummy.id = 42
    assert repr(dummy) == "<DummyRepr id=42>"
