---
title: Ask My Docs
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
---


# Ask My Docs

> A hybrid RAG system that turns uploaded PDFs into a queryable, multi-document knowledge base — combining keyword search, semantic retrieval, neural reranking, self-correcting generation, and Groq-powered LLM inference.

**[Live Demo →](https://huggingface.co/spaces/kashi-77/ask-my-docs)**

---

## What It Does

Pure vector search struggles with exact keywords, acronyms, and proper nouns — and even a well-retrieved context doesn't guarantee a grounded answer. Ask My Docs addresses both problems with a hybrid retrieval pipeline plus a self-correction loop:

1. **BM25 + ChromaDB** retrieve candidates via keyword and semantic search in parallel
2. **Cross-Encoder reranker** re-scores every `(query, chunk)` pair jointly for true relevance
3. **LLM (Groq)** generates an answer from the top-ranked context
4. **Grounding judge** scores the answer's faithfulness to the retrieved context (1–5)
5. **If the score is low**, a **query reformulator** rewrites the question and retries — up to 2 additional attempts — before falling back to an honest "insufficient information" response instead of hallucinating

Supports multiple documents in the same knowledge base — new uploads are added alongside existing ones, not replaced.

---

## Architecture

```text
User Query
    │
    ▼
Streamlit UI  ──►  FastAPI Backend
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
         BM25 Search        ChromaDB (Semantic)
              └─────────┬─────────┘
                        ▼
               Cross-Encoder Reranker
                        │
                        ▼
                Groq LLM — Generate Answer
                        │
                        ▼
              Grounding Judge (score 1–5)
                        │
              ┌─────────┴─────────┐
         score ≥ 4            score < 4
              │                   │
              ▼                   ▼
        Return Answer      Reformulate Query
                                   │
                          (retry, max 2x)
```

---

## Self-Correction Loop

Most RAG demos trust the LLM's output blindly — if retrieval pulls weak or irrelevant context, the model can still generate a confident, hallucinated answer. This project adds a verification layer:

- **Judge module** (`api/judge.py`) — an LLM call that rates how well the generated answer is supported by the retrieved context, with a short justification
- **Reformulator module** (`api/reformulator.py`) — rewrites the query when grounding is weak, without inventing new entities or details not present in the retrieved context
- **Attempt logging** (`api/logger.py`) — every attempt (original + retries) is logged with a shared session ID, enabling retry-rate and confidence analysis

This was validated against a real production-style failure mode during development: a shared vector store containing multiple unrelated documents caused one query to retrieve an out-of-context chunk and generate an unrelated answer. The fix was per-session document scoping discipline during testing — a good illustration of why retrieval quality, not just generation quality, determines whether a RAG system hallucinates.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI (async) |
| Vector Store | ChromaDB |
| Embeddings | `all-MiniLM-L6-v2` (Sentence Transformers) |
| Keyword Search | BM25 (rank-bm25) |
| Reranker | `ms-marco-MiniLM-L-6-v2` (Cross-Encoder) |
| LLM | Groq — `openai/gpt-oss-120b` |
| Self-Correction | Custom grounding judge + query reformulation loop |
| Deployment | Docker, Hugging Face Spaces |

---

## Project Structure

ask-my-docs/
├── api/
│ ├── main.py # FastAPI app — ingestion & query endpoints, retry orchestration
│ ├── judge.py # Grounding verification (scores answer vs. context)
│ ├── reformulator.py # Query rewriting on low-confidence retries
│ ├── logger.py # Per-attempt logging for evaluation
│ ├── data/ # PDF storage and vector index (gitignored)
│ └── Dockerfile
├── UI/
│ └── app.py # Streamlit frontend — chat interface with confidence badges
├── evaluation/
│ └── evaluation_results.json # 20-query grounding evaluation results
├── notebooks/ # RAG tuning experiments
├── .env # API keys — never commit this
├── .gitignore
├── Procfile # Hugging Face Spaces entry point
└── requirements.txt


---

## Run Locally

**Step 1 — Clone and install dependencies**

```bash
git clone https://github.com/Kashish-33/ask-my-docs.git
cd ask-my-docs
python -m venv rag_env
rag_env\Scripts\activate
pip install -r requirements.txt
```

**Step 2 — Add your API key**

Create a `.env` file in the root directory and add your Groq API key.
Get yours free at [console.groq.com](https://console.groq.com).

```env
GROQ_API_KEY=your_groq_api_key_here
```

> Never commit this file. It's already covered by `.gitignore`.

**Step 3 — Start the app**

```bash
# Terminal 1 — Backend
uvicorn api.main:app --reload --port 8000

# Terminal 2 — Frontend
streamlit run UI/app.py
```

**Step 4 — Or run with Docker**

```bash
docker build -t ask-my-docs .
docker run -p 8000:8000 --env-file .env ask-my-docs
```

---

## Why Hybrid Search + Reranking?

Vector search captures meaning but misses exact terms. BM25 matches keywords but misses paraphrase. Combining both gives broader, more robust candidate retrieval.

The Cross-Encoder re-scores candidates by attending to the full `(query, chunk)` pair simultaneously — unlike bi-encoders which encode them separately — so the LLM receives the most relevant context, not just the most similar.

---

## Evaluation

Tested against 20 queries split across two categories:
- **10 directly answerable** questions (grounded in uploaded document content)
- **10 intentionally unanswerable** questions (information not present in the document)

**Results:**
- 100% of answers scored ≥4/5 on grounding confidence
- 0% required a retry — the base generation prompt reliably refused to answer rather than hallucinate on missing information
- Retry mechanism separately stress-tested and confirmed functional under a forced-failure threshold

Full query-level results: [`evaluation/evaluation_results.json`](./evaluation/evaluation_results.json)

---

## License

MIT