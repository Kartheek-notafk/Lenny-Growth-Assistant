# Architecture

React → FastAPI → Agent/skills → retrieval → LLM provider.

## Provider abstraction
The backend chooses Ollama or OpenAI using environment configuration. Application-level prompts do not need to change when switching providers.

## Retrieval
Transcript files are chunked with overlap. The starter uses lexical scoring for transparency. A stronger submission should use embeddings + a vector database and retain source metadata.

## Persistence
PostgreSQL stores conversation records with session IDs, roles, content, and timestamps.

## Resilience
Health endpoint, missing-key checks, HTTP error propagation, empty-retrieval handling, and configurable model endpoints are included.

## Artifact isolation
Generated HTML is shown in a sandboxed iframe. The generation policy also prohibits scripts, network requests, forms, and inline event handlers.
