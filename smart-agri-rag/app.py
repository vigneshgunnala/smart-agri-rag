"""Streamlit UI. Run with: streamlit run app.py"""
from __future__ import annotations

import streamlit as st

from src.config import SETTINGS
from src.rag import RAGPipeline

st.set_page_config(page_title="Smart Agri RAG — Irish irrigation assistant",
                   page_icon="🌾", layout="centered")


@st.cache_resource(show_spinner="Building the index…")
def get_pipeline() -> RAGPipeline:
    return RAGPipeline()


pipe = get_pipeline()

st.title("🌾 Irish irrigation assistant")
st.caption("Retrieval-augmented answers grounded in FAO-56 agronomy, Irish climate "
           "context, and the method behind the smart-irrigation model. "
           "Every answer cites the passages it used.")

with st.sidebar:
    st.subheader("Setup")
    st.write(f"**Embeddings:** `{pipe.embedder.name}`")
    st.write(f"**Index:** `{pipe.store.backend}`, {len(pipe.store.chunks)} chunks")
    st.write(f"**Generation:** `{pipe.provider}`")
    if pipe.provider == "none":
        st.info("No LLM key set, so the app runs in retrieval-only mode: it shows "
                "the grounded passages instead of a written answer. Set "
                "`OPENAI_API_KEY` or `GROQ_API_KEY` for full answers.")
    top_k = st.slider("Passages to retrieve", 1, 8, SETTINGS.top_k)
    st.divider()
    st.caption("Ask about ET0, crop coefficients, effective rainfall, soil "
               "available water, or how the model is built and evaluated.")

EXAMPLES = [
    "What does ET0 actually measure?",
    "How do I turn ET0 into crop water demand for potatoes?",
    "Why would an Irish farm need irrigation when it rains so much?",
    "What exactly does the model predict, and what does it get compared against?",
    "How should I choose the millimetre threshold for irrigating?",
]

if "question" not in st.session_state:
    st.session_state.question = ""

cols = st.columns(2)
for i, example in enumerate(EXAMPLES):
    if cols[i % 2].button(example, use_container_width=True):
        st.session_state.question = example

question = st.text_input("Your question", value=st.session_state.question,
                         placeholder="e.g. What is effective rainfall?")

if question:
    with st.spinner("Retrieving…"):
        answer = pipe.ask(question, top_k=top_k)

    if not answer.grounded:
        st.warning(answer.text)
    else:
        st.markdown(answer.text)
        st.divider()
        st.subheader("Sources")
        for p in answer.passages:
            with st.expander(f"[{p.rank}] {p.chunk.source} — {p.chunk.heading}  ·  "
                             f"score {p.score:.3f}"):
                st.write(p.chunk.text)
