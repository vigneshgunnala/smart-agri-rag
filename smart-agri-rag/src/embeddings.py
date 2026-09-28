"""Embedding backends.

Two of them, chosen at runtime:

* ``sentence-transformers`` - real dense embeddings, used when the package is
  installed (this is the default on a normal machine).
* ``tfidf`` - a scikit-learn TF-IDF + SVD fallback with no heavy downloads, so
  the project still runs, and still gets tested, in a slim environment.

Both expose the same interface, so nothing downstream cares which is active.
"""
from __future__ import annotations

from typing import List

import numpy as np

from .config import SETTINGS


class BaseEmbedder:
    name = "base"
    dim = 0

    def fit(self, texts: List[str]) -> "BaseEmbedder":
        return self

    def encode(self, texts: List[str]) -> np.ndarray:
        raise NotImplementedError


class SentenceTransformerEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = SETTINGS.embedding_model):
        from sentence_transformers import SentenceTransformer  # noqa: WPS433
        self.model = SentenceTransformer(model_name)
        self.name = f"sentence-transformers:{model_name}"
        self.dim = int(self.model.get_sentence_embedding_dimension())

    def encode(self, texts: List[str]) -> np.ndarray:
        vecs = self.model.encode(texts, normalize_embeddings=True,
                                 show_progress_bar=False)
        return np.asarray(vecs, dtype="float32")


class TfidfEmbedder(BaseEmbedder):
    """Lexical fallback: TF-IDF reduced with truncated SVD (LSA)."""

    def __init__(self, n_components: int = 256):
        from sklearn.decomposition import TruncatedSVD
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2),
                                          sublinear_tf=True, min_df=1)
        self._svd_cls = TruncatedSVD
        self.n_components = n_components
        self.svd = None
        self.name = "tfidf+svd"

    def fit(self, texts: List[str]) -> "TfidfEmbedder":
        matrix = self.vectorizer.fit_transform(texts)
        n = min(self.n_components, max(2, min(matrix.shape) - 1))
        self.svd = self._svd_cls(n_components=n, random_state=42).fit(matrix)
        self.dim = n
        return self

    def encode(self, texts: List[str]) -> np.ndarray:
        if self.svd is None:
            raise RuntimeError("TfidfEmbedder.fit() must be called before encode()")
        reduced = self.svd.transform(self.vectorizer.transform(texts))
        norms = np.linalg.norm(reduced, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (reduced / norms).astype("float32")


def get_embedder(backend: str | None = None) -> BaseEmbedder:
    backend = backend or SETTINGS.embedding_backend
    if backend in {"auto", "sentence-transformers"}:
        try:
            return SentenceTransformerEmbedder()
        except Exception:
            if backend != "auto":
                raise
    return TfidfEmbedder()
