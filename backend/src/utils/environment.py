import os


def is_test_mode() -> bool:
    return (
        os.environ.get("ENVIRONMENT") == "test"
        or bool(os.environ.get("PYTEST_CURRENT_TEST"))
        or os.environ.get("REVIEWPOINT_TEST_MODE") == "1"
    )
