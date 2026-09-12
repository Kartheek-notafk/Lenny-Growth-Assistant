from .retrieval import retrieve
from .llm import generate
from .skills import SHIP_30_SKILL, ARTIFACT_SKILL
from .models import ChatRequest, ChatResponse, Source

async def answer_question(req: ChatRequest):
    chunks = retrieve(req.message)
    if not chunks:
        return ChatResponse(
            answer="I don't have enough support in the transcript knowledge base to answer that reliably.",
            sources=[],
            provider="ollama",
        )

    context = "\n\n".join(
        f"[SOURCE: {c.title} | {c.source}]\n{c.text}" for c in chunks
    )

    skill = ""
    if req.skill == "ship30":
        skill = SHIP_30_SKILL
    elif req.skill == "artifact":
        skill = ARTIFACT_SKILL

    prompt = f"""User question:
{req.message}

Additional skill instructions:
{skill}

Transcript context:
{context}

Answer with source references using the source names above."""

    answer = await generate(prompt)
    sources = [
        Source(title=c.title, source=c.source, snippet=c.text[:300] + "...")
        for c in chunks
    ]
    artifact = None
    if req.skill == "artifact":
        artifact = answer

    return ChatResponse(
        answer=answer,
        sources=sources,
        artifact=artifact,
        provider="ollama",
    )
