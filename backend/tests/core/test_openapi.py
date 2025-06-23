from fastapi.testclient import TestClient

from src.core.openapi import setup_openapi
from src.main import app

# Fix the OpenAPI schema for tests
setup_openapi(app)

client = TestClient(app)


# --- General OpenAPI and Docs Tests ---
def test_openapi_metadata() -> None:
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert data["info"]["title"] == "ReViewPoint Core API"
    assert data["info"]["description"].startswith(
        "API for modular scientific paper review platform"
    )
    assert data["info"]["version"] == "0.1.0"
    assert "contact" in data["info"]
    assert "license" in data["info"]
    assert "servers" in data
    assert any(s["url"] == "http://localhost:8000" for s in data["servers"])
    assert any(s["url"] == "https://api.reviewpoint.org" for s in data["servers"])


def test_docs_accessible() -> None:
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200


# --- Endpoint Documentation Tests ---
def test_auth_register_docs() -> None:
    resp = client.get("/openapi.json")
    paths = resp.json()["paths"]
    assert "/api/v1/auth/register" in paths
    post = paths["/api/v1/auth/register"]["post"]
    assert post["summary"] == "Register a new user"
    assert "responses" in post
    assert "201" in post["responses"]


def test_auth_login_docs() -> None:
    resp = client.get("/openapi.json")
    post = resp.json()["paths"]["/api/v1/auth/login"]["post"]
    assert post["summary"] == "User login"
    assert "responses" in post
    assert "200" in post["responses"]
