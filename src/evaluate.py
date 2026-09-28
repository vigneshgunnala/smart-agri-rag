"""Evaluation harness.

Retrieval quality is measured without any API key, which means the numbers are
reproducible by anyone who clones the repo:

* **hit@k**  - did the correct source document appear in the top k passages
* **MRR**    - 1/rank of the first correct passage, averaged
* **refusal accuracy** - does an out-of-scope question get refused rather than
  answered from thin air

If an LLM key is present, an optional grounding check also measures how much of
the generated answer is supported by the retrieved passages (a cheap, local
stand-in for RAGAS faithfulness; RAGAS itself is wired in behind a flag).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

from .config import EVAL_PATH, SETTINGS
from .rag import RAGPipeline


def load_eval_set(path: Path | None = None) -> List[dict]:
    return json.loads(Path(path or EVAL_PATH).read_text(encoding="utf-8"))


def _tokens(text: str) -> set:
    return {t for t in re.findall(r"[a-z0-9\.]+", text.lower()) if len(t) > 2}


def grounding_score(answer_text: str, passages) -> float:
    """Share of the answer's content words that appear in the retrieved context."""
    if not passages:
        return 0.0
    answer_tokens = _tokens(answer_text)
    if not answer_tokens:
        return 0.0
    context_tokens = set()
    for p in passages:
        context_tokens |= _tokens(p.chunk.text)
    return len(answer_tokens & context_tokens) / len(answer_tokens)


def evaluate(top_k: int | None = None, generate: bool = False) -> Dict[str, float]:
    pipe = RAGPipeline()
    cases = load_eval_set()
    k = top_k or SETTINGS.top_k

    in_scope = [c for c in cases if c["expected_source"]]
    out_scope = [c for c in cases if not c["expected_source"]]

    hits, reciprocal_ranks, keyword_hits, grounding = 0, [], 0, []

    for case in in_scope:
        passages = pipe.retrieve(case["question"], top_k=k)
        sources = [p.chunk.source for p in passages]
        if case["expected_source"] in sources:
            hits += 1
            reciprocal_ranks.append(1 / (sources.index(case["expected_source"]) + 1))
        else:
            reciprocal_ranks.append(0.0)

        context = " ".join(p.chunk.text.lower() for p in passages)
        if all(term.lower() in context for term in case["must_contain"]):
            keyword_hits += 1

        if generate:
            ans = pipe.ask(case["question"], top_k=k)
            grounding.append(grounding_score(ans.text, ans.passages))

    refusals = 0
    for case in out_scope:
        ans = pipe.ask(case["question"], top_k=k)
        refused = (not ans.grounded) or ("don't have" in ans.text.lower())
        refusals += int(refused)

    metrics = {
        f"hit@{k}": hits / len(in_scope),
        "mrr": sum(reciprocal_ranks) / len(in_scope),
        "answer_terms_present": keyword_hits / len(in_scope),
        "refusal_accuracy": refusals / len(out_scope) if out_scope else float("nan"),
        "questions": float(len(cases)),
    }
    if grounding:
        metrics["grounding"] = sum(grounding) / len(grounding)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the RAG pipeline")
    parser.add_argument("--top-k", type=int, default=None)
    parser.add_argument("--generate", action="store_true",
                        help="also generate answers and score grounding")
    parser.add_argument("--out", type=str, default="eval/results.json")
    args = parser.parse_args()

    metrics = evaluate(args.top_k, args.generate)
    width = max(len(k) for k in metrics)
    for key, value in metrics.items():
        print(f"{key:<{width}}  {value:.3f}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"\nwritten to {out}")


if __name__ == "__main__":
    main()
