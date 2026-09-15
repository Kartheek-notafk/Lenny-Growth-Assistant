# The Lenny Growth Assistant

A full-stack implementation for the Forward Deployed Engineer take-home assignment: a
session-aware, transcript-grounded assistant for product and growth questions, with a
Ship 30 for 30 essay skill and a sandboxed artifact viewer.

## Stack
- Backend: FastAPI + Python
- Agent layer: provider abstraction with Ollama and OpenAI adapters
- Knowledge base: transcript ingestion + lightweight lexical retrieval
- Persistence: PostgreSQL via SQLAlchemy
- Frontend: React + Vite
- Local LLM: Ollama
- Optional cloud LLM: OpenAI
- Artifact viewer: sandboxed iframe for generated HTML

## Quick start

### 1. Start infrastructure
```bash
docker compose up -d db
```

### 2. Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Ollama
Install Ollama, then:
```bash
ollama pull qwen2.5:7b
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

## Environment
Copy `.env.example` to `.env` (backend) and `frontend/.env.example` to `frontend/.env`
if you're not using the default `http://localhost:8000` API base.

Default:
- `LLM_PROVIDER=ollama`
- `OLLAMA_MODEL=qwen2.5:7b`

Optional OpenAI:
- set `LLM_PROVIDER=openai`
- set `OPENAI_API_KEY`
- set `OPENAI_MODEL` (default `gpt-4o-mini`)

Tuning (sensible defaults, rarely need changing):
- `RETRIEVAL_TOP_K` — chunks fed to the model per question (default `5`)
- `HISTORY_TURNS` — prior turns replayed for follow-up context (default `6`)
- `LLM_TIMEOUT_SECONDS` — provider call timeout (default `120`)

## Session handling
- `POST /api/sessions` issues a new `session_id`; the frontend calls this on load and
  on **New session**.
- Every turn is persisted to Postgres (`messages` table) with role, provider, and skill.
- `GET /api/sessions/{id}/messages` returns the full stored history for a session —
  used to verify persistence independent of the UI.
- Follow-up questions replay the last `HISTORY_TURNS` turns back into the prompt, so
  "what about for enterprise?" resolves against what was just discussed.

## Resilience
- Postgres unreachable at startup: the API still boots; `/health` reports `database: down`
  and chat requests degrade to ungrounded-but-functional rather than crashing.
- Ollama unreachable / times out / OpenAI key missing: the chat endpoint returns a normal
  200 with a clear explanation in `answer` (see `LLMUnavailableError` in `backend/app/llm.py`),
  never a bare 500.
- No transcript chunks match the question: the assistant says so explicitly
  (`grounded: false`) instead of guessing.

## Transcript ingestion
`data/transcripts/` already ships with 15 real episodes (~800 chunks) pulled from the
public [ChatPRD/lennys-podcast-transcripts](https://github.com/ChatPRD/lennys-podcast-transcripts)
archive — chosen for topic spread (positioning, pricing, retention, onboarding, PM craft,
leadership). Each file's YAML frontmatter (`guest`, `title`, `youtube_url`) is parsed and
carried through to every citation shown in the UI.

To add more episodes, drop additional `.md`/`.txt` transcript files into `data/transcripts/`
and sanity-check ingestion with:
```bash
cd backend
PYTHONPATH=. python scripts/ingest.py
```
This reports per-file chunk counts and parsed guest names before you start the server.
The running API loads and caches chunks lazily on first query — restart it (or call
`retrieval.load_chunks.cache_clear()`) to pick up newly added files.

Retrieval itself is deliberately simple and inspectable: word-overlap scoring over
overlapping chunks, not embeddings. `Chunk` / `retrieve()` is the seam to swap in a real
vector store without touching `agent.py` — see `docs/architecture.md` for the trade-off.

## Tests
```bash
pip install -r backend/requirements.txt
pytest
```

## Frontend
React + Vite, styled as a small "production desk" for the podcast archive: a dark
chrome shell frames a warm paper session surface, with citations rendered as cue-card
chips (guest + source file) under every grounded answer. Design rationale lives in
`docs/design.md`.

## Known gaps / next steps
- `docker-compose.yml` currently only runs Postgres — backend/frontend/Ollama one-command
  startup is not yet wired.
- No structured request tracing beyond basic access logs.
- Only 15 of 300+ available episodes are ingested (by design, for a fast demo — see
  `docs/PRD.md` for the scope rationale).
- Agent layer is a custom Python function, not the Pi Coding Agent harness referenced in
  the brief (Pi is TypeScript-native); documented as an assumption in `docs/PRD.md`.

