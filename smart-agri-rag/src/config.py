"""Central configuration. Everything tunable lives here."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "data" / "corpus"
INDEX_DIR = ROOT / "data" / "index"
EVAL_PATH = ROOT / "eval" / "qa_pairs.json"


@dataclass(frozen=True)
class Settings:
    # chunking
    chunk_size: int = 900          # characters, not tokens - keeps it dependency-free
    chunk_overlap: int = 150

    # retrieval
    top_k: int = 4
    min_score: float = 0.05        # below this, treat as "not in the corpus"

    # embeddings: "auto" uses sentence-transformers when installed, else TF-IDF
    embedding_backend: str = os.getenv("EMBEDDING_BACKEND", "auto")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # generation: "auto" picks the first provider with a key, else extractive
    llm_provider: str = os.getenv("LLM_PROVIDER", "auto")   # auto | openai | groq | none
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    temperature: float = 0.0
    max_tokens: int = 600


SETTINGS = Settings()

SYSTEM_PROMPT = """You are an irrigation advisor for Irish farms.

Rules you must follow:
1. Answer ONLY from the numbered context passages provided. They are your only
   source of truth.
2. Cite the passages you used as [1], [2] etc., inline, where the claim is made.
3. If the context does not contain the answer, say so plainly and state what
   information would be needed. Never fill a gap with general knowledge.
4. Give numbers with their units (mm, mm/day, degrees Celsius).
5. Be concise and practical. A grower is reading this, not a researcher.
"""
