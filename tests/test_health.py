from fastapi.testclient import TestClient
from backend.app.main import app


def test_health_reports_provider_and_db():
    client = TestClient(app)
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["provider"] in {"ollama", "openai"}
    assert body["database"] in {"up", "down"}
