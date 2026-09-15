import uuid
import pathlib
import pytest

import backend.app.agent as agent
import backend.app.retrieval as retrieval
import backend.app.llm as llm
import backend.app.db as db
from backend.app.models import ChatRequest

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "transcripts"


@pytest.fixture(autouse=True)
def fixture_transcripts(monkeypatch):
    monkeypatch.setattr(retrieval, "DATA_DIR", FIXTURES)
    retrieval.load_chunks.cache_clear()
    db.init_db()


async def test_ungrounded_question_short_circuits_without_calling_llm(monkeypatch):
    called = {"hit": False}

    async def fake_generate(prompt):
        called["hit"] = True
        return "should not be called"

    monkeypatch.setattr(llm, "generate", fake_generate)
    monkeypatch.setattr(agent, "generate", fake_generate)

    req = ChatRequest(session_id=str(uuid.uuid4()), message="xylophone zeppelin quokka")
    resp = await agent.answer_question(req)

    assert resp.grounded is False
    assert resp.sources == []
    assert called["hit"] is False


async def test_conversation_history_is_persisted_and_fed_back(monkeypatch):
    seen_prompts = []

    async def fake_generate(prompt):
        seen_prompts.append(prompt)
        return "A grounded answer about pricing."

    monkeypatch.setattr(agent, "generate", fake_generate)

    session_id = str(uuid.uuid4())
    first = ChatRequest(session_id=session_id, message="How should I price a subscription product?")
    await agent.answer_question(first)

    followup = ChatRequest(session_id=session_id, message="What about for enterprise customers?")
    await agent.answer_question(followup)

    # the second call's prompt should include the first turn as history
    assert "How should I price a subscription product?" in seen_prompts[1]
    assert "A grounded answer about pricing." in seen_prompts[1]

    history = db.get_history(session_id, limit_turns=10)
    roles = [m.role for m in history]
    assert roles == ["user", "assistant", "user", "assistant"]


async def test_llm_unavailable_is_handled_gracefully_not_raised(monkeypatch):
    async def broken_generate(prompt):
        raise llm.LLMUnavailableError("Ollama is not running")

    monkeypatch.setattr(agent, "generate", broken_generate)

    req = ChatRequest(session_id=str(uuid.uuid4()), message="How should I price a subscription product?")
    resp = await agent.answer_question(req)

    assert resp.grounded is False
    assert "unavailable" in resp.answer.lower()
