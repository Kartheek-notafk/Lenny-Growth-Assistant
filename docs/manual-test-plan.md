# Manual Test Plan

1. Start PostgreSQL, FastAPI, Ollama, and the frontend.
2. Ask a question supported by a transcript and verify sources appear.
3. Ask an unsupported question and verify the assistant refuses to invent an answer.
4. Ask for a Ship 30 essay and verify headings, hook, takeaway, and sources.
5. Ask for an HTML artifact and verify it renders in the Artifact Viewer.
6. Switch `LLM_PROVIDER` to `openai`, configure the key, restart the backend, and verify the same UI works.
7. Stop Ollama and verify the UI reports backend/model failure rather than silently fabricating an answer.
