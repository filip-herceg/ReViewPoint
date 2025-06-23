from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


def test_base_to_dict() -> None:
    class DummyToDict(Base):
        __tablename__ = "dummy_to_dict"
        __table_args__ = {"extend_existing": True}
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(nullable=True)

        def to_dict(self) -> dict[str, object]:
            return {"id": self.id, "name": self.name}

    dummy = DummyToDict()
    dummy.id = 1
    dummy.name = "test"
    d = dummy.to_dict()
    assert "id" in d
    assert "name" in d


def test_base_repr() -> None:
    class DummyRepr(Base):
        __tablename__ = "dummy_repr"
        __table_args__ = {"extend_existing": True}
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(nullable=True)

    dummy = DummyRepr()
    dummy.id = 42
    assert "DummyRepr object at " in repr(dummy)
