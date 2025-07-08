# Tests for src/main.py (FastAPI app entrypoint)
import importlib
import sys

import pytest
from fastapi import FastAPI

from tests.test_templates import MainAppTestTemplate


from typing import Final, Callable, Any
import importlib
import sys
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.test_templates import MainAppTestTemplate


class TestMainApp(MainAppTestTemplate):
    def test_app_is_fastapi_instance(self) -> None:
        """
        Test that create_app returns a FastAPI instance with correct title and version.
        """
        from src.main import create_app
        app: FastAPI = create_app()
        self.assert_is_instance(app, FastAPI)
        self.assert_equal(app.title, "ReViewPoint Core API")
        self.assert_equal(app.version, "0.1.0")

    def test_logging_initialized(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Test that init_logging is called with the correct level when app is created.
        """
        called: dict[str, object] = {}
        def fake_init_logging(level: str | None = None, **kwargs: object) -> None:
            called["level"] = level
            called.update(kwargs)
        self.patch_var("src.main.init_logging", fake_init_logging)
        from src.main import create_app
        create_app()
        assert "level" in called, f"Expected 'level' in called, got {called}"

    def test_request_logging_middleware_present(self) -> None:
        """
        Test that the RequestLoggingMiddleware is present in the app middleware stack.
        """
        from src.main import create_app
        app: FastAPI = create_app()
        self.assert_middleware_present(app, "RequestLoggingMiddleware")

    def test_app_can_start(self) -> None:
        """
        Test that the FastAPI app can start and respond to a /docs request.
        """
        from src.main import create_app
        app: FastAPI = create_app()
        client: TestClient = TestClient(app)
        resp = client.get("/docs")
        self.assert_status(resp, 200)

    def test_logging_init_error_propagates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Test that an error in init_logging propagates when creating the app.
        """
        def fake_init_logging(*_: object, **__: object) -> None:
            raise RuntimeError("logging failed")
        self.patch_var("src.main.init_logging", fake_init_logging)
        from src.main import create_app
        with pytest.raises(RuntimeError, match="logging failed"):
            create_app()

    def test_double_import_does_not_duplicate_middleware(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Test that double import of src.main does not duplicate middleware.
        """
        self.patch_var("src.core.logging.init_logging", lambda *a: None)
        sys.modules.pop("src.main", None)
        importlib.invalidate_caches()
        import src.main  # noqa: F401
        app1: FastAPI = src.main.app
        sys.modules.pop("src.main", None)
        importlib.invalidate_caches()
        import src.main as main2  # noqa: F401
        app2: FastAPI = main2.app
        names1: list[str] = [
            getattr(m.cls, "__name__", type(m.cls).__name__)
            for m in app1.user_middleware
        ]
        names2: list[str] = [
            getattr(m.cls, "__name__", type(m.cls).__name__)
            for m in app2.user_middleware
        ]
        self.assert_equal(names1, names2)
        self.assert_equal(names1.count("RequestLoggingMiddleware"), 1)

    def test_main_module_import_and_lifecycle(self) -> None:
        """
        Test that the main module can be imported, reloaded, and responds to requests.
        """
        import src.main
        importlib.reload(src.main)
        app: FastAPI = src.main.app
        self.assert_equal(app.title, "ReViewPoint Core API")
        self.assert_true(hasattr(app, "router"))
        with TestClient(app) as client:
            resp = client.get("/")
            assert resp.status_code in (200, 404), f"Expected status 200 or 404, got {resp.status_code}"

    def test_swagger_custom_css_served(self) -> None:
        """
        Test that the custom Swagger UI CSS is served with correct content type and content.
        """
        from src.main import create_app
        client: TestClient = TestClient(create_app())
        resp = client.get("/static/swagger-custom.css")
        self.assert_status(resp, 200)
        self.assert_in("text/css", resp.headers["content-type"])
        assert b"ReViewPoint Swagger UI Custom Styles" in resp.content, (
            f"Expected custom CSS branding in response content."
        )

    def test_swagger_favicon_served(self) -> None:
        """
        Test that the Swagger UI favicon is served with an image content type.
        """
        from src.main import create_app
        client: TestClient = TestClient(create_app())
        resp = client.get("/static/favicon.ico")
        self.assert_status(resp, 200)
        self.assert_true(resp.headers["content-type"].startswith("image/"))

    def test_swagger_ui_branding(self) -> None:
        """
        Test that the Swagger UI branding is present in the /docs page.
        """
        from src.main import create_app
        client: TestClient = TestClient(create_app())
        resp = client.get("/docs")
        self.assert_status(resp, 200)
        assert b"ReViewPoint API Docs" in resp.content, (
            "Expected API Docs branding in /docs response."
        )
        assert b"swagger-custom.css" in resp.content, (
            "Expected custom CSS link in /docs response."
        )
        assert b"favicon.ico" in resp.content, (
            "Expected favicon link in /docs response."
        )

    def test_swagger_custom_css_content(self) -> None:
        """
        Test that the custom Swagger UI CSS contains expected branding and styles.
        """
        from src.main import create_app
        client: TestClient = TestClient(create_app())
        resp = client.get("/static/swagger-custom.css")
        self.assert_status(resp, 200)
        self.assert_in("Swagger UI Custom Styles", resp.text)
        self.assert_in("background", resp.text)

    def test_swagger_favicon_content_type(self) -> None:
        """
        Test that the Swagger UI favicon is served with a valid icon content type.
        """
        from src.main import create_app
        client: TestClient = TestClient(create_app())
        resp = self.safe_request(client.get, "/static/favicon.ico")
        self.assert_status(resp, 200)
        assert resp.headers["content-type"] in [
            "image/x-icon",
            "image/vnd.microsoft.icon",
            "image/ico",
            "image/icon",
        ], f"Unexpected favicon content-type: {resp.headers['content-type']}"
