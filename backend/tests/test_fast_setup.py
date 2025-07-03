"""Test to verify the fast testing setup works correctly."""

import os
import pytest


def test_fast_test_environment():
    """Test that fast test environment variables are set correctly."""
    assert os.environ.get("FAST_TESTS") == "1"
    assert os.environ.get("REVIEWPOINT_ENVIRONMENT") == "test"
    assert os.environ.get("REVIEWPOINT_LOG_LEVEL") == "DEBUG"
    assert "sqlite" in os.environ.get("REVIEWPOINT_DB_URL", "")


@pytest.mark.fast
def test_fast_marker():
    """Test that fast marker works."""
    assert True


@pytest.mark.slow
def test_slow_marker():
    """Test that should be skipped in fast mode."""
    assert True  # This should be skipped when --fast is used


def test_basic_functionality():
    """Basic test to ensure pytest works."""
    assert 1 + 1 == 2
