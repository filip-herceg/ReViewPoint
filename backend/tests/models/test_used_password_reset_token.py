from datetime import UTC, datetime

import pytest

from src.models.used_password_reset_token import UsedPasswordResetToken


def test_token_creation_and_repr() -> None:
    token = UsedPasswordResetToken(
        email="test@example.com", nonce="abc123", used_at=datetime.now(UTC)
    )
    assert token.email == "test@example.com"
    assert token.nonce == "abc123"
    assert isinstance(token.used_at, datetime)
    assert "test@example.com" in repr(token)
    assert "abc123" in repr(token)


def test_token_used_at_timezone() -> None:
    now = datetime.now(UTC)
    token = UsedPasswordResetToken(
        email="user2@example.com", nonce="nonce2", used_at=now
    )
    assert token.used_at.tzinfo is UTC


def test_token_edge_cases() -> None:
    # Edge: empty email
    with pytest.raises(ValueError):
        UsedPasswordResetToken(email="", nonce="n", used_at=datetime.now(UTC))
    # Edge: empty nonce
    with pytest.raises(ValueError):
        UsedPasswordResetToken(email="a@b.com", nonce="", used_at=datetime.now(UTC))
    # Edge: used_at in the past
    past = datetime(2000, 1, 1, tzinfo=UTC)
    token = UsedPasswordResetToken(email="a@b.com", nonce="n2", used_at=past)
    assert token.used_at.year == 2000
