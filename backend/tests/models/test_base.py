from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base
from tests.test_templates import ModelUnitTestTemplate


class TestBaseModel(ModelUnitTestTemplate):
    def test_base_to_dict(self):
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
        self.assert_to_dict(dummy, {"id": 1, "name": "test"})
        self.assert_model_attrs(dummy, {"id": 1, "name": "test"})

    def test_base_to_dict_none(self):
        class DummyToDict(Base):
            __tablename__ = "dummy_to_dict_none"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(nullable=True)

            def to_dict(self) -> dict[str, object]:
                return {"id": self.id, "name": self.name}

        dummy = DummyToDict()
        dummy.id = 2
        dummy.name = None
        self.assert_to_dict(dummy, {"id": 2, "name": None})

    def test_base_repr(self):
        class DummyRepr(Base):
            __tablename__ = "dummy_repr"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(nullable=True)

        dummy = DummyRepr()
        dummy.id = 42
        self.assert_repr(dummy, "DummyRepr")

    def test_to_dict_missing_attr(self):
        class DummyMissing(Base):
            __tablename__ = "dummy_missing"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)
            # name intentionally missing

            def to_dict(self) -> dict[str, object]:
                return {"id": self.id}

        dummy = DummyMissing()
        dummy.id = 99
        self.assert_to_dict(dummy, {"id": 99})

    def test_repr_with_unset_attrs(self):
        class DummyUnset(Base):
            __tablename__ = "dummy_unset"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(nullable=True)

        dummy = DummyUnset()
        # id and name not set
        r = repr(dummy)
        assert "DummyUnset" in r
        assert "object at" in r

    def test_to_dict_with_extra_attrs(self):
        class DummyExtra(Base):
            __tablename__ = "dummy_extra"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)

            def to_dict(self) -> dict[str, object]:
                d = {"id": self.id}
                d["extra"] = "value"
                return d

        dummy = DummyExtra()
        dummy.id = 7
        self.assert_to_dict(dummy, {"id": 7, "extra": "value"})

    def test_to_dict_type_variants(self):
        class DummyTypes(Base):
            __tablename__ = "dummy_types"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)
            flag: Mapped[bool] = mapped_column(nullable=True)
            value: Mapped[float] = mapped_column(nullable=True)

            def to_dict(self) -> dict[str, object]:
                return {"id": self.id, "flag": self.flag, "value": self.value}

        dummy = DummyTypes()
        dummy.id = 3
        dummy.flag = True
        dummy.value = 1.23
        self.assert_to_dict(dummy, {"id": 3, "flag": True, "value": 1.23})

    def test_repr_edge_cases(self):
        class DummyEdge(Base):
            __tablename__ = "dummy_edge"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)

        dummy = DummyEdge()
        # id not set
        r = repr(dummy)
        assert "DummyEdge" in r
        assert "object at" in r
