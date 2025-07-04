"""Test to verify the fast testing setup works correctly."""

import os

import pytest


@pytest.mark.fast
def test_fast_test_environment():
    """Test that fast test environment variables are set correctly (only in fast mode)."""
    if os.environ.get("FAST_TESTS") != "1":
        pytest.skip("This test only runs in fast test mode")

    assert os.environ.get("FAST_TESTS") == "1"
    assert os.environ.get("REVIEWPOINT_ENVIRONMENT") == "test"
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
