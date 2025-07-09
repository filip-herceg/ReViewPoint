"""
Pytest markers and utilities for conditional test execution.

This module provides custom pytest markers that allow tests to be skipped
conditionally based on the test environment, rather than being skipped in all environments.
"""

import os
from typing import Final

import pytest


def skip_if_fast_tests(reason: str | None = None) -> None:
    """
    Skip this test only when running in fast test mode (FAST_TESTS=1).

    Unlike pytest.skip(), this allows the test to run normally in the regular test environment.

    Args:
        reason: Optional reason for skipping the test

    Usage:
        @skip_if_fast_tests("SQLite in-memory does not support this feature")
        def test_something() -> None:
            # This test will be skipped only in fast mode
            pass

        # Or inside a test function:
        def test_something() -> None:
            skip_if_fast_tests("Feature not available in fast mode")
            # rest of test...
    """
    if os.environ.get("FAST_TESTS") == "1":
        default_reason: Final[str] = (
            "Test not compatible with fast test mode (SQLite in-memory)"
        )
        pytest.skip(reason or default_reason)


def skip_if_not_fast_tests(reason: str | None = None) -> None:
    """
    Skip this test only when NOT running in fast test mode.

    Useful for tests that are specific to the fast test environment.

    Args:
        reason: Optional reason for skipping the test

    Usage:
        @skip_if_not_fast_tests("This test is specific to fast test mode")
        def test_fast_mode_feature() -> None:
            # This test will be skipped in regular mode
            pass
    """
    if os.environ.get("FAST_TESTS") != "1":
        default_reason: Final[str] = "Test only runs in fast test mode"
        pytest.skip(reason or default_reason)


def requires_real_db(reason: str | None = None) -> None:
    """
    Skip this test when running with in-memory SQLite (fast test mode).

    This is an alias for skip_if_fast_tests with a more descriptive name.

    Args:
        reason: Optional reason for skipping the test

    Usage:
        @requires_real_db("Test requires PostgreSQL features")
        def test_postgres_feature() -> None:
            # This test will be skipped in fast mode
            pass
    """
    skip_if_fast_tests(
        reason
        or "Test requires real database features not available in SQLite in-memory"
    )


def requires_timing_precision(reason: str | None = None) -> None:
    """
    Skip this test when running in fast test mode due to timing issues.

    Args:
        reason: Optional reason for skipping the test

    Usage:
        @requires_timing_precision("Test relies on precise timing")
        def test_ttl_expiry() -> None:
            # This test will be skipped in fast mode
            pass
    """
    skip_if_fast_tests(
        reason or "Test requires precise timing not reliable in fast test mode"
    )


def skip_if_missing_feature(feature_name: str, reason: str | None = None) -> None:
    """
    Skip this test if a specific feature is not available.

    Args:
        feature_name: Name of the feature/dependency to check
        reason: Optional reason for skipping the test

    Usage:
        @skip_if_missing_feature("openapi_schema_validator", "Package not installed")
        def test_openapi_validation() -> None:
            # This test will be skipped if the feature is missing
            pass
    """
    try:
        __import__(feature_name)
    except ImportError:
        default_reason: Final[str] = f"Feature '{feature_name}' not available"
        pytest.skip(reason or default_reason)


# Pytest markers for use with @pytest.mark.skip_if_fast_tests
skip_if_fast_tests_marker: Final = pytest.mark.skip_if_fast_tests
skip_if_not_fast_tests_marker: Final = pytest.mark.skip_if_not_fast_tests
requires_real_db_marker: Final = pytest.mark.requires_real_db
requires_timing_precision_marker: Final = pytest.mark.requires_timing_precision
