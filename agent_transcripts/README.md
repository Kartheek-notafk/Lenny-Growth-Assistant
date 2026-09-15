# Agent Transcripts

Place coding-agent transcripts/logs here for the final submission, including failed attempts and corrections. Remove secrets and sensitive data before committing.


Went through the whole zip. Good news: the skeleton is coherent and every required file exists. Bad news: it's still a skeleton — most files are 15–50 lines, and several rubric items are either stubbed, hardcoded, or not actually wired up yet. Here's the honest state, then a plan for the ~1 day you have left.

What's actually working
FastAPI app boots, has /health and /api/chat, Pydantic request/response models
Retrieval does real (if crude) chunking + lexical keyword-overlap scoring over data/transcripts/
Ollama and OpenAI are both wired into llm.py behind a config flag
Frontend is a real React/Vite app with a chat pane + sandboxed-iframe artifact viewer (sandbox="" with no allow-scripts — good instinct)
Docs exist for PRD/architecture/design/manual test plan
What's missing or just stubbed, mapped to the rubric

Grounding / RAG (core requirement)

data/transcripts/ is empty — nothing has actually been ingested. You'll need real transcript files before this can be graded on "source-grounded answers."
Retrieval is exact-keyword-overlap only, no embeddings — acceptable as a documented simplification, but the assignment explicitly calls out chunking/indexing/refresh, so this needs to be a stated trade-off, not silent.

Session persistence (core requirement)

db.py defines a Conversation table but agent.py never writes to it, and never reads prior turns back in. Right now every message is stateless — "preserve session context" and "follow-up questions" aren't actually implemented.

Agent layer — "Pi Coding Agent"

Worth flagging: Pi Coding Agent is a real (TypeScript) agent harness (@earendil-works/pi-coding-agent), not something your Python backend currently uses at all — agent.py is a hand-rolled function. This is a legitimate scope decision to document explicitly in the PRD ("used a custom Python agent layer instead of the Pi harness because Pi is TS-native and the rest of the stack is FastAPI/Python; documented as an assumption") rather than something to quietly ignore.

Ship 30 skill

SHIP_30_SKILL is a bullet list, not principles actually extracted from the Ship 30 for 30 guide as the brief asks ("encode the writing principles in the skill rather than an unstructured one-off prompt").

Model toggle visibility

UI header hardcodes Provider: Ollama regardless of actual config — doesn't reflect real state.

Deployment/ops

docker-compose.yml only runs Postgres — not the "one-command startup" for backend/frontend/Ollama.
No structured logging anywhere; no handling for DB-down, Ollama-down mid-request beyond a generic try/except.
.env.example has OPENAI_MODEL=gpt-5.6-luna, which isn't a real model name — needs fixing before submission.

Tests / agent transcripts

Only one health-check test exists. No retrieval, routing, or persistence tests.
agent_transcripts/ is empty — you need your actual coding-agent session logs in there for submission.


What's done (backend — core correctness)
Real data: Lenny's Podcast episode transcripts (~800 chunks) pulled from the public ChatPRD archive, replacing the empty data/transcripts/ folder. YAML frontmatter (guest, title, YouTube URL) is parsed and carried through to citations.
Session memory: messages table in Postgres actually gets written to now (user + assistant turns), and follow-up questions replay the last N turns back into the prompt — this was completely missing before.
New endpoints: POST /api/sessions (new chat) and GET /api/sessions/{id}/messages (inspect stored history).
Resilience: Ollama-down, OpenAI-key-missing, and timeout cases now return a clear 200 with an explanation instead of a raw 500; DB-down degrades /health instead of crashing; ungrounded questions short-circuit before ever calling the LLM.
Fixed the fake model name (gpt-5.6-luna → gpt-4o-mini) and added RETRIEVAL_TOP_K/HISTORY_TURNS/LLM_TIMEOUT_SECONDS tuning.
11 passing tests covering retrieval, session memory, grounding, LLM-failure handling, and API contracts — verified end-to-end against the real backend (health check, session creation, chat with Ollama intentionally unreachable, history persistence all confirmed working).
README updated to match reality (setup steps, ingestion instructions, resilience behavior, known gaps).
What's done (frontend — the "very good and unique" redesign)

Rebuilt from the generic template into a distinct "production desk" concept: dark chrome shell framing a warm paper "session" surface, transcript-style turns instead of chat bubbles, citations as cue-card chips (guest + source file), Fraunces/IBM Plex typography, a sandboxed (sandbox="") artifact iframe with a visible security note. Split into proper components (App.jsx, SessionFeed, Composer, ArtifactPanel, StatusCluster, api.js). Builds clean with npm run build.

Explicitly flagged gaps (in README, not hidden)
docker-compose.yml still only runs Postgres — no one-command full-stack startup yet.
The "Pi Coding Agent" requirement isn't implemented — it's a TypeScript harness, awkward to bolt onto a Python FastAPI backend; flagged as a documented assumption rather than silently ignored.
PRD/architecture/design docs haven't been updated yet to match the schema and endpoint changes — README has, but the deeper docs are still describing the old skeleton.