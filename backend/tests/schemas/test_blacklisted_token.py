from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from src.schemas.blacklisted_token import BlacklistedTokenSchema
from tests.test_templates import ModelUnitTestTemplate


class TestBlacklistedTokenSchema(ModelUnitTestTemplate):
    def test_valid_schema(self):
        now = datetime.now(UTC)
        schema = BlacklistedTokenSchema(jti="abc123", expires_at=now, created_at=now)
        self.assert_equal(schema.jti, "abc123")
        self.assert_equal(schema.expires_at, now)
        self.assert_equal(schema.created_at, now)
        # Test from dict (orm_mode)
        dummy = {"jti": "def456", "expires_at": now, "created_at": now}
        schema2 = BlacklistedTokenSchema.model_validate(dummy)
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
    def test_schema_missing_fields(self, jti, expires_at, created_at, should_raise):
        if should_raise:
            self.assert_raises(
                ValidationError,
                BlacklistedTokenSchema,
                jti=jti,
                expires_at=expires_at,
                created_at=created_at,
            )
        else:
            schema = BlacklistedTokenSchema(
                jti=jti, expires_at=expires_at, created_at=created_at
            )
            self.assert_equal(schema.jti, jti)
            self.assert_equal(schema.expires_at, expires_at)
            self.assert_is_true(
                schema.created_at == created_at or schema.created_at is None
            )

    @pytest.mark.parametrize(
        "jti,expires_at",
        [
            (123, datetime.now(UTC)),
            ("x", "notadate"),
        ],
    )
    def test_schema_invalid_types(self, jti, expires_at):
        self.assert_raises(
            ValidationError, BlacklistedTokenSchema, jti=jti, expires_at=expires_at
        )

    def test_schema_none_values(self):
        self.assert_raises(ValidationError, BlacklistedTokenSchema, jti=None, expires_at=None)  # type: ignore[arg-type]
        now = datetime.now(UTC)
        schema = BlacklistedTokenSchema(jti="x", expires_at=now, created_at=None)
        self.assert_is_none(schema.created_at)

    def test_schema_future_and_past_dates(self):
        now = datetime.now(UTC)
        future = now + timedelta(days=365)
        past = now - timedelta(days=365)
        schema_future = BlacklistedTokenSchema(
            jti="future", expires_at=future, created_at=now
        )
        schema_past = BlacklistedTokenSchema(
            jti="past", expires_at=past, created_at=now
        )
        self.assert_is_true(schema_future.expires_at > now)
        self.assert_is_true(schema_past.expires_at < now)

    def test_schema_repr_and_to_dict(self):
        now = datetime.now(UTC)
        schema = BlacklistedTokenSchema(jti="reprtest", expires_at=now, created_at=now)
        self.assert_repr(schema, "BlacklistedTokenSchema")
        d = schema.model_dump()
        self.assert_equal(d["jti"], "reprtest")
        self.assert_equal(d["expires_at"], now)
        self.assert_equal(d["created_at"], now)

    def test_schema_equality(self):
        now = datetime.now(UTC)
        s1 = BlacklistedTokenSchema(jti="eq", expires_at=now, created_at=now)
        s2 = BlacklistedTokenSchema(jti="eq", expires_at=now, created_at=now)
        self.assert_equal(s1, s2)
        s3 = BlacklistedTokenSchema(jti="neq", expires_at=now, created_at=now)
        self.assert_not_equal(s1, s3)

    def test_schema_copy_and_update(self):
        now = datetime.now(UTC)
        s1 = BlacklistedTokenSchema(jti="copyme", expires_at=now, created_at=now)
        s2 = s1.model_copy(update={"jti": "copyme2"})
        self.assert_equal(s2.jti, "copyme2")
        self.assert_equal(s2.expires_at, now)
        self.assert_equal(s2.created_at, now)

    def test_schema_json_serialization(self):
        now = datetime.now(UTC)
        s1 = BlacklistedTokenSchema(jti="json", expires_at=now, created_at=now)
        json_str = s1.model_dump_json()
        self.assert_in("json", json_str)
        self.assert_in(str(now.year), json_str)

    def test_schema_from_orm(self):
        now = datetime.now(UTC)

        class Dummy:
            def __init__(self, jti, expires_at, created_at):
                self.jti = jti
                self.expires_at = expires_at
                self.created_at = created_at

        dummy = Dummy("orm", now, now)
        schema = BlacklistedTokenSchema.model_validate(dummy)
        self.assert_equal(schema.jti, "orm")
        self.assert_equal(schema.expires_at, now)
        self.assert_equal(schema.created_at, now)

    def test_schema_str(self):
        now = datetime.now(UTC)
        s = BlacklistedTokenSchema(jti="strtest", expires_at=now, created_at=now)
        s_str = str(s)
        self.assert_in("strtest", s_str)
        self.assert_in("expires_at", s_str)
        self.assert_in("created_at", s_str)
