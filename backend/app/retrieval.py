"""Transcript ingestion + retrieval.

Intentionally simple and inspectable: transcripts are chunked with overlap and
scored against the query with lexical (keyword-overlap) matching. This is a
documented trade-off (see docs/architecture.md) — swap `retrieve()` for an
embeddings + vector-store implementation without touching callers, since the
Chunk / retrieve() contract stays the same.
"""
import re
import logging
from pathlib import Path
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional

import yaml

logger = logging.getLogger("lenny.retrieval")

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "transcripts"

CHUNK_SIZE_WORDS = 350
CHUNK_OVERLAP_WORDS = 60


@dataclass
class Chunk:
    title: str          # episode title (from frontmatter, falls back to filename)
    source: str          # filename, used as a stable citation key
    text: str
    guest: Optional[str] = None
    url: Optional[str] = None


def _parse_transcript(path: Path):
    """Split a transcript.md file into (frontmatter dict, body text).
    Falls back gracefully if there is no YAML frontmatter or it's malformed."""
    raw = path.read_text(encoding="utf-8", errors="ignore")
    meta = {}
    body = raw
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            fm_text = raw[3:end]
            body = raw[end + 4:]
            try:
                meta = yaml.safe_load(fm_text) or {}
            except yaml.YAMLError:
                logger.warning("Could not parse frontmatter in %s", path.name)
    return meta, body


def _chunk_words(words: List[str], size: int, overlap: int):
    step = max(size - overlap, 1)
    for i in range(0, len(words), step):
        part = words[i:i + size]
        if part:
            yield " ".join(part)


@lru_cache(maxsize=1)
def load_chunks() -> List[Chunk]:
    """Loaded once per process and cached. Call load_chunks.cache_clear() to
    force a refresh (e.g. after adding new transcript files) without a restart."""
    chunks: List[Chunk] = []
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(DATA_DIR.glob("*")):
        if path.suffix.lower() not in {".txt", ".md"}:
            continue
        if path.name.upper() == "README.MD":
            continue  # folder documentation, not transcript content
        meta, body = _parse_transcript(path)
        title = meta.get("title") or path.stem
        guest = meta.get("guest")
        url = meta.get("youtube_url")
        words = body.split()
        for part in _chunk_words(words, CHUNK_SIZE_WORDS, CHUNK_OVERLAP_WORDS):
            chunks.append(Chunk(title=title, source=path.name, text=part, guest=guest, url=url))
    logger.info("Loaded %d chunks from %d transcript file(s)", len(chunks),
                len(list(DATA_DIR.glob("*.md"))) + len(list(DATA_DIR.glob("*.txt"))))
    return chunks


def retrieve(query: str, k: int = 5) -> List[Chunk]:
    terms = set(re.findall(r"\w+", query.lower()))
    scored = []
    for c in load_chunks():
        words = set(re.findall(r"\w+", c.text.lower()))
        score = len(terms & words)
        if score:
            scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:k]]
