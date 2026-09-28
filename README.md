# 🌾 Smart Agri RAG — an irrigation assistant grounded in real agronomy

A retrieval-augmented question answering system for Irish irrigation decisions.
Ask it about evapotranspiration, crop coefficients, effective rainfall, soil
water, or how the underlying forecasting model works, and it answers **only**
from a curated knowledge base — with citations, and with a refusal when the
answer isn't in the corpus.

Built as a companion to [smart-irrigation-ireland](https://github.com/Vignesh22-hub/smart-irrigation-ireland),
which forecasts next-day net irrigation requirement for Irish counties.

> **Screenshot placeholder** — add `docs/screenshot.png` after your first run.

---

## Why this exists

Most RAG demos answer questions about a PDF. This one is built around a
decision someone actually makes: *should I irrigate tomorrow, or wait for the
rain?* The corpus is FAO-56 agronomy, Irish climate context, and the documented
method behind the forecasting model — so the assistant explains the reasoning
behind a recommendation rather than repeating the recommendation.

Three things it does that a minimal RAG demo doesn't:

1. **Refuses out-of-scope questions** instead of hallucinating an answer.
2. **Ships an evaluation harness** that runs with no API key, so the retrieval
   numbers below are reproducible by anyone who clones the repo.
3. **Degrades gracefully** — no LLM key, no FAISS, no GPU? It still runs, in
   retrieval-only mode, and says so.

---

## Results

Measured on 22 held-out questions (21 in-scope, 1 deliberately out-of-scope),
`top_k = 4`, using the dependency-free TF-IDF + SVD backend — the *worst-case*
configuration:

| Metric | Score | What it means |
|---|---|---|
| hit@4 | **1.000** | the correct source document is always in the top 4 passages |
| MRR | **0.833** | the correct passage is usually ranked first |
| answer terms present | **0.810** | the retrieved context contains the key terms the answer needs |
| refusal accuracy | **1.000** | out-of-scope questions are refused, not answered |

Reproduce with `python -m src.evaluate --top-k 4`. Installing
`sentence-transformers` switches on dense embeddings, which should match or beat
these numbers — re-run and update the table.

---

## Architecture

```
       documents (markdown)
                │
       heading-aware chunking          900 chars, 150 overlap, never
                │                      straddling two headings
        embeddings  ──────────────►  sentence-transformers (dense)
                │                      └─ or TF-IDF + SVD fallback
          vector index ────────────►  FAISS IndexFlatIP
                │                      └─ or exact numpy cosine
                │
  question ──► retrieve top-k ──► score threshold ──► in scope?
                                                  │            │
                                              no ─┘            └─ yes
                                               │                   │
                                    refuse honestly      grounded prompt
                                                                   │
                                                    OpenAI / Groq / extractive
                                                                   │
                                                      answer + [1][2] citations
```

Every layer has a fallback, which is the point: the system is useful on a
laptop with no keys and correct on a server with them.

---

## Quick start

```bash
git clone https://github.com/Vignesh22-hub/smart-agri-rag.git
cd smart-agri-rag
pip install -r requirements.txt

python -m src.rag                 # builds the index on first run
streamlit run app.py              # the UI
```

Optional, for written answers rather than retrieved passages:

```bash
cp .env.example .env              # then add OPENAI_API_KEY or GROQ_API_KEY
```

As an API:

```bash
uvicorn api:app --reload
curl -X POST localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I turn ET0 into crop demand for potatoes?"}'
```

---

## Project layout

```
smart-agri-rag/
├── app.py                 Streamlit UI with citations and source expanders
├── api.py                 FastAPI service (/ask, /health)
├── src/
│   ├── config.py          all tunables and the system prompt
│   ├── corpus.py          loading and heading-aware chunking
│   ├── embeddings.py      dense backend + TF-IDF fallback
│   ├── vectorstore.py     FAISS backend + numpy fallback, save/load
│   ├── rag.py             retrieve → ground → generate → cite
│   └── evaluate.py        hit@k, MRR, refusal accuracy, grounding
├── data/corpus/           the knowledge base (6 documents)
├── eval/qa_pairs.json     22 evaluation questions
└── tests/test_rag.py      7 tests, no API key needed
```

---

## Design decisions worth explaining in an interview

**Heading-aware chunking.** Splitting on markdown headings before windowing
stops a chunk from starting in "crop coefficients" and ending in "soil water".
Retrieval precision comes mostly from chunk boundaries, not from the model.

**A score threshold, not just top-k.** Top-k always returns k passages, even for
"what is the capital of France". Requiring a minimum similarity is what makes
refusal possible.

**Evaluation without an LLM.** Retrieval quality is where RAG systems actually
fail, and it can be measured deterministically. Generation quality needs a key,
so it sits behind a flag and never blocks CI.

**Fallbacks everywhere.** A demo that only runs with a paid key and a GPU is a
demo nobody clones.

---

## Extending it

- Point `data/corpus/` at your own documents and rebuild — nothing else changes
- Add a reranker (cross-encoder) between retrieval and generation
- Wire in RAGAS faithfulness / answer-relevancy when a key is available
- Swap the corpus loader for PDFs with `pypdf` if your sources are papers

## License

MIT — see [LICENSE](LICENSE).

## Author

**Vignesh Gunnala** — Data & AI Analyst, Limerick, Ireland
[LinkedIn](https://linkedin.com/in/vigneshgunnala) · [GitHub](https://github.com/Vignesh22-hub) · vigneshgunnala440@gmail.com
