import os
from typing import Final

# Module-level constants for environment variable names
ENVIRONMENT_VAR: Final[str] = "ENVIRONMENT"
PYTEST_CURRENT_TEST_VAR: Final[str] = "PYTEST_CURRENT_TEST"
REVIEWPOINT_TEST_MODE_VAR: Final[str] = "REVIEWPOINT_TEST_MODE"
TEST_ENV_LITERAL: Final[str] = "test"
TEST_MODE_LITERAL: Final[str] = "1"


def is_test_mode() -> bool:
    """
    Returns True if the current environment is test mode.
    Checks the following environment variables:
    - ENVIRONMENT == 'test'
    - PYTEST_CURRENT_TEST is set (not None or empty)
    - REVIEWPOINT_TEST_MODE == '1'

    :return: True if in test mode, False otherwise.
    """
    env: str | None = os.environ.get(ENVIRONMENT_VAR)
    pytest_current_test: str | None = os.environ.get(PYTEST_CURRENT_TEST_VAR)
    reviewpoint_test_mode: str | None = os.environ.get(REVIEWPOINT_TEST_MODE_VAR)
    return (
        env == TEST_ENV_LITERAL
        or bool(pytest_current_test)
        or reviewpoint_test_mode == TEST_MODE_LITERAL
    )
