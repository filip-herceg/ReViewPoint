"""Test module for SQLAlchemy base model functionality.

This module tests the base SQLAlchemy model classes including:
- Base declarative base class functionality
- Custom to_dict method implementations
- Model representation and attribute handling
- Edge cases for model operations
"""

from __future__ import annotations

from typing import Any, Final

from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base
from tests.test_templates import ModelUnitTestTemplate


class TestBaseModel(ModelUnitTestTemplate):
    """Test class for Base SQLAlchemy model functionality."""

    def _assert_to_dict_typed(self, model: Any, expected_dict: dict[str, Any]) -> None:
        """Type-safe wrapper for assert_to_dict method."""
        # Use cast to handle the untyped method call
        from typing import cast

        cast(Any, self.assert_to_dict)(model, expected_dict)

    def _assert_model_attrs_typed(self, model: Any, attrs: dict[str, Any]) -> None:
        """Type-safe wrapper for assert_model_attrs method."""
        from typing import cast

        cast(Any, self.assert_model_attrs)(model, attrs)

    def _assert_repr_typed(self, obj: Any, class_name: str) -> None:
        """Type-safe wrapper for assert_repr method."""
        from typing import cast

        cast(Any, self.assert_repr)(obj, class_name)

    def test_base_to_dict(self) -> None:
        """Test that custom to_dict method works correctly with set attributes.

        This test verifies that a custom to_dict implementation on a model
        class properly returns the expected dictionary representation when
        all attributes are set to non-None values.
        """

        class DummyToDict(Base):
            __tablename__ = "dummy_to_dict"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str | None] = mapped_column(nullable=True)

            def to_dict(self) -> dict[str, Any]:
                return {"id": self.id, "name": self.name}

        dummy: DummyToDict = DummyToDict()
        dummy.id = 1
        dummy.name = "test"

        expected_dict: Final[dict[str, Any]] = {"id": 1, "name": "test"}
        self._assert_to_dict_typed(dummy, expected_dict)
        self._assert_model_attrs_typed(dummy, expected_dict)

    def test_base_to_dict_none(self) -> None:
        """Test that custom to_dict method handles None values correctly.

        This test verifies that when a nullable field is set to None,
        the to_dict method properly includes the None value in the
        returned dictionary.
        """

        class DummyToDict(Base):
            __tablename__ = "dummy_to_dict_none"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str | None] = mapped_column(nullable=True)

            def to_dict(self) -> dict[str, Any]:
                return {"id": self.id, "name": self.name}

        dummy: DummyToDict = DummyToDict()
        dummy.id = 2
        dummy.name = None

        expected_dict: Final[dict[str, Any]] = {"id": 2, "name": None}
        self._assert_to_dict_typed(dummy, expected_dict)

    def test_base_repr(self) -> None:
        """Test that model representation includes the class name.

        This test verifies that the default __repr__ implementation
        for SQLAlchemy models includes the class name in the string
        representation, which is useful for debugging.
        """

        class DummyRepr(Base):
            __tablename__ = "dummy_repr"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str | None] = mapped_column(nullable=True)

        dummy: DummyRepr = DummyRepr()
        dummy.id = 42

        expected_class_name: Final[str] = "DummyRepr"
        self._assert_repr_typed(dummy, expected_class_name)

    def test_to_dict_missing_attr(self) -> None:
        """Test to_dict method with minimal attributes.

        This test verifies that a to_dict implementation works correctly
        when the model has fewer attributes than other test cases, ensuring
        the method only returns the attributes it's designed to handle.
        """

        class DummyMissing(Base):
            __tablename__ = "dummy_missing"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)
            # name intentionally missing

            def to_dict(self) -> dict[str, Any]:
                return {"id": self.id}

        dummy: DummyMissing = DummyMissing()
        dummy.id = 99

        expected_dict: Final[dict[str, Any]] = {"id": 99}
        self._assert_to_dict_typed(dummy, expected_dict)

    def test_repr_with_unset_attrs(self) -> None:
        """Test model representation when attributes are not set.

        This test verifies that the __repr__ method works correctly
        even when model attributes haven't been set, which can happen
        when creating model instances without immediately populating them.
        """

        class DummyUnset(Base):
            __tablename__ = "dummy_unset"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str | None] = mapped_column(nullable=True)

        dummy: DummyUnset = DummyUnset()
        # id and name not set
        r: str = repr(dummy)
        assert "DummyUnset" in r
        assert "object at" in r

    def test_to_dict_with_extra_attrs(self) -> None:
        """Test to_dict method with additional non-column attributes.

        This test verifies that a custom to_dict implementation can
        include computed or derived values that aren't directly mapped
        to database columns, providing flexibility in API responses.
        """

        class DummyExtra(Base):
            __tablename__ = "dummy_extra"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)

            def to_dict(self) -> dict[str, Any]:
                d: dict[str, Any] = {"id": self.id}
                d["extra"] = "value"
                return d

        dummy: DummyExtra = DummyExtra()
        dummy.id = 7

        expected_dict: Final[dict[str, Any]] = {"id": 7, "extra": "value"}
        self._assert_to_dict_typed(dummy, expected_dict)

    def test_to_dict_type_variants(self) -> None:
        """Test to_dict method with various data types.

        This test verifies that the to_dict method correctly handles
        different data types including integers, booleans, and floats,
        ensuring type preservation in the serialized representation.
        """

        class DummyTypes(Base):
            __tablename__ = "dummy_types"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)
            flag: Mapped[bool | None] = mapped_column(nullable=True)
            value: Mapped[float | None] = mapped_column(nullable=True)

            def to_dict(self) -> dict[str, Any]:
                return {"id": self.id, "flag": self.flag, "value": self.value}

        dummy: DummyTypes = DummyTypes()
        dummy.id = 3
        dummy.flag = True
        dummy.value = 1.23

        expected_dict: Final[dict[str, Any]] = {"id": 3, "flag": True, "value": 1.23}
        self._assert_to_dict_typed(dummy, expected_dict)

    def test_repr_edge_cases(self) -> None:
        """Test model representation in edge cases.

        This test verifies that the __repr__ method behaves correctly
        for minimal model classes and when primary key attributes
        are not set, which is common during model instantiation.
        """

        class DummyEdge(Base):
            __tablename__ = "dummy_edge"
            __table_args__ = {"extend_existing": True}
            id: Mapped[int] = mapped_column(primary_key=True)

        dummy: DummyEdge = DummyEdge()
        # id not set
        r: str = repr(dummy)
        assert "DummyEdge" in r
        assert "object at" in r
