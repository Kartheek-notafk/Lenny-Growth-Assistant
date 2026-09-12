from pathlib import Path
from app.retrieval import load_chunks

chunks = load_chunks()
print(f"Loaded {len(chunks)} transcript chunks.")
print("For the production version, persist embeddings/chunks in a vector store.")
