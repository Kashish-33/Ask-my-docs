# Ask My Docs

> A hybrid RAG system that turns uploaded PDFs into a queryable knowledge base — combining keyword search, semantic retrieval, neural reranking, and Groq-powered LLM inference.



**[Live Demo →(https://kashi-77-ask-my-docs.hf.space)]**

---

## What It Does

Pure vector search struggles with exact keywords, acronyms, and proper nouns. Ask My Docs fixes this with a three-stage hybrid pipeline:

1. **BM25 + ChromaDB** retrieve candidates via keyword and semantic search in parallel
2. **Cross-Encoder reranker** re-scores every `(query, chunk)` pair jointly for true relevance
3. **Llama 3.3-70B on Groq** generates the final answer from the top-ranked context

---

## Architecture

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
               Groq — Llama 3.3-70B
                        │
                        ▼
                   Final Answer


## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI (async) |
| Vector Store | ChromaDB |
| Embeddings | `all-MiniLM-L6-v2` (Sentence Transformers) |
| Keyword Search | BM25 (rank-bm25) |
| Reranker | `ms-marco-MiniLM-L-6-v2` (Cross-Encoder) |
| LLM | Groq — Llama 3.3-70B-Versatile |
| Deployment | Docker, Hugging Face Spaces |


## Project Structure

```
ask-my-docs/
├── api/
│   ├── main.py          # FastAPI app — ingestion & query endpoints
│   ├── data/            # PDF storage and vector index
│   └── Dockerfile
├── UI/
│   └── app.py           # Streamlit frontend
├── notebooks/           # RAG tuning experiments
├── .env                 # API keys — never commit this
├── .gitignore
├── Procfile             # Hugging Face Spaces entry point
└── requirements.txt


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

```
# Terminal 1 — Backend
uvicorn api.main:app --reload --port 8000

# Terminal 2 — Frontend
streamlit run UI/app.py
```

**Step 4 — Or run with Docker**

```
docker build -t ask-my-docs .
docker run -p 8000:8000 --env-file .env ask-my-docs
```

---

## Why Hybrid Search + Reranking?

Vector search captures meaning but misses exact terms. BM25 matches keywords but misses paraphrase. Combining both gives broader, more robust candidate retrieval.

The Cross-Encoder re-scores candidates by attending to the full `(query, chunk)` pair simultaneously — unlike bi-encoders which encode them separately — so the LLM receives the most relevant context, not just the most similar.

---

## License

MIT