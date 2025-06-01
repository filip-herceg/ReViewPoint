# Tests for src/main.py (FastAPI app entrypoint)
import importlib
import sys

import pytest
from fastapi import FastAPI


def test_app_is_fastapi_instance() -> None:
    from src.main import create_app

    app = create_app()
    assert isinstance(app, FastAPI)
    assert app.title == "ReViewPoint Core API"
    assert app.version == "0.1.0"


def test_logging_initialized(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch init_logging to check it is called with correct level
    from typing import Any

    called: dict[str, Any] = {}

    def fake_init_logging(level: str | None = None, **kwargs: Any):
        called["level"] = level
        called.update(kwargs)

    monkeypatch.setattr("src.main.init_logging", fake_init_logging)  # Patch where used
    from src.main import create_app

    create_app()
    assert "level" in called


def test_request_logging_middleware_present() -> None:
    from src.main import create_app

    app = create_app()
    middlewares: list[str] = [
        getattr(m, "cls", type(m)).__name__ for m in app.user_middleware
    ]
    assert "RequestLoggingMiddleware" in middlewares


def test_app_can_start() -> None:
    # Use FastAPI TestClient to make a request and check middleware runs
    from fastapi.testclient import TestClient

    from src.main import create_app

    app = create_app()
    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200


def test_logging_init_error_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch init_logging to raise
    def fake_init_logging(*_: object, **__: object) -> None:
        raise RuntimeError("logging failed")

    monkeypatch.setattr("src.main.init_logging", fake_init_logging)  # Patch where used
    from src.main import create_app

    with pytest.raises(RuntimeError, match="logging failed"):
        create_app()


def test_double_import_does_not_duplicate_middleware(monkeypatch: pytest.MonkeyPatch) -> None:
    # Patch init_logging to do nothing
    monkeypatch.setattr("src.core.logging.init_logging", lambda *a, **k: None)
    sys.modules.pop("src.main", None)
    importlib.invalidate_caches()
    import src.main  # noqa: F401

    app1 = src.main.app
    sys.modules.pop("src.main", None)
    importlib.invalidate_caches()
    import src.main as main2  # noqa: F401

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

    import src.main

    importlib.reload(src.main)
    app = src.main.app
    assert app.title == "ReViewPoint Core API"
    assert hasattr(app, "router")
    # Simulate startup and shutdown events
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        response = client.get("/")
        # Accept 404 or 200, just to trigger the app
        assert response.status_code in (200, 404)
