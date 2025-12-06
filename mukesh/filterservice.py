from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
import psycopg
import logging

# Set up logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Enum definitions for language and difficulty level
class LanguageEnum(str, Enum):
    python = "Python"
    java = "Java"
    sql = "SQL"

class DifficultyEnum(str, Enum):
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"

# Pydantic model for input validation
class FilterRequest(BaseModel):
    language: LanguageEnum
    difficulty_level: DifficultyEnum

# PostgreSQL connection function
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

# Function to fetch MCQs from PostgreSQL
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
        logger.error(f"Error fetching MCQs from PostgreSQL: {e}")
        raise HTTPException(status_code=500, detail="Error fetching MCQs")

# Initialize FastAPI app
app = FastAPI()

# Endpoint to filter MCQs based on language and difficulty
@app.post("/api/filter_mcqs")
async def filter_mcqs(filters: FilterRequest):
    """
    Fetch MCQs based on programming language and difficulty level.
    """
    try:
        # Fetch filtered MCQs from the database
        mcqs = fetch_mcqs(filters.language, filters.difficulty_level)

        if not mcqs:
            # If no MCQs are found, raise a 404 error
            raise HTTPException(status_code=404, detail="No MCQs found with these filters.")

        return {"mcqs": mcqs}

    except HTTPException as e:
        # If an HTTP exception occurs, re-raise it
        raise e
    except Exception as e:
        # Log and raise internal server errors for unexpected issues
        logger.error(f"Error fetching MCQs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")