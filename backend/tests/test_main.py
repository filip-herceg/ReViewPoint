# Tests for src/main.py (FastAPI app entrypoint)
import importlib
import sys

import pytest
from fastapi import FastAPI

from tests.test_templates import MainAppTestTemplate


class TestMainApp(MainAppTestTemplate):
    def test_app_is_fastapi_instance(self):
        from src.main import create_app

        app = create_app()
        self.assert_is_instance(app, FastAPI)
        self.assert_equal(app.title, "ReViewPoint Core API")
        self.assert_equal(app.version, "0.1.0")

    def test_logging_initialized(self, monkeypatch):
        # Patch init_logging to check it is called with correct level
        from typing import Any

        called: dict[str, Any] = {}

        def fake_init_logging(level: str | None = None, **kwargs: Any) -> None:
            called["level"] = level
            called.update(kwargs)

        self.patch_var("src.main.init_logging", fake_init_logging)
        from src.main import create_app

        create_app()
        self.assert_in("level", called)

    def test_request_logging_middleware_present(self):
        from src.main import create_app

        app = create_app()
        self.assert_middleware_present(app, "RequestLoggingMiddleware")

    def test_app_can_start(self):
        # Use FastAPI TestClient to make a request and check middleware runs
        from fastapi.testclient import TestClient

        from src.main import create_app

        app = create_app()
        client = TestClient(app)
        resp = client.get("/docs")
        self.assert_status(resp, 200)

    def test_logging_init_error_propagates(self, monkeypatch):
        # Patch init_logging to raise
        def fake_init_logging(*_, **__):
            raise RuntimeError("logging failed")

        self.patch_var("src.main.init_logging", fake_init_logging)
        from src.main import create_app

        with pytest.raises(RuntimeError, match="logging failed"):
            create_app()

    def test_double_import_does_not_duplicate_middleware(self, monkeypatch):
        self.patch_var("src.core.logging.init_logging", lambda *a, **k: None)
        sys.modules.pop("src.main", None)
        importlib.invalidate_caches()
        import src.main  # noqa: F401

        app1 = src.main.app
        sys.modules.pop("src.main", None)
        importlib.invalidate_caches()
        import src.main as main2  # noqa: F401

        app2 = main2.app
        # Middleware should not be duplicated

        names1 = [
            getattr(m.cls, "__name__", type(m.cls).__name__)
            for m in app1.user_middleware
        ]
        names2 = [
            getattr(m.cls, "__name__", type(m.cls).__name__)
            for m in app2.user_middleware
        ]
        self.assert_equal(names1, names2)
        self.assert_equal(names1.count("RequestLoggingMiddleware"), 1)

    def test_main_module_import_and_lifecycle(self):
        import importlib

        import src.main

        importlib.reload(src.main)
        app = src.main.app
        self.assert_equal(app.title, "ReViewPoint Core API")
        self.assert_true(hasattr(app, "router"))
        from fastapi.testclient import TestClient

        with TestClient(app) as client:
            resp = client.get("/")
            # Accept 404 or 200, just to trigger the app
            self.assert_in(resp.status_code, (200, 404))

    def test_swagger_custom_css_served(self):
        from fastapi.testclient import TestClient

        from src.main import create_app

        client = TestClient(create_app())
        resp = client.get("/static/swagger-custom.css")
        self.assert_status(resp, 200)
        self.assert_in("text/css", resp.headers["content-type"])
        self.assert_in(b"ReViewPoint Swagger UI Custom Styles", resp.content)

    def test_swagger_favicon_served(self):
        from fastapi.testclient import TestClient

        from src.main import create_app

        client = TestClient(create_app())
        resp = client.get("/static/favicon.ico")
        self.assert_status(resp, 200)
        self.assert_true(resp.headers["content-type"].startswith("image/"))

    def test_swagger_ui_branding(self):
        from fastapi.testclient import TestClient

        from src.main import create_app

        client = TestClient(create_app())
        resp = client.get("/docs")
        self.assert_status(resp, 200)
        self.assert_in(b"ReViewPoint API Docs", resp.content)
        self.assert_in(b"swagger-custom.css", resp.content)
        self.assert_in(b"favicon.ico", resp.content)

    def test_swagger_custom_css_content(self):
        from fastapi.testclient import TestClient

        from src.main import create_app

        client = TestClient(create_app())
        resp = client.get("/static/swagger-custom.css")
        self.assert_status(resp, 200)
        self.assert_in("Swagger UI Custom Styles", resp.text)
        self.assert_in("background", resp.text)

    def test_swagger_favicon_content_type(self):
        from fastapi.testclient import TestClient
        from src.main import create_app
        client = TestClient(create_app())
        resp = self.safe_request(client.get, "/static/favicon.ico")
        self.assert_status(resp, 200)
        self.assert_in(
            resp.headers["content-type"],
            [
                "image/x-icon",
                "image/vnd.microsoft.icon",
                "image/ico",
                "image/icon",
            ],
        )
