import logging

from .retrieval import retrieve
from .llm import generate, LLMUnavailableError
from .skills import SHIP_30_SKILL, ARTIFACT_SKILL
from .models import ChatRequest, ChatResponse, Source
from .config import settings
from . import db

logger = logging.getLogger("lenny.agent")


def _format_history(session_id: str) -> str:
    """Recent turns for this session, rendered for prompt inclusion.
    Lets the assistant handle follow-ups ("what about for B2B?") without the
    caller re-sending prior context."""
    history = db.get_history(session_id, settings.history_turns)
    if not history:
        return "(no prior turns in this session)"
    lines = []
    for m in history:
        speaker = "User" if m.role == "user" else "Assistant"
        lines.append(f"{speaker}: {m.content}")
    return "\n".join(lines)


async def answer_question(req: ChatRequest) -> ChatResponse:
    provider = settings.llm_provider.lower()

    # Persist the user turn before we do anything else, so it survives even
    # if retrieval or generation fails downstream.
    db.save_message(req.session_id, "user", req.message, provider=provider, skill=req.skill)

    chunks = retrieve(req.message, k=settings.retrieval_top_k)
    if not chunks:
        answer = (
            "I don't have enough support in the transcript knowledge base to "
            "answer that reliably. Try rephrasing, or ask about a topic covered "
            "by an ingested episode."
        )
        db.save_message(req.session_id, "assistant", answer, provider=provider, skill=req.skill)
        return ChatResponse(answer=answer, sources=[], provider=provider, grounded=False)

    context = "\n\n".join(
        f"[SOURCE: {c.title} | guest: {c.guest or 'unknown'} | file: {c.source}]\n{c.text}"
        for c in chunks
    )

    skill_instructions = ""
    if req.skill == "ship30":
        skill_instructions = SHIP_30_SKILL
    elif req.skill == "artifact":
        skill_instructions = ARTIFACT_SKILL

    prompt = f"""Conversation so far:
{_format_history(req.session_id)}

Current user question:
{req.message}

Additional skill instructions:
{skill_instructions or "(none — answer conversationally)"}

Transcript context:
{context}

Answer using the source names shown above. If the transcript context does not
support part of the answer, say so explicitly rather than filling the gap."""

    try:
        answer = await generate(prompt)
    except LLMUnavailableError as exc:
        logger.warning("LLM unavailable for session %s: %s", req.session_id, exc)
        answer = f"The {provider} model is currently unavailable: {exc}"
        db.save_message(req.session_id, "assistant", answer, provider=provider, skill=req.skill)
        return ChatResponse(answer=answer, sources=[], provider=provider, grounded=False)

    db.save_message(req.session_id, "assistant", answer, provider=provider, skill=req.skill)

    sources = [
        Source(title=c.title, source=c.source, guest=c.guest, url=c.url,
               snippet=c.text[:300] + ("..." if len(c.text) > 300 else ""))
        for c in chunks
    ]
    artifact = answer if req.skill == "artifact" else None

    return ChatResponse(answer=answer, sources=sources, artifact=artifact, provider=provider)
