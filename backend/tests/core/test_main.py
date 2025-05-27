# Tests for backend/main.py (FastAPI app entrypoint)
import importlib
import sys

import pytest
from fastapi import FastAPI


def test_app_is_fastapi_instance():
    import backend.main

    assert isinstance(backend.main.app, FastAPI)
    assert backend.main.app.title == "ReViewPoint Core API"
    assert backend.main.app.version == "0.1.0"


def test_logging_initialized(monkeypatch):
    # Patch init_logging to check it is called with correct level
    called = {}

    def fake_init_logging(level=None, **kwargs):
        called["level"] = level
        called.update(kwargs)

    monkeypatch.setattr("backend.core.logging.init_logging", fake_init_logging)
    # Reload main.py to trigger logging init
    sys.modules.pop("backend.main", None)
    importlib.invalidate_caches()
    import backend.main  # noqa: F401

    assert called["level"] == backend.main.settings.log_level


def test_request_logging_middleware_present():
    import backend.main

    middlewares = [m.cls.__name__ for m in backend.main.app.user_middleware]
    assert "RequestLoggingMiddleware" in middlewares


def test_app_can_start(monkeypatch):
    # Use FastAPI TestClient to make a request and check middleware runs
    from fastapi.testclient import TestClient

    import backend.main

    client = TestClient(backend.main.app)
    response = client.get("/docs")
    assert response.status_code == 200
    # Optionally check for middleware effect (headers, logs, etc.)


def test_logging_init_error_propagates(monkeypatch):
    # Patch init_logging to raise
    def fake_init_logging(*a, **k):
        raise RuntimeError("logging failed")

    monkeypatch.setattr("backend.core.logging.init_logging", fake_init_logging)
    sys.modules.pop("backend.main", None)
    importlib.invalidate_caches()
    with pytest.raises(RuntimeError, match="logging failed"):
        import backend.main  # noqa: F401


def test_missing_log_level(monkeypatch):
    # Patch settings to remove log_level
    import backend.core.config as config_mod

    orig_settings = config_mod.settings

    class DummySettings:
        pass

    config_mod.settings = DummySettings()
    monkeypatch.setattr("backend.core.logging.init_logging", lambda *a, **k: None)
    sys.modules.pop("backend.main", None)
    importlib.invalidate_caches()
    try:
        import backend.main  # noqa: F401

        # Should raise AttributeError
        raise AssertionError("Should raise AttributeError for missing log_level")
    except AttributeError:
        pass
    finally:
        config_mod.settings = orig_settings


def test_double_import_does_not_duplicate_middleware(monkeypatch):
    # Patch init_logging to do nothing
    monkeypatch.setattr("backend.core.logging.init_logging", lambda *a, **k: None)
    sys.modules.pop("backend.main", None)
    importlib.invalidate_caches()
    import backend.main  # noqa: F401

    app1 = backend.main.app
    sys.modules.pop("backend.main", None)
    importlib.invalidate_caches()
    import backend.main as main2  # noqa: F401

    app2 = main2.app
    # Middleware should not be duplicated
    names1 = [m.cls.__name__ for m in app1.user_middleware]
    names2 = [m.cls.__name__ for m in app2.user_middleware]
    assert names1 == names2
    assert names1.count("RequestLoggingMiddleware") == 1
