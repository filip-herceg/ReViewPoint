from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from src.schemas.blacklisted_token import BlacklistedTokenSchema


def test_blacklisted_token_schema() -> None:
    now = datetime.now(UTC)
    schema = BlacklistedTokenSchema(jti="abc123", expires_at=now, created_at=now)
    assert schema.jti == "abc123"
    assert schema.expires_at == now
    assert schema.created_at == now
    # Test from_attributes (orm_mode) with dict
    dummy = {"jti": "def456", "expires_at": now, "created_at": now}
    schema2 = BlacklistedTokenSchema.model_validate(dummy)
    assert schema2.jti == "def456"
    assert schema2.expires_at == now
    assert schema2.created_at == now


def test_schema_missing_fields() -> None:
    now = datetime.now(UTC)
    # created_at is optional
    schema = BlacklistedTokenSchema(jti="x", expires_at=now)
    assert schema.created_at is None
    # jti is required
    with pytest.raises(ValidationError):
        BlacklistedTokenSchema(expires_at=now, jti=None)  # type: ignore[arg-type]
    # expires_at is required
    with pytest.raises(ValidationError):
        BlacklistedTokenSchema(jti="x", expires_at=None)  # type: ignore[arg-type]


def test_schema_invalid_types() -> None:
    now = datetime.now(UTC)
    # jti must be str
    with pytest.raises(ValidationError):
        BlacklistedTokenSchema(jti=123, expires_at=now)  # type: ignore[arg-type]
    # expires_at must be datetime
    with pytest.raises(ValidationError):
        BlacklistedTokenSchema(jti="x", expires_at="notadate")  # type: ignore[arg-type]


def test_schema_none_values() -> None:
    # None for required fields should fail
    with pytest.raises(ValidationError):
        BlacklistedTokenSchema(jti=None, expires_at=None)  # type: ignore[arg-type]
    # None for optional field is allowed
    now = datetime.now(UTC)
    schema = BlacklistedTokenSchema(jti="x", expires_at=now, created_at=None)
    assert schema.created_at is None


def test_schema_future_and_past_dates() -> None:
    now = datetime.now(UTC)
    future = now + timedelta(days=365)
    past = now - timedelta(days=365)
    schema_future = BlacklistedTokenSchema(
        jti="future", expires_at=future, created_at=now
    )
    schema_past = BlacklistedTokenSchema(jti="past", expires_at=past, created_at=now)
    assert schema_future.expires_at > now
    assert schema_past.expires_at < now
