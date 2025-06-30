import sys
import os

# Ensure the project root is in sys.path for test imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from loguru import logger

# Remove all handlers at module level to start clean
logger.remove()


@pytest.fixture(autouse=True)
def _global_teardown():
    logger.remove()
    yield
    logger.remove()


pytest_plugins = [
    "backend.tests.pytest_plugins.mapping_checker",
    "pytest_loguru",
]


@pytest.fixture(autouse=True, scope="session")
def patch_loguru_remove(monkeypatch):
    orig_remove = logger.remove

    def safe_remove(handler_id=None):
        try:
            orig_remove(handler_id)
        except ValueError:
            pass

    monkeypatch.setattr(logger, "remove", safe_remove)
