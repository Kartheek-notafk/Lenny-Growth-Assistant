from fastapi.testclient import TestClient
from backend.app.main import app


def test_new_session_returns_a_unique_id():
    client = TestClient(app)
    a = client.post("/api/sessions").json()["session_id"]
    b = client.post("/api/sessions").json()["session_id"]
    assert a != b
    assert len(a) > 0


def test_session_messages_reflects_chat_history(monkeypatch):
    import backend.app.agent as agent

    async def fake_generate(prompt):
        return "Stub answer."

    monkeypatch.setattr(agent, "generate", fake_generate)

    client = TestClient(app)
    session_id = client.post("/api/sessions").json()["session_id"]

    client.post("/api/chat", json={"session_id": session_id, "message": "hello there"})

    history = client.get(f"/api/sessions/{session_id}/messages").json()
    assert history["session_id"] == session_id
    assert [m["role"] for m in history["messages"]] == ["user", "assistant"]


def test_chat_request_validation_rejects_empty_message():
    client = TestClient(app)
    r = client.post("/api/chat", json={"session_id": "s1", "message": ""})
    assert r.status_code == 422
