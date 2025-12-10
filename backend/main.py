"""
Monolithic Talent Assessment Backend
====================================

This FastAPI app consolidates all services into a single monolithic backend.

Services included:

1. Test Storage Service - Working code intact
2. Admin Panel Service - test_assignments endpoints
3. Test–Candidate Mapping Service 
4. Question Fetching Service (MCQ + Coding + Unified)
5. Candidate Answers Storage Service
6. MCQ Filtering Service - Fetch MCQs by language and difficulty
"""

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from enum import Enum
from typing import List
import logging
import psycopg
import uuid
from datetime import datetime

# ---------- Logging ----------
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- FastAPI App ----------
app = FastAPI()

# ---------- PostgreSQL Connection ----------
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

# ---------- Enums ----------
class LanguageEnum(str, Enum):
    python = "Python"
    java = "Java"
    sql = "SQL"

class DifficultyEnum(str, Enum):
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"

class TestStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    completed = "completed"

class QuestionTypeEnum(str, Enum):
    multiple_choice = "multiple_choice"
    coding = "coding"
    unified = "unified"

class AssignmentStatusEnum(str, Enum):
    pending = "pending"
    scheduled = "scheduled"
    completed = "completed"

# ---------- Pydantic Models ----------
class FilterRequest(BaseModel):
    language: LanguageEnum
    difficulty_level: DifficultyEnum

class TestCreate(BaseModel):
    test_name: str
    duration_minutes: int
    status: TestStatusEnum

class TestQuestionCreate(BaseModel):
    question_id: uuid.UUID
    question_type: QuestionTypeEnum
    order_index: int

class TestAssignmentCreate(BaseModel):
    test_id: uuid.UUID
    candidate_id: uuid.UUID
    scheduled_start_time: datetime = None
    scheduled_end_time: datetime = None

class TestAnswerCreate(BaseModel):
    assignment_id: uuid.UUID
    question_id: uuid.UUID
    question_type: QuestionTypeEnum
    selected_option: str = None
    code_submission: str = None
    code_output: str = None
    is_correct: bool = None
    score: float = None
    time_spent_seconds: int = None
    code_analysis: str = None
    ai_review_notes: str = None
    language: str = None
    stdin: str = ""
    stdout: str = ""
    code_status: str = "pending"
    code_passed: bool = False

# ---------- Service Functions ----------
# ---- Test Storage Service (Ishaan) ----
def create_test(db_conn, test: TestCreate, created_by: uuid.UUID):
    try:
        cur = db_conn.cursor()
        cur.execute("""
            INSERT INTO tests (test_id, test_name, created_by, duration_minutes, status, created_at)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING test_id;
        """, (uuid.uuid4(), test.test_name, created_by, test.duration_minutes, test.status.value))
        test_id = cur.fetchone()[0]
        db_conn.commit()
        cur.close()
        return {"test_id": test_id, "test_name": test.test_name, "created_by": created_by}
    except Exception as e:
        logger.error(f"Error creating test: {e}")
        raise HTTPException(status_code=500, detail="Error creating test")

def create_test_question(db_conn, test_id: uuid.UUID, test_question: TestQuestionCreate):
    try:
        cur = db_conn.cursor()
        cur.execute("""
            INSERT INTO test_questions (id, test_id, question_id, question_type, order_index)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (uuid.uuid4(), test_id, test_question.question_id, test_question.question_type.value, test_question.order_index))
        question_id = cur.fetchone()[0]
        db_conn.commit()
        cur.close()
        return {"id": question_id, "test_id": test_id}
    except Exception as e:
        logger.error(f"Error creating test question: {e}")
        raise HTTPException(status_code=500, detail="Error creating test question")

# ---- Admin Panel + Mapping Service (Swarang + Harsh P) ----
def assign_test_to_candidate(db_conn, assignment: TestAssignmentCreate):
    try:
        cur = db_conn.cursor()
        cur.execute("""
            INSERT INTO test_assignments (assignment_id, test_id, candidate_id, status, assigned_at, scheduled_start_time, scheduled_end_time)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s)
            RETURNING assignment_id;
        """, (uuid.uuid4(), assignment.test_id, assignment.candidate_id, AssignmentStatusEnum.pending.value, assignment.scheduled_start_time, assignment.scheduled_end_time))
        assignment_id = cur.fetchone()[0]
        db_conn.commit()
        cur.close()
        return {"assignment_id": assignment_id}
    except Exception as e:
        logger.error(f"Error assigning test: {e}")
        raise HTTPException(status_code=500, detail="Error assigning test")

def get_assignments_for_test(db_conn, test_id: uuid.UUID):
    try:
        cur = db_conn.cursor()
        cur.execute("""
            SELECT assignment_id, candidate_id, status, scheduled_start_time, scheduled_end_time
            FROM test_assignments
            WHERE test_id = %s;
        """, (test_id,))
        rows = cur.fetchall()
        cur.close()
        return [{"assignment_id": r[0], "candidate_id": r[1], "status": r[2],
                 "scheduled_start_time": r[3], "scheduled_end_time": r[4]} for r in rows]
    except Exception as e:
        logger.error(f"Error fetching assignments: {e}")
        raise HTTPException(status_code=500, detail="Error fetching assignments")

# ---- Candidate Answer Service (Mukesh) ----
def submit_test_answer(db_conn, answer: TestAnswerCreate):
    try:
        cur = db_conn.cursor()
        cur.execute("""
            INSERT INTO test_answers (
                answer_id, assignment_id, question_id, question_type, selected_option,
                code_submission, code_output, is_correct, score, time_spent_seconds,
                code_analysis, ai_review_notes, language, stdin, stdout, code_status, code_passed
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING answer_id;
        """, (
            uuid.uuid4(), answer.assignment_id, answer.question_id, answer.question_type.value,
            answer.selected_option, answer.code_submission, answer.code_output, answer.is_correct,
            answer.score, answer.time_spent_seconds, answer.code_analysis, answer.ai_review_notes,
            answer.language, answer.stdin, answer.stdout, answer.code_status, answer.code_passed
        ))
        answer_id = cur.fetchone()[0]
        db_conn.commit()
        cur.close()
        return {"answer_id": answer_id}
    except Exception as e:
        logger.error(f"Error submitting test answer: {e}")
        raise HTTPException(status_code=500, detail="Error submitting test answer")

# ---- MCQ Filter Service ----
def fetch_mcqs(language: str, difficulty: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT mcq_id, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM mcq_questions
            WHERE language = %s AND difficulty_level = %s
            ORDER BY mcq_id;
        """, (language, difficulty))
        rows = cur.fetchall()
        mcqs = [{"mcq_id": r[0], "question_text": r[1], "option_a": r[2], "option_b": r[3], "option_c": r[4], "option_d": r[5], "correct_answer": r[6]} for r in rows]
        cur.close()
        conn.close()
        return mcqs
    except Exception as e:
        logger.error(f"Error fetching MCQs: {e}")
        raise HTTPException(status_code=500, detail="Error fetching MCQs")

# ---------- FastAPI Endpoints ----------

@app.post("/tests/")
def create_test_endpoint(test: TestCreate):
    conn = get_db_connection()
    user_id = uuid.uuid4()  # Placeholder, replace with auth
    return create_test(conn, test, created_by=user_id)

@app.post("/tests/{test_id}/questions/")
def create_test_question_endpoint(test_id: uuid.UUID, question: TestQuestionCreate):
    conn = get_db_connection()
    return create_test_question(conn, test_id, question)

@app.post("/assignments/")
def assign_test_endpoint(assignment: TestAssignmentCreate):
    conn = get_db_connection()
    return assign_test_to_candidate(conn, assignment)

@app.get("/assignments/{test_id}")
def get_assignments_endpoint(test_id: uuid.UUID):
    conn = get_db_connection()
    return get_assignments_for_test(conn, test_id)

@app.post("/answers/")
def submit_answer_endpoint(answer: TestAnswerCreate):
    conn = get_db_connection()
    return submit_test_answer(conn, answer)

@app.post("/api/filter_mcqs")
def filter_mcqs_endpoint(filters: FilterRequest):
    mcqs = fetch_mcqs(filters.language.value, filters.difficulty_level.value)
    if not mcqs:
        raise HTTPException(status_code=404, detail="No MCQs found with these filters.")
    return {"mcqs": mcqs}
