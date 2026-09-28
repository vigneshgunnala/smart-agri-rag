"""FastAPI service. Run with: uvicorn api:app --reload"""
from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.config import SETTINGS
from src.rag import RAGPipeline

app = FastAPI(
    title="Smart Agri RAG",
    version="1.0.0",
    description="Retrieval-augmented irrigation Q&A grounded in FAO-56 agronomy "
                "and Irish climate context.",
)

pipeline: Optional[RAGPipeline] = None


@app.on_event("startup")
def _startup() -> None:
    global pipeline
    pipeline = RAGPipeline()


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["What does ET0 measure?"])
    top_k: Optional[int] = Field(None, ge=1, le=10)


class SourceOut(BaseModel):
    rank: int
    score: float
    source: str
    heading: str
    text: str


class AskResponse(BaseModel):
    question: str
    answer: str
    grounded: bool
    provider: str
    sources: List[SourceOut]


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "chunks": len(pipeline.store.chunks),
        "embedder": pipeline.embedder.name,
        "index_backend": pipeline.store.backend,
        "llm_provider": pipeline.provider,
    }


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    answer = pipeline.ask(req.question, top_k=req.top_k or SETTINGS.top_k)
    return AskResponse(
        question=answer.question,
        answer=answer.text,
        grounded=answer.grounded,
        provider=answer.provider,
        sources=[SourceOut(rank=p.rank, score=round(p.score, 4),
                           source=p.chunk.source, heading=p.chunk.heading,
                           text=p.chunk.text) for p in answer.passages],
    )
