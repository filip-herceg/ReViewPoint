
from datetime import UTC, datetime, timedelta
from typing import Final, Optional, Type, cast
from collections.abc import Container
from collections.abc import Container
from collections.abc import Sequence, Callable
import pytest
from pydantic import ValidationError

from src.schemas.blacklisted_token import BlacklistedTokenSchema
from tests.test_templates import ModelUnitTestTemplate


class TestBlacklistedTokenSchema(ModelUnitTestTemplate):
    # --- Typed assertion helpers for mypy compliance ---
    def assert_equal(self, a: object, b: object, msg: Optional[str] = None) -> None:
        assert a == b, msg or f"Expected {a!r} == {b!r}"

    def assert_not_equal(self, a: object, b: object, msg: Optional[str] = None) -> None:
        assert a != b, msg or f"Expected {a!r} != {b!r}"

    def assert_is_true(self, value: object, msg: Optional[str] = None) -> None:
        assert value, msg or "Expected expression to be True"

    def assert_is_none(self, value: object, msg: Optional[str] = None) -> None:
        assert value is None, msg or f"Expected {value!r} is None"

    def assert_in(self, member: object, container: object, msg: Optional[str] = None) -> None:
        # Best practice: match base signature, but check/cast at runtime for type safety
        if isinstance(container, Container):
            assert member in container, msg or f"Expected {member!r} in {container!r}"
        else:
            raise TypeError(f"Container argument does not support 'in': {type(container)}")

    def assert_raises(self, exc_type: type[BaseException], func: Callable[..., object], *args: object, **kwargs: object) -> None:
        with pytest.raises(exc_type):
            func(*args, **kwargs)

    def assert_repr(self, obj: object, class_name: str) -> None:
        assert class_name in repr(obj), f"Expected '{class_name}' in repr: {repr(obj)}"
    def test_valid_schema(self) -> None:
        """
        Verifies that BlacklistedTokenSchema accepts valid input and sets all fields correctly, including from dict.
        """
        now: Final[datetime] = datetime.now(UTC)
        schema: BlacklistedTokenSchema = BlacklistedTokenSchema(jti="abc123", expires_at=now, created_at=now)
        self.assert_equal(schema.jti, "abc123")
        self.assert_equal(schema.expires_at, now)
        self.assert_equal(schema.created_at, now)
        dummy: dict[str, object] = {"jti": "def456", "expires_at": now, "created_at": now}
        schema2: BlacklistedTokenSchema = BlacklistedTokenSchema.model_validate(dummy)
        self.assert_equal(schema2.jti, "def456")
        self.assert_equal(schema2.expires_at, now)
        self.assert_equal(schema2.created_at, now)




    @pytest.mark.parametrize(
        "jti,expires_at,created_at,should_raise",
        [
            (None, datetime.now(UTC), None, True),
            ("x", None, None, True),
            ("x", datetime.now(UTC), None, False),
            ("x", datetime.now(UTC), datetime.now(UTC), False),
        ],
    )
    def test_schema_missing_fields(
        self: "TestBlacklistedTokenSchema",
        jti: Optional[str],
        expires_at: Optional[datetime],
        created_at: Optional[datetime],
        should_raise: bool,
    ) -> None:
        """
        Verifies that BlacklistedTokenSchema raises ValidationError for missing required fields, or accepts valid input.
        """
        if should_raise:
            self.assert_raises(
                ValidationError,
                BlacklistedTokenSchema,
                jti=jti,
                expires_at=expires_at,
                created_at=created_at,
            )
        else:
            assert jti is not None
            assert expires_at is not None
            schema: BlacklistedTokenSchema = BlacklistedTokenSchema(
                jti=jti, expires_at=expires_at, created_at=created_at
            )
            self.assert_equal(schema.jti, jti)
            self.assert_equal(schema.expires_at, expires_at)
            # created_at can be None or a datetime, depending on input
            if created_at is not None:
                self.assert_equal(schema.created_at, created_at)
            else:
                self.assert_is_true(schema.created_at is None or isinstance(schema.created_at, datetime))

    @pytest.mark.parametrize(
        "jti,expires_at",
        [
            (123, datetime.now(UTC)),
            ("x", "notadate"),
        ],
    )
    def test_schema_invalid_types(
        self: "TestBlacklistedTokenSchema", jti: object, expires_at: object
    ) -> None:
        """
        Verifies that BlacklistedTokenSchema raises ValidationError for invalid types.
        """
        self.assert_raises(
            ValidationError, BlacklistedTokenSchema, jti=jti, expires_at=expires_at
        )

    def test_schema_none_values(self: "TestBlacklistedTokenSchema") -> None:
        """
        Verifies that BlacklistedTokenSchema raises ValidationError for None values, and accepts None for created_at.
        """
        self.assert_raises(ValidationError, BlacklistedTokenSchema, jti=None, expires_at=None)
        now: Final[datetime] = datetime.now(UTC)
        schema: BlacklistedTokenSchema = BlacklistedTokenSchema(jti="x", expires_at=now, created_at=None)
        self.assert_is_none(schema.created_at)

    def test_schema_future_and_past_dates(self: "TestBlacklistedTokenSchema") -> None:
        """
        Verifies that BlacklistedTokenSchema accepts both future and past dates for expires_at.
        """
        now: Final[datetime] = datetime.now(UTC)
        future: Final[datetime] = now + timedelta(days=365)
        past: Final[datetime] = now - timedelta(days=365)
        schema_future: BlacklistedTokenSchema = BlacklistedTokenSchema(
            jti="future", expires_at=future, created_at=now
        )
        schema_past: BlacklistedTokenSchema = BlacklistedTokenSchema(
            jti="past", expires_at=past, created_at=now
        )
        self.assert_is_true(schema_future.expires_at > now)
        self.assert_is_true(schema_past.expires_at < now)

    def test_schema_repr_and_to_dict(self: "TestBlacklistedTokenSchema") -> None:
        """
        Verifies that __repr__ and model_dump work as expected for BlacklistedTokenSchema.
        """
        now: Final[datetime] = datetime.now(UTC)
        schema: BlacklistedTokenSchema = BlacklistedTokenSchema(jti="reprtest", expires_at=now, created_at=now)
        self.assert_repr(schema, "BlacklistedTokenSchema")
        d: dict[str, object] = schema.model_dump()
        self.assert_equal(d["jti"], "reprtest")
        self.assert_equal(d["expires_at"], now)
        self.assert_equal(d["created_at"], now)

    def test_schema_equality(self: "TestBlacklistedTokenSchema") -> None:
        """
        Verifies that equality and inequality work for BlacklistedTokenSchema.
        """
        now: Final[datetime] = datetime.now(UTC)
        s1: BlacklistedTokenSchema = BlacklistedTokenSchema(jti="eq", expires_at=now, created_at=now)
        s2: BlacklistedTokenSchema = BlacklistedTokenSchema(jti="eq", expires_at=now, created_at=now)
        s3: BlacklistedTokenSchema = BlacklistedTokenSchema(jti="neq", expires_at=now, created_at=now)
        self.assert_equal(s1, s2)
        self.assert_not_equal(s1, s3)

    def test_schema_copy_and_update(self: "TestBlacklistedTokenSchema") -> None:
        """
        Verifies that model_copy and update work for BlacklistedTokenSchema.
        """
        now: Final[datetime] = datetime.now(UTC)
        s1: BlacklistedTokenSchema = BlacklistedTokenSchema(jti="copyme", expires_at=now, created_at=now)
        s2: BlacklistedTokenSchema = s1.model_copy(update={"jti": "copyme2"})
        self.assert_equal(s2.jti, "copyme2")
        self.assert_equal(s2.expires_at, now)
        self.assert_equal(s2.created_at, now)

    def test_schema_json_serialization(self: "TestBlacklistedTokenSchema") -> None:
        """
        Verifies that model_dump_json serializes BlacklistedTokenSchema correctly.
        """
        now: Final[datetime] = datetime.now(UTC)
        s1: BlacklistedTokenSchema = BlacklistedTokenSchema(jti="json", expires_at=now, created_at=now)
        json_str: str = s1.model_dump_json()
        self.assert_in("json", json_str)
        self.assert_in(str(now.year), json_str)

    def test_schema_from_orm(self: "TestBlacklistedTokenSchema") -> None:
        """
        Verifies that model_validate works with ORM-like objects.
        """
        now: Final[datetime] = datetime.now(UTC)

        class Dummy:
            jti: str
            expires_at: datetime
            created_at: datetime
            def __init__(self, jti: str, expires_at: datetime, created_at: datetime) -> None:
                self.jti = jti
                self.expires_at = expires_at
                self.created_at = created_at

        dummy: Dummy = Dummy("orm", now, now)
        schema: BlacklistedTokenSchema = BlacklistedTokenSchema.model_validate(dummy)
        self.assert_equal(schema.jti, "orm")
        self.assert_equal(schema.expires_at, now)
        self.assert_equal(schema.created_at, now)

    def test_schema_str(self: "TestBlacklistedTokenSchema") -> None:
        """
        Verifies that __str__ includes all relevant fields for BlacklistedTokenSchema.
        """
        now: Final[datetime] = datetime.now(UTC)
        s: BlacklistedTokenSchema = BlacklistedTokenSchema(jti="strtest", expires_at=now, created_at=now)
        s_str: str = str(s)
        self.assert_in("strtest", s_str)
        self.assert_in("expires_at", s_str)
        self.assert_in("created_at", s_str)
