# The Lenny Growth Assistant

A full-stack starter implementation for the Forward Deployed Engineer take-home assignment.

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
Copy `.env.example` to `.env`.

Default:
- `LLM_PROVIDER=ollama`
- `OLLAMA_MODEL=qwen2.5:7b`

Optional OpenAI:
- set `LLM_PROVIDER=openai`
- set `OPENAI_API_KEY`
- set `OPENAI_MODEL`

## Transcript ingestion
Put transcript `.txt` or `.md` files into `data/transcripts/`, then run:
```bash
python -m backend.scripts.ingest
```

The starter retrieval implementation is deliberately simple and inspectable. For a production-quality submission, replace it with embeddings/vector search and preserve source metadata.

## Tests
```bash
pip install -r backend/requirements.txt
pytest
```

## Notes
The assignment requires the submitted demo to run with Ollama, a cloud provider integration, FastAPI, PostgreSQL, source-grounded answers, a Ship 30 for 30 skill, and an in-app artifact viewer. This repository provides the implementation skeleton and working starter paths for those requirements.
