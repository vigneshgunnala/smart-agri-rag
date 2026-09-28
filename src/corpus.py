"""Load the knowledge base and split it into retrievable chunks."""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

from .config import CORPUS_DIR, SETTINGS


@dataclass
class Chunk:
    id: str
    text: str
    source: str          # file name
    heading: str         # nearest markdown heading, for citations

    def as_dict(self) -> dict:
        return asdict(self)


def _split_sections(markdown: str) -> List[tuple[str, str]]:
    """Split on markdown headings so a chunk never straddles two topics."""
    lines = markdown.splitlines()
    sections, heading, buf = [], "", []
    for line in lines:
        if re.match(r"^#{1,6}\s", line):
            if buf:
                sections.append((heading, "\n".join(buf).strip()))
                buf = []
            heading = line.lstrip("#").strip()
        else:
            buf.append(line)
    if buf:
        sections.append((heading, "\n".join(buf).strip()))
    return [(h, t) for h, t in sections if t]


def _window(text: str, size: int, overlap: int) -> List[str]:
    if len(text) <= size:
        return [text]
    out, start = [], 0
    while start < len(text):
        end = start + size
        if end < len(text):                      # prefer to break at a sentence
            dot = text.rfind(". ", start + size // 2, end)
            if dot != -1:
                end = dot + 1
        out.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [c for c in out if c]


def load_chunks(corpus_dir: Path | None = None) -> List[Chunk]:
    corpus_dir = Path(corpus_dir or CORPUS_DIR)
    files = sorted(p for p in corpus_dir.glob("**/*") if p.suffix.lower() in {".md", ".txt"})
    if not files:
        raise FileNotFoundError(f"No .md or .txt documents found in {corpus_dir}")

    chunks: List[Chunk] = []
    for path in files:
        raw = path.read_text(encoding="utf-8")
        for heading, body in _split_sections(raw):
            for piece in _window(body, SETTINGS.chunk_size, SETTINGS.chunk_overlap):
                chunks.append(Chunk(
                    id=f"{path.stem}#{len(chunks)}",
                    text=piece,
                    source=path.name,
                    heading=heading or path.stem,
                ))
    return chunks
