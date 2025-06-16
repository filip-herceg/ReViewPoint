from datetime import datetime, UTC, timedelta
from src.schemas.blacklisted_token import BlacklistedTokenSchema
import pytest

def test_blacklisted_token_schema():
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


def test_schema_missing_fields():
    now = datetime.now(UTC)
    # created_at is optional
    schema = BlacklistedTokenSchema(jti="x", expires_at=now)
    assert schema.created_at is None
    # jti is required
    with pytest.raises(Exception):
        BlacklistedTokenSchema(expires_at=now)
    # expires_at is required
    with pytest.raises(Exception):
        BlacklistedTokenSchema(jti="x")

def test_schema_invalid_types():
    now = datetime.now(UTC)
    # jti must be str
    with pytest.raises(Exception):
        BlacklistedTokenSchema(jti=123, expires_at=now)
    # expires_at must be datetime
    with pytest.raises(Exception):
        BlacklistedTokenSchema(jti="x", expires_at="notadate")

def test_schema_none_values():
    # None for required fields should fail
    with pytest.raises(Exception):
        BlacklistedTokenSchema(jti=None, expires_at=None)
    # None for optional field is allowed
    now = datetime.now(UTC)
    schema = BlacklistedTokenSchema(jti="x", expires_at=now, created_at=None)
    assert schema.created_at is None

def test_schema_future_and_past_dates():
    now = datetime.now(UTC)
    future = now + timedelta(days=365)
    past = now - timedelta(days=365)
    schema_future = BlacklistedTokenSchema(jti="future", expires_at=future, created_at=now)
    schema_past = BlacklistedTokenSchema(jti="past", expires_at=past, created_at=now)
    assert schema_future.expires_at > now
    assert schema_past.expires_at < now
