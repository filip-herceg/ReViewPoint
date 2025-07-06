"""Test to verify the fast testing setup works correctly."""

import os
from typing import Final, Literal
import pytest


@pytest.mark.fast
def test_fast_test_environment() -> None:
    """
    Test that fast test environment variables are set correctly (only in fast mode).
    Skips if not in fast mode.
    """
    fast_env: Final[str | None] = os.environ.get("FAST_TESTS")
    if fast_env != "1":
        pytest.skip("This test only runs in fast test mode")

    env: Final[str | None] = os.environ.get("REVIEWPOINT_ENVIRONMENT")
    db_url: Final[str] = os.environ.get("REVIEWPOINT_DB_URL", "")
    assert fast_env == "1"
    assert env == "test"
    assert "sqlite" in db_url


@pytest.mark.fast
def test_fast_marker() -> None:
    """
    Test that fast marker works and the test is collected and run in fast mode.
    """
    assert True


@pytest.mark.slow
def test_slow_marker() -> None:
    """
    Test that should be skipped in fast mode (marked as slow).
    """
    assert True  # This should be skipped when --fast is used


def test_basic_functionality() -> None:
    """
    Basic test to ensure pytest works and arithmetic is correct.
    """
    result: int = 1 + 1
    assert result == 2
