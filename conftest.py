from pathlib import Path
import pytest
from loguru import logger

# Remove all handlers at module level to start clean
logger.remove()

@pytest.fixture(autouse=True)
def _global_teardown():
    logger.remove()
    yield
    logger.remove()

pytest_plugins = ["pytest_loguru"]

@pytest.fixture(autouse=True, scope="session")
def patch_loguru_remove(monkeypatch):
    orig_remove = logger.remove
    def safe_remove(handler_id=None):
        try:
            orig_remove(handler_id)
        except ValueError:
            pass
    monkeypatch.setattr(logger, "remove", safe_remove)
