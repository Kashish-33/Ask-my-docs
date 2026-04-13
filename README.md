#  Ask My Docs

A production RAG (Retrieval Augmented Generation) application that lets you upload any PDF and ask questions about it.

##  Architecture

User → Streamlit UI → FastAPI → ChromaDB + BM25 → CrossEncoder Reranker → Groq LLM → Answer

##  Tech Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI
- **Vector DB:** ChromaDB
- **Embeddings:** Sentence Transformers (all-MiniLM-L6-v2)
- **Retrieval:** Hybrid (BM25 + Semantic Search)
- **Reranking:** CrossEncoder (ms-marco-MiniLM-L-6-v2)
- **LLM:** Groq (Llama 3.3-70b-versatile)

##  Run Locally

1. Clone the repo
   
   git clone https://github.com/Kashish-33/ask-my-docs.git
   cd ask-my-docs

2. Create virtual environment
   
   python -m venv rag_env
   rag_env\Scripts\activate
   pip install -r requirements.txt

3. Add your API key in .env file
   
   GROQ_API_KEY=your_groq_api_key_here

4. Start FastAPI server
   
   uvicorn main:app --reload

5. Start Streamlit UI
   
   streamlit run app.py

##  Project Structure

ask-my-docs/
├── main.py          # FastAPI backend
├── app.py           # Streamlit frontend  
├── data/            # PDF storage
├── notebooks/       # Experimentation notebooks
├── requirements.txt
└── .env             # API keys (not pushed)