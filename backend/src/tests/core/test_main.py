# Tests for backend/main.py (FastAPI app entrypoint)
import importlib
import sys

import pytest
from fastapi import FastAPI


def test_app_is_fastapi_instance() -> None:
    import backend.main

    assert isinstance(backend.main.app, FastAPI)
    assert backend.main.app.title == "ReViewPoint Core API"
    assert backend.main.app.version == "0.1.0"


def test_logging_initialized(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch init_logging to check it is called with correct level
    from typing import Any

    called: dict[str, Any] = {}

    def fake_init_logging(level: str | None = None, **kwargs: Any) -> None:
        called["level"] = level
        called.update(kwargs)

    monkeypatch.setattr("backend.core.logging.init_logging", fake_init_logging)
    # Reload main.py to trigger logging init
    sys.modules.pop("backend.main", None)
    importlib.invalidate_caches()
    import backend.main

    _ = getattr(backend.main, "app", None)

    assert called["level"] == backend.main.settings.log_level


def test_request_logging_middleware_present() -> None:

    import backend.main

    middlewares: list[str] = [
        getattr(m, "cls", type(m)).__name__ for m in backend.main.app.user_middleware
    ]
    assert "RequestLoggingMiddleware" in middlewares


def test_app_can_start() -> None:
    # Use FastAPI TestClient to make a request and check middleware runs
    import backend.main
    from fastapi.testclient import TestClient

    client = TestClient(backend.main.app)
    response = client.get("/docs")
    assert response.status_code == 200
    # Optionally check for middleware effect (headers, logs, etc.)


def test_logging_init_error_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch init_logging to raise
    def fake_init_logging(*_: object, **__: object) -> None:
        raise RuntimeError("logging failed")

    monkeypatch.setattr("backend.core.logging.init_logging", fake_init_logging)
    sys.modules.pop("backend.main", None)
    importlib.invalidate_caches()
    with pytest.raises(RuntimeError, match="logging failed"):
        import backend.main

        _ = getattr(backend.main, "app", None)


def test_missing_log_level(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch settings to remove log_level
    import backend.core.config as config_mod

    orig_settings = config_mod.settings

    class DummySettings:
        pass

    config_mod.settings = DummySettings()
    monkeypatch.setattr("backend.core.logging.init_logging", lambda *a: None)
    sys.modules.pop("backend.main", None)
    importlib.invalidate_caches()
    try:
        import backend.main

        # Access an attribute to use the import (even if it raises)
        _ = getattr(backend.main, "app", None)

        # Should raise AttributeError
        raise AssertionError("Should raise AttributeError for missing log_level")
    except AttributeError:
        pass
    finally:
        config_mod.settings = orig_settings


def test_double_import_does_not_duplicate_middleware(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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

    names1: list[str] = [
        getattr(m.cls, "__name__", type(m.cls).__name__) for m in app1.user_middleware
    ]
    names2: list[str] = [
        getattr(m.cls, "__name__", type(m.cls).__name__) for m in app2.user_middleware
    ]
    assert names1 == names2
    assert names1.count("RequestLoggingMiddleware") == 1


def test_main_module_import_and_lifecycle() -> None:
    import importlib

    import backend.main

    importlib.reload(backend.main)
    app = backend.main.app
    assert app.title == "ReViewPoint Core API"
    assert hasattr(app, "router")
    # Simulate startup and shutdown events
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        response = client.get("/")
        # Accept 404 or 200, just to trigger the app
        assert response.status_code in (200, 404)
