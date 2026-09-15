import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .models import ChatRequest, ChatResponse, NewSessionResponse, SessionHistoryResponse, MessageOut
from .db import init_db, db_healthy, get_history
from .agent import answer_question
from .config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("lenny.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_ok = init_db()
    logger.info(
        "Startup: db_initialized=%s provider=%s ollama_model=%s",
        db_ok, settings.llm_provider, settings.ollama_model,
    )
    yield


app = FastAPI(title="The Lenny Growth Assistant", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 1)
    logger.info("%s %s -> %s (%sms)", request.method, request.url.path,
                response.status_code, duration_ms)
    return response


@app.get("/health")
def health():
    """Component-level health, not just process-up — an evaluator can tell
    whether persistence is actually reachable without making a chat request."""
    return {
        "status": "ok",
        "provider": settings.llm_provider,
        "database": "up" if db_healthy() else "down",
    }


@app.post("/api/sessions", response_model=NewSessionResponse)
def new_session():
    return NewSessionResponse(session_id=str(uuid.uuid4()))


@app.get("/api/sessions/{session_id}/messages", response_model=SessionHistoryResponse)
def session_messages(session_id: str):
    rows = get_history(session_id, limit_turns=1000)
    return SessionHistoryResponse(
        session_id=session_id,
        messages=[MessageOut.model_validate(r) for r in rows],
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        return await answer_question(req)
    except Exception:
        logger.exception("Unhandled error answering session %s", req.session_id)
        raise HTTPException(status_code=500, detail="Internal error answering the request.")
