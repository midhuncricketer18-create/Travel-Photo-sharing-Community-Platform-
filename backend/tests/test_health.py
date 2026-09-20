from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_health_check() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Online Photography Print Platform API is running"
    }


def test_swagger_documentation_is_available() -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger" in response.text.lower()