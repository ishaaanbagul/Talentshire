"""
Problem Fetching Microservice
Handles: Fetching coding problems from MongoDB
Port: 8002
Returns: id, title, description, difficulty, labels, sample_input, sample_output, constraints
"""
'''
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from typing import Optional
import os
from datetime import datetime

app = FastAPI(title="Problem Service", version="1.0.0")

# MongoDB Configuration with Authentication
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://root:password@mongodb:27017/codeplay?authSource=admin")

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

# Mock data for testing without MongoDB
MOCK_PROBLEMS = {
    "1": {
        "id": "1",
        "title": "Sum Two Numbers",
        "description": "Write a program that takes two numbers and returns their sum.",
        "difficulty": "Easy",
        "labels": ["arithmetic", "basic", "beginner"],
        "sample_input": "3\n5",
        "sample_output": "8",
        "constraints": "1 <= a, b <= 1000"
    },
    "2": {
        "id": "2",
        "title": "Prime Number Checker",
        "description": "Check if a given number is prime.",
        "difficulty": "Medium",
        "labels": ["math", "number-theory"],
        "sample_input": "7",
        "sample_output": "Yes",
        "constraints": "1 <= n <= 10000"
    },
    "3": {
        "id": "3",
        "title": "Array Sum",
        "description": "Find the sum of all elements in an array.",
        "difficulty": "Easy",
        "labels": ["arrays", "loops"],
        "sample_input": "3\n1\n2\n3",
        "sample_output": "6",
        "constraints": "1 <= n <= 100"
    },
    "4": {
        "id": "4",
        "title": "SQL - Employee Salary Analysis",
        "description": "Write a SQL query to find employees earning more than their department average salary. Return employee_name, salary, department, and department_avg_salary. Order by department and salary DESC.",
        "difficulty": "Hard",
        "labels": ["sql", "database", "subquery", "window-function"],
        "sample_input": "SELECT e.employee_name, e.salary, e.department, ROUND(AVG(e2.salary) OVER (PARTITION BY e2.department), 2) as dept_avg FROM employees e JOIN employees e2 ON e.department = e2.department WHERE e.salary > (SELECT AVG(salary) FROM employees e3 WHERE e3.department = e.department) ORDER BY e.department, e.salary DESC",
        "sample_output": "john\t65000\tsales\t55000\nalice\t72000\thr\t60000\nbob\t58000\tit\t52000",
        "constraints": "Use subquery or window functions. Table: employees(employee_name VARCHAR, salary INT, department VARCHAR)"
    },
    "5": {
        "id": "5",
        "title": "PySpark - Word Count",
        "description": "Write a PySpark program to count occurrences of each word in text data. Return results sorted by count DESC.",
        "difficulty": "Medium",
        "labels": ["pyspark", "rdd", "data-processing"],
        "sample_input": "spark = SparkSession.builder.appName('WordCount').getOrCreate()\ndata = ['hello world', 'hello spark', 'world of spark']\nrdd = spark.sparkContext.parallelize(data)",
        "sample_output": "hello\t2\nworld\t2\nspark\t2\nof\t1",
        "constraints": "Use flatMap, map, reduceByKey operations. Return word count pairs."
    }
}

async def get_problem_from_db(problem_id: str) -> Optional[dict]:
    """Fetch problem from MongoDB or return mock data"""
    
    # Try MongoDB first
    client = get_mongodb_client()
    if client:
        try:
            db = client.codeplay
            problem = db.coding_problems.find_one({"id": problem_id})
            client.close()
            
            if problem:
                # Return only required fields
                return {
                    "id": problem.get("id", problem_id),
                    "title": problem.get("title", ""),
                    "description": problem.get("description", ""),
                    "difficulty": problem.get("difficulty", ""),
                    "labels": problem.get("labels", []),
                    "sample_input": problem.get("sample_input", ""),
                    "sample_output": problem.get("sample_output", ""),
                    "constraints": problem.get("constraints", "")
                }
        except Exception as e:
            print(f"Error fetching from MongoDB: {e}")
    
    # Return mock data if MongoDB not available or problem not found
    if problem_id in MOCK_PROBLEMS:
        return MOCK_PROBLEMS[problem_id]
    
    # If ID not found, return a default mock problem
    return {
        "id": problem_id,
        "title": f"Problem {problem_id}",
        "description": "Problem not found in database - using mock data for testing",
        "difficulty": "Unknown",
        "labels": [],
        "sample_input": "",
        "sample_output": "",
        "constraints": ""
    }

# ========================= API ENDPOINTS =========================

@app.get("/health")
async def health():
    """Health check endpoint"""
    client = get_mongodb_client()
    mongodb_status = "connected" if client else "disconnected (mock mode)"
    if client:
        client.close()
    
    return {
        "status": "healthy",
        "service": "Problem Service",
        "port": 8002,
        "mongodb": mongodb_status
    }

@app.get("/problem/{problem_id}")
async def get_problem(problem_id: str):
    """Fetch problem by ID"""
    problem = await get_problem_from_db(problem_id)
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    return problem

@app.get("/problems")
async def list_problems(skip: int = 0, limit: int = 10):
    """List all problems (with pagination)"""
    
    client = get_mongodb_client()
    if client:
        try:
            db = client.codeplay
            problems = list(db.coding_problems.find().skip(skip).limit(limit))
            client.close()
            
            # Return only required fields
            return [
                {
                    "id": p.get("id"),
                    "title": p.get("title", ""),
                    "difficulty": p.get("difficulty", ""),
                    "labels": p.get("labels", [])
                }
                for p in problems
            ]
        except Exception as e:
            print(f"Error fetching from MongoDB: {e}")
    
    # Return mock problems list
    return [
        {
            "id": p["id"],
            "title": p["title"],
            "difficulty": p["difficulty"],
            "labels": p["labels"]
        }
        for p in MOCK_PROBLEMS.values()
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
'''

"""
Problem Fetching Microservice (Postgres + Mongo)
Handles:
  - Public problem fetch from MongoDB
  - Candidate-authorized fetching of coding problems assigned via PostgreSQL chain:
    test_assignments -> tests -> test_questions -> unified_questions -> source_id (Mongo)

Port: 8002

Returns (problem payload):
  id, title, description, difficulty, labels, sample_input, sample_output, constraints
Plus:
  candidate_id (for candidate endpoints)
"""

from fastapi import FastAPI, HTTPException, Header, Query
from pymongo import MongoClient
from typing import Optional, List, Dict, Any
import os
from datetime import datetime
from dotenv import load_dotenv

# NEW: Postgres
import psycopg2
import psycopg2.extras

app = FastAPI(title="Problem Service", version="2.0.0")

# -------------------- Environment --------------------
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://root:password@mongodb:27017/codeplay?authSource=admin")
MONGO_DB = os.getenv("MONGODB_DB", "codeplay")
# Choose the collection that stores coding questions (per your ERD): coding_questions or coding_problems
MONGO_COLLECTION = os.getenv("MONGODB_COLLECTION", "coding_questions")

# PostgreSQL Configuration (for assignment enforcement & question mapping)
POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://postgres:password@postgres:5432/codeplay")

# Which unified_questions.source_type values should be treated as Mongo coding sources
CODING_SOURCE_TYPES = set(os.getenv("CODING_SOURCE_TYPES", "coding_questions,coding_problems").split(","))

# -------------------- DB Clients --------------------
def get_mongodb_client() -> Optional[MongoClient]:
    """Get MongoDB connection"""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✓ MongoDB connected")
        return client
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e} - Running in MOCK_MODE")
        return None

def get_pg_conn():
    """Get PostgreSQL connection"""
    try:
        conn = psycopg2.connect(POSTGRES_URI)
        return conn
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e} - Running in MOCK_MODE")
        return None

# -------------------- Mock data (when DBs unavailable) --------------------
MOCK_PROBLEMS = {
    "1": {
        "id": "1",
        "title": "Sum Two Numbers",
        "description": "Write a program that takes two numbers and returns their sum.",
        "difficulty": "Easy",
        "labels": ["arithmetic", "basic", "beginner"],
        "sample_input": "3\n5",
        "sample_output": "8",
        "constraints": "1 <= a, b <= 1000",
    },
    "2": {
        "id": "2",
        "title": "Prime Number Checker",
        "description": "Check if a given number is prime.",
        "difficulty": "Medium",
        "labels": ["math", "number-theory"],
        "sample_input": "7",
        "sample_output": "Yes",
        "constraints": "1 <= n <= 10000",
    },
    "3": {
        "id": "3",
        "title": "Array Sum",
        "description": "Find the sum of all elements in an array.",
        "difficulty": "Easy",
        "labels": ["arrays", "loops"],
        "sample_input": "3\n1\n2\n3",
        "sample_output": "6",
        "constraints": "1 <= n <= 100",
    },
    "4": {
        "id": "4",
        "title": "SQL - Employee Salary Analysis",
        "description": "Write a SQL query to find employees earning more than their department average salary. Return employee_name, salary, department, and department_avg_salary. Order by department and salary DESC.",
        "difficulty": "Hard",
        "labels": ["sql", "database", "subquery", "window-function"],
        "sample_input": "SELECT e.employee_name, e.salary, e.department, ROUND(AVG(e2.salary) OVER (PARTITION BY e2.department), 2) as dept_avg FROM employees e JOIN employees e2 ON e.department = e2.department WHERE e.salary > (SELECT AVG(salary) FROM employees e3 WHERE e3.department = e.department) ORDER BY e.department, e.salary DESC",
        "sample_output": "john\t65000\tsales\t55000\nalice\t72000\thr\t60000\nbob\t58000\tit\t52000",
        "constraints": "Use subquery or window functions. Table: employees(employee_name VARCHAR, salary INT, department VARCHAR)"
    },
    "5": {
        "id": "5",
        "title": "PySpark - Word Count",
        "description": "Write a PySpark program to count occurrences of each word in text data. Return results sorted by count DESC.",
        "difficulty": "Medium",
        "labels": ["pyspark", "rdd", "data-processing"],
        "sample_input": "spark = SparkSession.builder.appName('WordCount').getOrCreate()\ndata = ['hello world', 'hello spark', 'world of spark']\nrdd = spark.sparkContext.parallelize(data)",
        "sample_output": "hello\t2\nworld\t2\nspark\t2\nof\t1",
        "constraints": "Use flatMap, map, reduceByKey operations. Return word count pairs."
    }
}

# -------------------- Token → candidate_id --------------------
def get_candidate_id_from_token(authorization: Optional[str]) -> str:
    """
    Extract candidate_id from 'Authorization: Bearer <token>'.
    Replace with real JWT verification in production (e.g., pyjwt).
    For now, accept tokens like:
      'candidate_student_001'  -> candidate_id = 'student_001'
      'student_001'            -> candidate_id = 'student_001'
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1].strip()
    if token.startswith("candidate_"):
        return token.replace("candidate_", "", 1)
    return token

# -------------------- PG Queries (assignment chain per ERD) --------------------
def ensure_candidate_has_assignment(conn, candidate_id: str, test_id: str) -> Dict[str, Any]:
    """
    Verify that candidate has an assignment for this test_id.
    Returns the assignment row if found, else raises HTTPException.
    """
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT assignment_id, test_id, candidate_id, status
                FROM test_assignments
                WHERE candidate_id = %s AND test_id = %s
                """,
                (candidate_id, test_id),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="No assignment found for candidate/test")

            status = row.get("status")
            if status and status.lower() not in ("assigned", "active", "started"):
                raise HTTPException(status_code=403, detail=f"Assignment not active (status={status})")
            return row
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Postgres error during assignment check: {e}")

def get_coding_source_ids_for_test(conn, test_id: str) -> List[Dict[str, Any]]:
    """
    Resolve coding questions for a given test_id:
      tests -> test_questions (test_id, question_id, question_type)
      -> unified_questions (id=question_id) -> source_id, source_type
    Returns: [{question_id, source_id, source_type}, ...] filtered to coding sources only.
    """
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Get all questions for this test, then keep coding ones
            cur.execute(
                """
                SELECT tq.question_id, tq.question_type
                FROM test_questions AS tq
                WHERE tq.test_id = %s
                """,
                (test_id,),
            )
            tq_rows = cur.fetchall() or []
            question_ids = [
                r["question_id"] for r in tq_rows
                if str(r.get("question_type", "")).lower() in ("coding", "code")
            ]
            if not question_ids:
                return []

            # Map to unified_questions to get source_id/source_type
            cur.execute(
                """
                SELECT uq.id AS question_id, uq.source_id, uq.source_type
                FROM unified_questions AS uq
                WHERE uq.id = ANY(%s)
                """,
                (question_ids,),
            )
            uq_rows = cur.fetchall() or []

            # Filter to Mongo coding sources per env
            out = [r for r in uq_rows if str(r.get("source_type", "")).lower() in CODING_SOURCE_TYPES]
            return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Postgres error during source resolution: {e}")

# -------------------- Mongo fetch helpers --------------------
def get_problem_from_mongo(source_id: str) -> Optional[dict]:
    """Fetch problem by Mongo 'id' (string) from configured collection."""
    client = get_mongodb_client()
    if not client:
        # Mock fallback
        return MOCK_PROBLEMS.get(source_id)
    try:
        db = client[MONGO_DB]
        coll = db[MONGO_COLLECTION]
        doc = coll.find_one({"id": source_id}) or coll.find_one({"_id": source_id})
        client.close()

        if not doc:
            return None

        return {
            "id": doc.get("id", source_id),
            "title": doc.get("title", ""),
            "description": doc.get("description", ""),
            "difficulty": doc.get("difficulty", ""),
            "labels": doc.get("labels", []),
            "sample_input": doc.get("sample_input", ""),
            "sample_output": doc.get("sample_output", ""),
            "constraints": doc.get("constraints", ""),
        }
    except Exception as e:
        client.close()
        raise HTTPException(status_code=500, detail=f"Mongo fetch error: {e}")

# -------------------- Existing public endpoints (unchanged) --------------------
@app.get("/health")
async def health():
    """Health check endpoint"""
    mg = get_mongodb_client()
    pg = get_pg_conn()
    mongodb_status = "connected" if mg else "disconnected (mock mode)"
    pg_status = "connected" if pg else "disconnected (mock mode)"
    if mg:
        mg.close()
    if pg:
        pg.close()

    return {
        "status": "healthy",
        "service": "Problem Service",
        "port": 8002,
        "mongodb": mongodb_status,
        "postgres": pg_status,
    }

@app.get("/problem/{problem_id}")
async def get_problem(problem_id: str):
    """Public fetch by problem_id (Mongo only, no assignment enforcement)"""
    problem = get_problem_from_mongo(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem

@app.get("/problems")
async def list_problems(skip: int = 0, limit: int = 10):
    """List all problems (with pagination) — Mongo only, no assignment enforcement"""
    client = get_mongodb_client()
    if client:
        try:
            db = client[MONGO_DB]
            coll = db[MONGO_COLLECTION]
            problems = list(coll.find().skip(skip).limit(limit))
            client.close()

            return [
                {
                    "id": p.get("id"),
                    "title": p.get("title", ""),
                    "difficulty": p.get("difficulty", ""),
                    "labels": p.get("labels", []),
                }
                for p in problems
            ]
        except Exception as e:
            print(f"Error fetching from MongoDB: {e}")

    # Return mock problems list
    return [
        {
            "id": p["id"],
            "title": p["title"],
            "difficulty": p["difficulty"],
            "labels": p["labels"],
        }
        for p in MOCK_PROBLEMS.values()
    ]

# -------------------- Candidate-aware endpoints (assignment enforced) --------------------
@app.get("/candidate/problems")
async def list_candidate_problems(
    test_id: str = Query(..., description="The test_id to list problems for"),
    authorization: Optional[str] = Header(None),
):
    """
    Returns coding problems assigned to the candidate for a given test_id.
    Enforces assignment via Postgres and fetches problem payloads from Mongo.
    """
    candidate_id = get_candidate_id_from_token(authorization)
    conn = get_pg_conn()
    if not conn:
        # Mock fallback: return mock problems with candidate_id
        return [{**p, "candidate_id": candidate_id} for p in MOCK_PROBLEMS.values()]

    try:
        # 1) Verify assignment exists for candidate + test
        _assign = ensure_candidate_has_assignment(conn, candidate_id, test_id)
        # 2) Resolve coding sources via test_questions -> unified_questions
        sources = get_coding_source_ids_for_test(conn, test_id)
        if not sources:
            return []

        # 3) Fetch each source_id from Mongo
        results = []
        for s in sources:
            src_id = str(s["source_id"])
            problem = get_problem_from_mongo(src_id)
            if problem:
                problem["candidate_id"] = candidate_id
                results.append(problem)
        return results
    finally:
        conn.close()

@app.get("/candidate/problem/{problem_id}")
async def get_candidate_problem(
    problem_id: str,
    test_id: str = Query(..., description="The test_id the candidate is attempting"),
    authorization: Optional[str] = Header(None),
):
    """
    Fetch a specific coding problem for a candidate, enforcing that
    the problem_id (Mongo source_id) is part of the assigned test's coding questions.
    """
    candidate_id = get_candidate_id_from_token(authorization)
    conn = get_pg_conn()
    if not conn:
        # Mock fallback; no strict assignment
        problem = MOCK_PROBLEMS.get(problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found (mock)")
        problem["candidate_id"] = candidate_id
        return problem

    try:
        # 1) Verify assignment exists
        _assign = ensure_candidate_has_assignment(conn, candidate_id, test_id)
        # 2) Resolve sources for this test
        sources = get_coding_source_ids_for_test(conn, test_id)
        allowed_ids = {str(s["source_id"]) for s in sources}

        if problem_id not in allowed_ids:
            raise HTTPException(status_code=403, detail="Problem not assigned to this candidate for the given test")

        # 3) Fetch from Mongo by source_id == problem_id
        problem = get_problem_from_mongo(problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        problem["candidate_id"] = candidate_id
        return problem
    finally:
        conn.close()

# -------------------- Local dev runner --------------------
if __name__ == "__main__":
    import uvicorn
