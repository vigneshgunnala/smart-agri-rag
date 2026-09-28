"""Tests that run with no API key and no model downloads."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.corpus import load_chunks               # noqa: E402
from src.evaluate import evaluate, grounding_score  # noqa: E402
from src.rag import RAGPipeline                  # noqa: E402


@pytest.fixture(scope="module")
def pipe() -> RAGPipeline:
    return RAGPipeline()


def test_corpus_loads_and_chunks():
    chunks = load_chunks()
    assert len(chunks) > 10
    assert all(c.text.strip() for c in chunks)
    assert all(c.source.endswith((".md", ".txt")) for c in chunks)


def test_chunks_are_bounded():
    for chunk in load_chunks():
        assert len(chunk.text) <= 1200, f"chunk too long: {chunk.id}"


def test_retrieval_finds_the_right_document(pipe):
    passages = pipe.retrieve("What is the crop coefficient for potatoes?")
    assert passages, "expected at least one passage"
    assert "03_crop_coefficients.md" in {p.chunk.source for p in passages}


def test_answer_carries_citations(pipe):
    answer = pipe.ask("How is net irrigation requirement defined?")
    assert answer.grounded
    assert answer.passages
    assert answer.sources_block()


def test_out_of_scope_is_refused(pipe):
    answer = pipe.ask("Who won the 2014 World Cup?")
    assert not answer.grounded or "don't have" in answer.text.lower()


def test_grounding_score_bounds(pipe):
    answer = pipe.ask("What does ET0 measure?")
    score = grounding_score(answer.text, answer.passages)
    assert 0.0 <= score <= 1.0


def test_retrieval_quality_meets_threshold():
    metrics = evaluate(top_k=4)
    assert metrics["hit@4"] >= 0.8, metrics
    assert metrics["mrr"] >= 0.5, metrics
    assert metrics["refusal_accuracy"] == 1.0, metrics
