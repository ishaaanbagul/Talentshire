from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
import psycopg
from pymongo import MongoClient
import logging

# Set up logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Enum definitions
class LanguageEnum(str, Enum):
    python = "Python"
    java = "Java"
    sql = "SQL"

class DifficultyEnum(str, Enum):
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"

# Pydantic model for MCQ filters
class FilterRequest(BaseModel):
    language: LanguageEnum
    difficulty_level: DifficultyEnum

# NEW: Pydantic model for coding question filters
class CodingFilterRequest(BaseModel):
    title: str | None = None
    labels: list[str] | None = None
    difficulty: DifficultyEnum | None = None


# PostgreSQL connection (MCQs)
def get_db_connection():
    try:
        conn = psycopg.connect(
            dbname="talentshire",
            user="postgres",
            password="admin@123",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")


# MongoDB connection (coding questions)
def get_mongo_connection():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["talentshire"]
        return db
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise HTTPException(status_code=500, detail="MongoDB connection failed")


# Fetch MCQs from PostgreSQL
def fetch_mcqs(language: str, difficulty: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            SELECT mcq_id, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM mcq_questions
            WHERE language = %s AND difficulty_level = %s
            ORDER BY mcq_id;
        """
        cur.execute(query, (language, difficulty))
        rows = cur.fetchall()

        mcqs = []
        for row in rows:
            mcqs.append({
                "mcq_id": row[0],
                "question_text": row[1],
                "option_a": row[2],
                "option_b": row[3],
                "option_c": row[4],
                "option_d": row[5],
                "correct_answer": row[6]
            })

        cur.close()
        conn.close()

        return mcqs

    except Exception as e:
        logger.error(f"Error fetching MCQs: {e}")
        raise HTTPException(status_code=500, detail="Error fetching MCQs")


# Fetch coding questions from MongoDB (OR-based search)
def fetch_coding_questions(title: str | None, labels: list[str] | None, difficulty: str | None):
    try:
        db = get_mongo_connection()
        collection = db["coding_questions"]

        query = {"$or": []}

        # Title filter (case-insensitive regex)
        if title:
            query["$or"].append({"title": {"$regex": title, "$options": "i"}})

        # Label filter (any label match)
        if labels and len(labels) > 0:
            query["$or"].append({"labels": {"$in": labels}})

        # Difficulty filter
        if difficulty:
            query["$or"].append({"difficulty": difficulty})

        # If no filters are provided → return all documents
        if len(query["$or"]) == 0:
            query = {}

        results = list(collection.find(query, {"_id": 0}))  # hide Mongo _id

        return results

    except Exception as e:
        logger.error(f"Error fetching coding questions from MongoDB: {e}")
        raise HTTPException(status_code=500, detail="Error fetching coding questions")


# Initialize FastAPI
app = FastAPI()

# MCQ endpoint
@app.post("/api/filter_mcqs")
async def filter_mcqs(filters: FilterRequest):
    try:
        mcqs = fetch_mcqs(filters.language, filters.difficulty_level)

        if not mcqs:
            raise HTTPException(status_code=404, detail="No MCQs found with these filters.")

        return {"mcqs": mcqs}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching MCQs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# NEW coding question endpoint
@app.post("/api/filter_coding_questions")
async def filter_coding_questions(filters: CodingFilterRequest):
    try:
        coding_questions = fetch_coding_questions(
            title=filters.title,
            labels=filters.labels,
            difficulty=filters.difficulty,
        )

        if not coding_questions:
            raise HTTPException(status_code=404, detail="No coding questions found with these filters.")

        return {"coding_questions": coding_questions}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching coding questions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")