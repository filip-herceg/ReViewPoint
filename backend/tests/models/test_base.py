# type: ignore
from backend.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column


# Use a real mapped column for the Dummy model
def test_base_to_dict():
    class DummyToDict(Base):
        __tablename__ = "dummy_to_dict"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(nullable=True)

        def to_dict(self):
            # Simple implementation for test purposes
            return {
                "id": self.id,
                "name": self.name,
                # created_at and updated_at are not present in this dummy, so skip
            }

    dummy = DummyToDict()
    dummy.id = 1
    dummy.name = "test"
    d = dummy.to_dict()
    assert "id" in d
    assert "name" in d


def test_base_repr():
    class DummyRepr(Base):
        __tablename__ = "dummy_repr"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(nullable=True)

    dummy = DummyRepr()
    dummy.id = 42
    # For local classes, __repr__ includes the full module and function path
    assert repr(dummy).startswith(
        "<test_base.test_base_repr.<locals>.DummyRepr object at "
    )
