"""
Submission Storage Microservice
Handles: Storing and retrieving code submissions (MongoDB + PostgreSQL)
Port: 8003

Database Structure:
- MongoDB: code_submissions, code_drafts (backup/session recovery)
- PostgreSQL: test_answer table (primary storage for test submissions)
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional, List
from datetime import datetime
import os
import uuid
import json
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Submission Service", version="1.0.0")

# Custom JSON encoder for MongoDB objects
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

# ======================= DATABASE CONFIGURATION =======================

# MongoDB Configuration
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://root:password@mongodb:27017/codeplay?authSource=admin")

# PostgreSQL Configuration
POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "user": os.getenv("POSTGRES_USER", "codeplay_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "codeplay_password"),
    "database": os.getenv("POSTGRES_DB", "codeplay_db")
}

# ======================= REQUEST MODELS =======================

# Request Models
class SubmissionRequest(BaseModel):
    candidate_id: str  # Changed from user_id
    problem_id: str
    language: str
    code: str
    stdin: Optional[str] = ""
    expected_output: Optional[str] = ""  # For comparison
    sample_output: Optional[str] = ""    # From problem definition

class TestAnswerRequest(BaseModel):
    """Model for storing test answers with output comparison"""
    candidate_id: str
    problem_id: str
    language: str
    code: str
    stdin: str = ""
    stdout: str = ""
    output: str = ""
    status: str = "pending"  # pending, success, error, timeout
    is_passed: bool = False
    expected_output: str = ""

class DraftRequest(BaseModel):
    candidate_id: str  # Changed from user_id
    problem_id: str
    language: str
    code: str
    cursor_position: Optional[int] = 0
    status: str = "draft"

def get_mongodb_client():
    """Get MongoDB connection"""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✓ MongoDB connected")
        return client
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e} - Running in MOCK_MODE")
        return None

def convert_mongo_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict"""
    if not doc:
        return {}
    result = {}
    for key, value in doc.items():
        if key == "_id":
            continue
        elif isinstance(value, ObjectId):
            result[key] = str(value)
        else:
            result[key] = value
    return result

# ======================= POSTGRESQL FUNCTIONS =======================

def get_postgres_connection():
    """Get PostgreSQL connection"""
    try:
        conn = psycopg2.connect(
            host=POSTGRES_CONFIG["host"],
            port=POSTGRES_CONFIG["port"],
            user=POSTGRES_CONFIG["user"],
            password=POSTGRES_CONFIG["password"],
            database=POSTGRES_CONFIG["database"],
            connect_timeout=5
        )
        print("✓ PostgreSQL connected")
        return conn
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        return None

def save_test_answer_to_postgres(test_answer: TestAnswerRequest) -> dict:
    """
    Save test answer to PostgreSQL test_answer table
    
    Returns:
        {
            "id": submission_id,
            "candidate_id": str,
            "problem_id": str,
            "is_passed": bool,
            "status": str
        }
    """
    conn = get_postgres_connection()
    if not conn:
        return {
            "status": "error",
            "message": "PostgreSQL connection failed"
        }
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Insert into test_answer table
        insert_query = """
            INSERT INTO test_answer 
            (candidate_id, problem_id, language, code, stdin, stdout, output, status, is_passed)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, candidate_id, problem_id, language, status, is_passed, timestamp
        """
        
        cursor.execute(insert_query, (
            test_answer.candidate_id,
            test_answer.problem_id,
            test_answer.language,
            test_answer.code,
            test_answer.stdin,
            test_answer.stdout,
            test_answer.output,
            test_answer.status,
            test_answer.is_passed
        ))
        
        result = cursor.fetchone()
        conn.commit()
        
        print(f"✓ Test answer saved to PostgreSQL: ID {result['id']}")
        
        return {
            "id": result["id"],
            "candidate_id": result["candidate_id"],
            "problem_id": result["problem_id"],
            "language": result["language"],
            "status": result["status"],
            "is_passed": result["is_passed"],
            "timestamp": result["timestamp"].isoformat() if result["timestamp"] else None
        }
        
    except Exception as e:
        print(f"Error saving to PostgreSQL: {e}")
        conn.rollback()
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        cursor.close()
        conn.close()

def get_test_answers_postgres(candidate_id: str) -> List[dict]:
    """Fetch all test answers for a candidate from PostgreSQL"""
    conn = get_postgres_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        select_query = """
            SELECT * FROM test_answer 
            WHERE candidate_id = %s 
            ORDER BY timestamp DESC
        """
        
        cursor.execute(select_query, (candidate_id,))
        results = cursor.fetchall()
        
        # Convert to list of dicts
        answers = []
        for row in results:
            answers.append({
                "id": row["id"],
                "candidate_id": row["candidate_id"],
                "problem_id": row["problem_id"],
                "language": row["language"],
                "code": row["code"],
                "stdin": row["stdin"],
                "stdout": row["stdout"],
                "output": row["output"],
                "status": row["status"],
                "is_passed": row["is_passed"],
                "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None
            })
        
        return answers
        
    except Exception as e:
        print(f"Error fetching from PostgreSQL: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_test_answer_postgres(answer_id: int) -> Optional[dict]:
    """Fetch specific test answer from PostgreSQL"""
    conn = get_postgres_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        select_query = "SELECT * FROM test_answer WHERE id = %s"
        cursor.execute(select_query, (answer_id,))
        result = cursor.fetchone()
        
        if not result:
            return None
        
        return {
            "id": result["id"],
            "candidate_id": result["candidate_id"],
            "problem_id": result["problem_id"],
            "language": result["language"],
            "code": result["code"],
            "stdin": result["stdin"],
            "stdout": result["stdout"],
            "output": result["output"],
            "status": result["status"],
            "is_passed": result["is_passed"],
            "timestamp": result["timestamp"].isoformat() if result["timestamp"] else None
        }
        
    except Exception as e:
        print(f"Error fetching from PostgreSQL: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# ========================= API ENDPOINTS =========================

@app.get("/health")
async def health():
    """Health check endpoint - check both databases"""
    mongo_client = get_mongodb_client()
    postgres_conn = get_postgres_connection()
    
    mongodb_status = "connected" if mongo_client else "disconnected"
    postgres_status = "connected" if postgres_conn else "disconnected"
    
    if mongo_client:
        mongo_client.close()
    if postgres_conn:
        postgres_conn.close()
    
    return {
        "status": "healthy",
        "service": "Submission Service",
        "port": 8003,
        "mongodb": mongodb_status,
        "postgresql": postgres_status
    }

@app.post("/submission")
async def submit_code(req: SubmissionRequest):
    """
    Save code submission to both MongoDB and PostgreSQL
    
    Expected: code without input declaration
    Will use stdin from request or sample_input
    """
    
    submission = {
        "candidate_id": req.candidate_id,
        "problem_id": req.problem_id,
        "language": req.language,
        "code": req.code,
        "stdin": req.stdin or "",
        "status": "submitted",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Save to MongoDB
    client = get_mongodb_client()
    if client:
        try:
            db = client.codeplay
            result = db.code_submissions.insert_one(submission)
            client.close()
            print(f"✓ Submission saved to MongoDB: {result.inserted_id}")
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
            if client:
                client.close()
    
    return {
        "submission_id": submission.get("submission_id"),
        "candidate_id": req.candidate_id,
        "problem_id": req.problem_id,
        "language": req.language,
        "status": "submitted",
        "timestamp": submission["timestamp"]
    }

@app.post("/test-answer")
async def save_test_answer(req: TestAnswerRequest):
    """
    Save test answer with output comparison to PostgreSQL
    
    Used after code execution to store results
    
    Response includes:
    - id: submission ID
    - is_passed: whether output matches expected
    - status: success, error, timeout
    """
    
    result = save_test_answer_to_postgres(req)
    return result

@app.get("/submissions/{candidate_id}")
async def get_submissions(candidate_id: str):
    """Fetch all submissions for a candidate"""
    
    submissions = await get_user_submissions(candidate_id)
    
    return {
        "candidate_id": candidate_id,
        "count": len(submissions),
        "submissions": submissions
    }

@app.get("/test-answers/{candidate_id}")
async def get_test_answers(candidate_id: str):
    """Fetch all test answers for a candidate from PostgreSQL"""
    
    answers = get_test_answers_postgres(candidate_id)
    
    return {
        "candidate_id": candidate_id,
        "count": len(answers),
        "test_answers": answers
    }

@app.get("/test-answer/{answer_id}")
async def get_test_answer(answer_id: int):
    """Fetch specific test answer from PostgreSQL"""
    
    answer = get_test_answer_postgres(answer_id)
    
    if not answer:
        raise HTTPException(status_code=404, detail="Test answer not found")
    
    return answer

@app.get("/submission/{submission_id}")
async def get_submission(submission_id: str):
    """Fetch specific submission from MongoDB"""
    
    client = get_mongodb_client()
    if client:
        try:
            db = client.codeplay
            submission = db.code_submissions.find_one({"submission_id": submission_id})
            client.close()
            
            if submission:
                return convert_mongo_doc(submission)
        except Exception as e:
            print(f"Error fetching from MongoDB: {e}")
            client.close() if client else None
    
    raise HTTPException(status_code=404, detail="Submission not found")

# ======================= DRAFT FUNCTIONS =======================

async def get_user_submissions(candidate_id: str) -> List[dict]:
    """Fetch user submissions from MongoDB"""
    
    client = get_mongodb_client()
    if client:
        try:
            db = client.codeplay
            submissions = list(db.code_submissions.find({"candidate_id": candidate_id}))
            client.close()
            
            return [convert_mongo_doc(sub) for sub in submissions]
        except Exception as e:
            print(f"Error fetching from MongoDB: {e}")
    
    return []

@app.post("/draft")
async def save_draft(req: DraftRequest):
    """Auto-save draft for session recovery"""
    
    draft = {
        "candidate_id": req.candidate_id,
        "problem_id": req.problem_id,
        "language": req.language,
        "code": req.code,
        "cursor_position": req.cursor_position,
        "status": "draft",
        "timestamp": datetime.utcnow().isoformat(),
        "last_saved": datetime.utcnow().isoformat()
    }
    
    client = get_mongodb_client()
    if client:
        try:
            db = client.codeplay
            draft_id = f"{req.candidate_id}_{req.problem_id}_draft"
            result = db.code_drafts.update_one(
                {"draft_id": draft_id},
                {"$set": draft},
                upsert=True
            )
            client.close()
            print(f"✓ Draft saved: {draft_id}")
            return {"status": "saved", "draft_id": draft_id}
        except Exception as e:
            print(f"Error saving draft to MongoDB: {e}")
            client.close() if client else None
    
    return {"status": "error", "message": "Failed to save draft"}

@app.get("/draft/{candidate_id}/{problem_id}")
async def get_draft(candidate_id: str, problem_id: str):
    """Retrieve draft for session recovery"""
    
    draft_id = f"{candidate_id}_{problem_id}_draft"
    
    client = get_mongodb_client()
    if client:
        try:
            db = client.codeplay
            draft = db.code_drafts.find_one({"draft_id": draft_id})
            client.close()
            
            if draft:
                return convert_mongo_doc(draft)
        except Exception as e:
            print(f"Error fetching draft: {e}")
            client.close() if client else None
    
    return {"status": "no_draft", "message": "No saved draft for this problem"}

@app.delete("/draft/{candidate_id}/{problem_id}")
async def delete_draft(candidate_id: str, problem_id: str):
    """Delete draft after submission"""
    
    draft_id = f"{candidate_id}_{problem_id}_draft"
    
    client = get_mongodb_client()
    if client:
        try:
            db = client.codeplay
            result = db.code_drafts.delete_one({"draft_id": draft_id})
            client.close()
            print(f"✓ Draft deleted: {draft_id}")
            return {"status": "deleted"}
        except Exception as e:
            print(f"Error deleting draft: {e}")
            client.close() if client else None
    
    return {"status": "error", "message": "Failed to delete draft"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
