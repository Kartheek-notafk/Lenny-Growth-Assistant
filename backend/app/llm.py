import httpx
from .config import settings

SYSTEM = """You are The Lenny Growth Assistant.
Answer product and growth questions using ONLY the supplied transcript context.
If the context does not support the answer, say that clearly.
Do not invent sources or claims.
"""

async def generate(prompt: str) -> str:
    if settings.llm_provider.lower() == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is missing")
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.responses.create(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
        )
        return response.output_text

    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(url, json={
            "model": settings.ollama_model,
            "prompt": SYSTEM + "\n\n" + prompt,
            "stream": False,
        })
        r.raise_for_status()
        return r.json()["response"]
