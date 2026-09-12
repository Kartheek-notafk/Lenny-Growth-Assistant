from pathlib import Path
import re
from dataclasses import dataclass

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "transcripts"

@dataclass
class Chunk:
    title: str
    source: str
    text: str

def load_chunks():
    chunks = []
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for path in DATA_DIR.glob("*"):
        if path.suffix.lower() not in {".txt", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        words = text.split()
        size = 350
        overlap = 50
        for i in range(0, len(words), size - overlap):
            part = " ".join(words[i:i+size])
            if part:
                chunks.append(Chunk(path.stem, path.name, part))
    return chunks

def retrieve(query: str, k: int = 5):
    terms = set(re.findall(r"\w+", query.lower()))
    scored = []
    for c in load_chunks():
        words = set(re.findall(r"\w+", c.text.lower()))
        score = len(terms & words)
        if score:
            scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:k]]
