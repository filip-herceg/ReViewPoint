import pytest

from backend.core.config import settings as global_settings
from backend.tests.utils import DummySettings


@pytest.fixture(autouse=True)
def settings(monkeypatch):
    config_mod = global_settings.__module__
    monkeypatch.setattr(config_mod, "settings", DummySettings())
    monkeypatch.setattr("backend.core.logging.init_logging", lambda *a: None)