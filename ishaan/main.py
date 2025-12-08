"""
Keyword extraction from JD (multi-line safe)

Dynamic top-K for MCQs and coding questions

Difficulty & tag filtering

Pagination

Semantic embedding search using FAISS

Multi-source content (Postgres + MongoDB)
"""
import os
import faiss
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
import psycopg2
from transformers import pipeline
from sentence_transformers import SentenceTransformer

# -------------------------
# ENVIRONMENT VARIABLES
# -------------------------
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "talentshire")

POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME", "talentshire")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin@123")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

EMBED_DIM = 1024

# -------------------------
# DATABASE CONNECTIONS
# -------------------------
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client[MONGO_DB_NAME]
coding_questions_collection = mongo_db["coding_questions"]

pg_conn = psycopg2.connect(
    database=POSTGRES_DB_NAME,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
)
pg_cursor = pg_conn.cursor()

# -------------------------
# NLP MODELS
# -------------------------
keyword_model = pipeline("text2text-generation", model="google/flan-t5-base", device=-1)
embed_model = SentenceTransformer("BAAI/bge-m3", device="cpu")

# -------------------------
# FAISS INDEXES
# -------------------------
mcq_index = faiss.IndexFlatL2(EMBED_DIM)
coding_index = faiss.IndexFlatL2(EMBED_DIM)

mcq_data = []        # Store MCQ metadata (question, options)
coding_data = []     # Store coding question metadata

# -------------------------
# HELPERS
# -------------------------
def extract_keywords(jd_text: str, top_n=10):
    """Extract unique keywords from a job description"""
    prompt = f"Extract exactly {top_n} unique keywords from this job description, comma separated:\n{jd_text}"
    out = keyword_model(prompt, max_length=64, num_return_sequences=1)
    keywords = [k.strip().lower() for k in out[0]["generated_text"].split(",")]
    return list(dict.fromkeys(keywords))

def embed_text(text: str):
    """Get embedding for a text"""
    return np.array(embed_model.encode(text, normalize_embeddings=True), dtype="float32")

def embed_db_content():
    """Embed MCQs and coding questions into FAISS indexes"""
    global mcq_index, coding_index, mcq_data, coding_data

    # ---- MCQs ----
    pg_cursor.execute("SELECT question_text, option_a, option_b, option_c, option_d, correct_answer FROM mcq_questions")
    rows = pg_cursor.fetchall()
    mcq_vectors = []
    mcq_data = []
    for r in rows:
        text = r[0] + " " + " ".join(r[1:5])
        mcq_vectors.append(embed_text(text))
        mcq_data.append({
            "question": r[0],
            "options": {"A": r[1], "B": r[2], "C": r[3], "D": r[4]},
            "correct_answer": r[5]
        })
    if mcq_vectors:
        mcq_index.reset()
        mcq_index.add(np.array(mcq_vectors, dtype="float32"))

    # ---- Coding Questions ----
    coding_docs = list(coding_questions_collection.find({}))
    coding_vectors = []
    coding_data = []
    for doc in coding_docs:
        text = doc["title"] + ": " + doc["description"]
        coding_vectors.append(embed_text(text))
        coding_data.append(doc)
    if coding_vectors:
        coding_index.reset()
        coding_index.add(np.array(coding_vectors, dtype="float32"))

def search_index(keywords, data_list, index, top_k):
    """Generic FAISS search"""
    if not data_list:
        raise HTTPException(status_code=500, detail="Index not embedded yet.")
    query_vec = embed_text(" ".join(keywords)).reshape(1, -1)
    distances, indices = index.search(query_vec, min(top_k, len(data_list)))
    return [data_list[i] for i in indices[0]]

def search_mcq(keywords, top_k=5):
    return search_index(keywords, mcq_data, mcq_index, top_k)

def search_coding(keywords, top_k=5):
    return search_index(keywords, coding_data, coding_index, top_k)

# -------------------------
# FASTAPI APP
# -------------------------
app = FastAPI(title="TalentShire Interactive Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class JDInput(BaseModel):
    text: str

@app.on_event("startup")
def startup_event():
    print("Embedding DB content...")
    embed_db_content()
    print("Done embedding DB content.")

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/process-jd")
def process_jd(
    body: JDInput,
    mcq_top_k: int = Query(5, description="Number of MCQs to return"),
    coding_top_k: int = Query(5, description="Number of coding questions to return")
):
    """
    Process a Job Description:
    - Extract keywords
    - Search MCQs & Coding questions
    - Dynamic number of questions via query params
    """
    try:
        jd_text = body.text.replace("\n", " ").replace("\r", "")
        keywords = extract_keywords(jd_text)
        if not keywords:
            raise HTTPException(status_code=404, detail="No keywords extracted from JD.")
        
        mcqs = search_mcq(keywords, top_k=mcq_top_k)
        coding_questions = search_coding(keywords, top_k=coding_top_k)

        return {
            "jd_text": jd_text,
            "keywords": keywords,
            "mcq_questions": mcqs,
            "coding_questions": coding_questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
