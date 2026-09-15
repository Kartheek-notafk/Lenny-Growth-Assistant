import logging
import httpx
from .config import settings

logger = logging.getLogger("lenny.llm")

SYSTEM = """You are The Lenny Growth Assistant.
Answer product and growth questions using ONLY the supplied transcript context
and the recent conversation history for follow-ups.
If the context does not support the answer, say that clearly instead of guessing.
Do not invent sources, guests, or claims that aren't in the provided context.
"""


class LLMUnavailableError(RuntimeError):
    """Raised when the configured provider can't be reached or isn't configured.
    Callers should treat this as a recoverable, user-facing condition — not a 500."""


async def generate(prompt: str) -> str:
    provider = settings.llm_provider.lower()

    if provider == "openai":
        if not settings.openai_api_key:
            raise LLMUnavailableError(
                "LLM_PROVIDER=openai but OPENAI_API_KEY is not set. "
                "Set it in .env or switch LLM_PROVIDER=ollama."
            )
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.responses.create(
                model=settings.openai_model,
                input=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                timeout=settings.llm_timeout_seconds,
            )
            return response.output_text
        except LLMUnavailableError:
            raise
        except Exception as exc:
            logger.exception("OpenAI call failed")
            raise LLMUnavailableError(f"OpenAI request failed: {exc}") from exc

    # default: ollama
    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    try:
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            r = await client.post(url, json={
                "model": settings.ollama_model,
                "prompt": SYSTEM + "\n\n" + prompt,
                "stream": False,
            })
            r.raise_for_status()
            return r.json()["response"]
    except httpx.ConnectError as exc:
        raise LLMUnavailableError(
            f"Could not reach Ollama at {settings.ollama_base_url}. "
            "Is `ollama serve` running and is the model pulled?"
        ) from exc
    except httpx.TimeoutException as exc:
        raise LLMUnavailableError(
            f"Ollama timed out after {settings.llm_timeout_seconds}s generating a response."
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise LLMUnavailableError(f"Ollama returned an error: {exc.response.text}") from exc
