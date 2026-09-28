"""Vector store: FAISS when available, exact numpy cosine search otherwise.

The corpus here is small (hundreds of chunks), so exact search is instant and
the FAISS path exists to show the production shape rather than for speed.
"""
from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import List, Tuple

import numpy as np

from .config import INDEX_DIR
from .corpus import Chunk


class VectorStore:
    def __init__(self, chunks: List[Chunk], vectors: np.ndarray, backend: str = "numpy"):
        if len(chunks) != vectors.shape[0]:
            raise ValueError("chunks and vectors must be the same length")
        self.chunks = chunks
        self.vectors = vectors.astype("float32")
        self.backend = backend
        self._faiss_index = None
        if backend == "faiss":
            import faiss  # noqa: WPS433
            index = faiss.IndexFlatIP(self.vectors.shape[1])
            index.add(self.vectors)
            self._faiss_index = index

    # ------------------------------------------------------------------ build
    @classmethod
    def build(cls, chunks: List[Chunk], vectors: np.ndarray) -> "VectorStore":
        try:
            import faiss  # noqa: F401,WPS433
            return cls(chunks, vectors, backend="faiss")
        except Exception:
            return cls(chunks, vectors, backend="numpy")

    # ----------------------------------------------------------------- search
    def search(self, query_vec: np.ndarray, top_k: int = 4) -> List[Tuple[Chunk, float]]:
        q = np.asarray(query_vec, dtype="float32").reshape(1, -1)
        if self._faiss_index is not None:
            scores, idx = self._faiss_index.search(q, top_k)
            pairs = zip(idx[0].tolist(), scores[0].tolist())
        else:
            sims = (self.vectors @ q.T).ravel()
            order = np.argsort(sims)[::-1][:top_k]
            pairs = ((int(i), float(sims[i])) for i in order)
        return [(self.chunks[i], float(s)) for i, s in pairs if i >= 0]

    # ------------------------------------------------------------- persistence
    def save(self, path: Path | None = None) -> Path:
        path = Path(path or INDEX_DIR)
        path.mkdir(parents=True, exist_ok=True)
        np.save(path / "vectors.npy", self.vectors)
        (path / "chunks.json").write_text(
            json.dumps([c.as_dict() for c in self.chunks], indent=1), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path | None = None) -> "VectorStore":
        path = Path(path or INDEX_DIR)
        vectors = np.load(path / "vectors.npy")
        raw = json.loads((path / "chunks.json").read_text(encoding="utf-8"))
        chunks = [Chunk(**c) for c in raw]
        return cls.build(chunks, vectors)


def save_embedder(embedder, path: Path | None = None) -> Path:
    """TF-IDF needs its fitted state; dense models are reloaded by name."""
    path = Path(path or INDEX_DIR)
    path.mkdir(parents=True, exist_ok=True)
    target = path / "embedder.pkl"
    with target.open("wb") as fh:
        pickle.dump(embedder, fh)
    return target


def load_embedder(path: Path | None = None):
    target = Path(path or INDEX_DIR) / "embedder.pkl"
    with target.open("rb") as fh:
        return pickle.load(fh)
