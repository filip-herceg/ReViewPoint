def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_upload_mock(client):
    payload = {
        "title": "Test Title",
        "author": "John Smith",
        "content": "This is some text",
    }
    response = client.post("/upload", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["module_name"] == "structure_validator"
    assert "feedback" in data
