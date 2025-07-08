import sys
import os
from collections.abc import Generator
from typing import Final

import pytest
from loguru import logger

# Ensure the project root is in sys.path for test imports
project_root: Final[str] = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Remove all handlers at module level to start clean
logger.remove()

@pytest.fixture(autouse=True)
def _global_teardown() -> Generator[None, None, None]:
    """
    Fixture to remove all loguru handlers before and after each test for a clean log state.
    """
    logger.remove()
    yield
    logger.remove()

pytest_plugins: list[str] = [
    "backend.tests.pytest_plugins.mapping_checker",
    "pytest_loguru",
]

@pytest.fixture(autouse=True, scope="session")
def patch_loguru_remove(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Patch loguru's remove method to safely ignore ValueError if handler is already removed.
    """
    orig_remove = logger.remove

    def safe_remove(handler_id: int | None = None) -> None:
        try:
            orig_remove(handler_id)
        except ValueError:
            pass

    monkeypatch.setattr(logger, "remove", safe_remove)
