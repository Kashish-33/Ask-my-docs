from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import  SentenceTransformer, CrossEncoder
from groq import Groq
from dotenv import load_dotenv
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np
import os

load_dotenv()



app = FastAPI()


client_db = chromadb.PersistentClient(path="./data/chromadb_rag")
collection = client_db.get_or_create_collection(name="my_pdf_docs")

all_data = collection.get()
chunks = all_data['documents']

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class QueryRequest(BaseModel):
    question: str


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    temp_path = f"./data/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)

    text = ""
    with pdfplumber.open(temp_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    new_chunks = splitter.split_text(text)

    embeddings = embed_model.encode(new_chunks).tolist()

    # Purana data clear karo
    existing = collection.get()
    if existing['ids']:
        collection.delete(ids=existing['ids'])

    collection.add(
        documents=new_chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(new_chunks))]
    )

    return {"message": f" {file.filename} processed!", "chunks": len(new_chunks)}

@app.get("/")
def home():
    return {"status": "Ask My Docs API is running!"}


@app.post("/ask")
def ask(request: QueryRequest):
    query = request.question
    
    all_data = collection.get()
    chunks = all_data['documents']
    
    tokenized = [c.lower().split() for c in chunks]
    bm25 = BM25Okapi(tokenized)
    bm25_scores = bm25.get_scores(query.lower().split())
    top_bm25 = [chunks[i] for i in np.argsort(bm25_scores)[::-1][:5]]

    
    vector_results = collection.query(query_texts=[query], n_results=5)
    vector_chunks = vector_results['documents'][0]

    
    combined = list(dict.fromkeys(top_bm25 + vector_chunks))

    
    pairs = [[query, chunk] for chunk in combined]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, combined), reverse=True)
    top_chunks = [chunk for _, chunk in ranked[:3]]

    
    context = "\n\n".join(top_chunks)
    prompt = f"""
Answer the question using ONLY the context below.
If answer is not in context, say "I don't know".
At the end mention which part of context you used.

Context:
{context}

Question: {query}
"""
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "question": query,
        "answer": response.choices[0].message.content,
        "top_chunks": top_chunks
    }