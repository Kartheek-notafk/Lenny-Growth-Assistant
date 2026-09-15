"""Manual ingestion check: loads every transcript in data/transcripts/ and
reports what was parsed, so you can confirm new files are chunkable before
starting the server. The API loads/caches chunks lazily on first query;
this script exists for a fast, standalone sanity check.
"""
from collections import Counter
from app.retrieval import load_chunks

def main():
    chunks = load_chunks()
    if not chunks:
        print("No chunks loaded. Add .txt/.md transcript files to data/transcripts/.")
        return
    by_source = Counter(c.source for c in chunks)
    print(f"Loaded {len(chunks)} chunks from {len(by_source)} transcript file(s):\n")
    for source, count in sorted(by_source.items()):
        guest = next(c.guest for c in chunks if c.source == source) or "unknown guest"
        print(f"  {source:40s} guest={guest:25s} chunks={count}")
    print("\nFor a stronger submission, replace lexical scoring in retrieval.py")
    print("with embeddings + a vector store, keeping the Chunk/retrieve() contract.")

if __name__ == "__main__":
    main()
