# PRD — The Lenny Growth Assistant

## User and problem
Primary users are product and growth practitioners who want reliable advice grounded in Lenny's Podcast transcripts without learning prompts, models, or infrastructure.

## Success metrics
- ≥90% of evaluated answers contain a relevant transcript source.
- 100% of unsupported questions receive an explicit insufficient-evidence response.
- Fresh evaluator can run the app from the README in under 10 minutes after prerequisites are installed.

## Assumptions
- Transcript files are supplied as text/Markdown.
- Local Ollama is available for the demo.
- PostgreSQL is available locally or through a managed service.

## Scope
Included: conversational RAG, session-aware API shape, model provider toggle, Ship 30 skill, artifact viewer, persistence foundation, tests.
Excluded from the starter: production authentication, advanced vector infrastructure, multi-tenant permissions, external web search.

## Risks and trade-offs
- Hallucination: restrict generation to retrieved context.
- Latency: local models may be slower.
- Cost: Ollama is free to run locally; cloud provider is optional.
- HTML security: sandbox generated HTML and disallow scripts in the generation policy.
