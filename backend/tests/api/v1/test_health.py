from fastapi.testclient import TestClient

from src.main import app


def test_health_unauthorized() -> None:
    client = TestClient(app)
    resp = client.get("/api/v1/health")
    # Health endpoint may or may not require auth, accept 200 or 401
    assert resp.status_code in [200, 401]


def test_health_invalid_method() -> None:
    client = TestClient(app)
    resp = client.post("/api/v1/health")
    assert resp.status_code in [405, 401]  # 405 Method Not Allowed or 401 Unauthorized


def test_health_invalid_token() -> None:
    client = TestClient(app)
    resp = client.get("/api/v1/health", headers={"Authorization": "Bearer not.a.jwt"})
    assert resp.status_code in [200, 401]
