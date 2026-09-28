"""The RAG pipeline: ingest -> retrieve -> ground -> answer with citations."""
from __future__ import annotations

import os
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from .config import INDEX_DIR, SETTINGS, SYSTEM_PROMPT
from .corpus import Chunk, load_chunks
from .embeddings import get_embedder
from .vectorstore import VectorStore, load_embedder, save_embedder


@dataclass
class Passage:
    rank: int
    score: float
    chunk: Chunk

    @property
    def citation(self) -> str:
        return f"[{self.rank}] {self.chunk.source} - {self.chunk.heading}"


@dataclass
class Answer:
    question: str
    text: str
    passages: List[Passage] = field(default_factory=list)
    provider: str = "extractive"
    grounded: bool = True

    def sources_block(self) -> str:
        return "\n".join(p.citation for p in self.passages)


# --------------------------------------------------------------------- ingest
def build_index(corpus_dir: Path | None = None, index_dir: Path | None = None) -> VectorStore:
    chunks = load_chunks(corpus_dir)
    texts = [c.text for c in chunks]
    embedder = get_embedder().fit(texts)
    vectors = embedder.encode(texts)
    store = VectorStore.build(chunks, vectors)
    store.save(index_dir or INDEX_DIR)
    save_embedder(embedder, index_dir or INDEX_DIR)
    return store


# ------------------------------------------------------------------ generation
def _pick_provider() -> str:
    choice = SETTINGS.llm_provider
    if choice != "auto":
        return choice
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("GROQ_API_KEY"):
        return "groq"
    return "none"


def _format_context(passages: List[Passage]) -> str:
    blocks = []
    for p in passages:
        blocks.append(f"[{p.rank}] ({p.chunk.source} - {p.chunk.heading})\n{p.chunk.text}")
    return "\n\n".join(blocks)


def _extractive_answer(question: str, passages: List[Passage]) -> str:
    """No-API-key mode: return the grounded passages with their citations.

    Honest about what it is - retrieval without generation - so the app still
    demonstrates the retrieval half of RAG for anyone who clones it without keys.
    """
    if not passages:
        return ("I don't have anything in the knowledge base that answers that. "
                "Try asking about ET0, crop coefficients, effective rainfall, "
                "soil available water, or how the irrigation model works.")
    lead = passages[0]
    body = textwrap.shorten(lead.chunk.text.replace("\n", " "), width=700, placeholder=" ...")
    others = ", ".join(f"[{p.rank}]" for p in passages[1:])
    tail = f"\n\nAlso relevant: {others}" if others else ""
    return (f"(retrieval-only mode - no LLM key set)\n\n"
            f"Most relevant passage [1]: {body}{tail}")


def _call_openai(question: str, context: str) -> str:
    from openai import OpenAI  # noqa: WPS433
    client = OpenAI()
    resp = client.chat.completions.create(
        model=SETTINGS.openai_model,
        temperature=SETTINGS.temperature,
        max_tokens=SETTINGS.max_tokens,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context passages:\n\n{context}\n\nQuestion: {question}"},
        ],
    )
    return resp.choices[0].message.content.strip()


def _call_groq(question: str, context: str) -> str:
    from groq import Groq  # noqa: WPS433
    client = Groq()
    resp = client.chat.completions.create(
        model=SETTINGS.groq_model,
        temperature=SETTINGS.temperature,
        max_tokens=SETTINGS.max_tokens,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context passages:\n\n{context}\n\nQuestion: {question}"},
        ],
    )
    return resp.choices[0].message.content.strip()


# ------------------------------------------------------------------- pipeline
class RAGPipeline:
    def __init__(self, index_dir: Path | None = None):
        index_dir = Path(index_dir or INDEX_DIR)
        if not (index_dir / "vectors.npy").exists():
            self.store = build_index(index_dir=index_dir)
        else:
            self.store = VectorStore.load(index_dir)
        self.embedder = load_embedder(index_dir)
        self.provider = _pick_provider()

    def retrieve(self, question: str, top_k: int | None = None) -> List[Passage]:
        k = top_k or SETTINGS.top_k
        qvec = self.embedder.encode([question])[0]
        hits = self.store.search(qvec, top_k=k)
        return [Passage(rank=i + 1, score=score, chunk=chunk)
                for i, (chunk, score) in enumerate(hits)
                if score >= SETTINGS.min_score]

    def ask(self, question: str, top_k: int | None = None) -> Answer:
        passages = self.retrieve(question, top_k)
        if not passages:
            return Answer(question=question,
                          text=("That isn't covered by the documents I have. I can answer "
                                "questions about evapotranspiration, crop coefficients, "
                                "effective rainfall, soil water, and how this irrigation "
                                "model is built and evaluated."),
                          passages=[], provider=self.provider, grounded=False)

        context = _format_context(passages)
        try:
            if self.provider == "openai":
                text = _call_openai(question, context)
            elif self.provider == "groq":
                text = _call_groq(question, context)
            else:
                text = _extractive_answer(question, passages)
        except Exception as exc:  # fail soft - a demo that 500s helps nobody
            text = _extractive_answer(question, passages) + f"\n\n(LLM call failed: {exc})"

        return Answer(question=question, text=text, passages=passages,
                      provider=self.provider, grounded=True)


if __name__ == "__main__":   # python -m src.rag  -> build the index
    store = build_index()
    print(f"indexed {len(store.chunks)} chunks ({store.backend} backend)")
