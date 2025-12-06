from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import sys
import tempfile
import json
import re
import shutil
from datetime import datetime
from typing import Optional, List
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

app = FastAPI(title="Code Runner with MongoDB")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print(f"Python executable: {sys.executable}", flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"Code execution: Direct subprocess mode with MongoDB integration", flush=True)

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "coding_platform")

# Global MongoDB client (will be initialized on first use)
mongodb_client = None
MOCK_MODE = False  # Flag to track if we're using mock data


def get_mongodb_client():
    """Get MongoDB client with error handling and fallback to mock mode."""
    global mongodb_client, MOCK_MODE
    
    if mongodb_client is not None:
        return mongodb_client
    
    try:
        mongodb_client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        # Test connection
        mongodb_client.admin.command('ping')
        print(f"[MongoDB] Connected to {MONGODB_URL}", flush=True)
        MOCK_MODE = False
        return mongodb_client
    except (ServerSelectionTimeoutError, Exception) as e:
        print(f"[MongoDB] Connection failed: {str(e)}", flush=True)
        print(f"[MongoDB] Falling back to MOCK MODE with hardcoded data", flush=True)
        MOCK_MODE = True
        return None


def get_problem_from_db(problem_id: str):
    """Fetch problem from MongoDB or return mock data."""
    try:
        client = get_mongodb_client()
        
        if MOCK_MODE or client is None:
            # Return mock problem data with SQL support
            return {
                "id": problem_id,
                "title": "Sum Two Numbers (Mock Data)",
                "body": "Given two integers a and b, print their sum.\nWrite a program that reads two integers and outputs their sum.",
                "sample_input": "3 5",
                "sample_output": "8",
                "constraints": "-10^9 <= a,b <= 10^9",
                "difficulty": "Easy",
                "languages": ["python", "java", "sql"],
                "time_limit": 10,
                "test_cases": [
                    {"input": "3 5", "output": "8"},
                    {"input": "-1 1", "output": "0"},
                    {"input": "1000000000 1000000000", "output": "2000000000"}
                ],
                "sql_schema": "CREATE TABLE numbers (a INT, b INT);",
                "sql_test_data": "INSERT INTO numbers VALUES (3, 5), (-1, 1), (1000000000, 1000000000);",
                "sql_expected_output": "8\n0\n2000000000"
            }
        
        # Try to fetch from MongoDB
        db = client[DB_NAME]
        problem = db.coding_problems.find_one({"id": str(problem_id)})
        
        if problem:
            # Remove MongoDB's _id field from response
            problem.pop('_id', None)
            return problem
        else:
            # Return mock data if problem not found
            return {
                "id": problem_id,
                "title": "Sum Two Numbers (Mock Data)",
                "body": "Given two integers a and b, print their sum.",
                "sample_input": "3 5",
                "sample_output": "8",
                "constraints": "-10^9 <= a,b <= 10^9",
                "difficulty": "Easy",
                "languages": ["python", "java", "sql"],
                "time_limit": 10,
                "test_cases": [
                    {"input": "3 5", "output": "8"},
                    {"input": "-1 1", "output": "0"}
                ],
                "sql_schema": "CREATE TABLE numbers (a INT, b INT);",
                "sql_test_data": "INSERT INTO numbers VALUES (3, 5), (-1, 1);",
                "sql_expected_output": "8\n0"
            }
    except Exception as e:
        print(f"[Error] get_problem_from_db: {str(e)}", flush=True)
        # Return mock data on any error
        return {
            "id": problem_id,
            "title": "Error - Using Mock Data",
            "body": "Database error occurred. Using mock problem.",
            "sample_input": "3 5",
            "sample_output": "8",
            "constraints": "-10^9 <= a,b <= 10^9",
            "difficulty": "Easy",
            "languages": ["python", "java", "sql"],
            "time_limit": 10,
            "test_cases": []
        }


def save_submission_to_db(submission: dict):
    """Save submission to MongoDB or log to console in mock mode."""
    try:
        client = get_mongodb_client()
        
        if MOCK_MODE or client is None:
            # Log to console in mock mode
            print(f"[Mock Submission] {json.dumps(submission, indent=2)}", flush=True)
            return {"success": True, "mode": "mock", "message": "Submission logged to mock mode"}
        
        # Save to MongoDB
        db = client[DB_NAME]
        result = db.submissions.insert_one(submission)
        print(f"[MongoDB] Submission saved with ID: {result.inserted_id}", flush=True)
        return {"success": True, "submission_id": str(result.inserted_id)}
    except Exception as e:
        print(f"[Error] save_submission_to_db: {str(e)}", flush=True)
        return {"success": False, "error": str(e)}


def save_code_execution_to_db(execution_result: dict):
    """Save code execution result to MongoDB for code analysis."""
    try:
        client = get_mongodb_client()
        
        if MOCK_MODE or client is None:
            # Log to console in mock mode
            print(f"[Mock Code Execution] {json.dumps(execution_result, indent=2)}", flush=True)
            return {"success": True, "mode": "mock", "code_id": execution_result.get("code_id")}
        
        # Save to MongoDB
        db = client[DB_NAME]
        result = db.code_executions.insert_one(execution_result)
        print(f"[MongoDB] Code execution saved with ID: {result.inserted_id}", flush=True)
        return {"success": True, "code_id": str(result.inserted_id)}
    except Exception as e:
        print(f"[Error] save_code_execution_to_db: {str(e)}", flush=True)
        return {"success": False, "error": str(e)}



class Question(BaseModel):
    id: str
    title: str
    body: str
    sample_input: str
    sample_output: str
    constraints: str
    difficulty: str


class RunRequest(BaseModel):
    language: str
    version: Optional[str] = None
    files: Optional[list] = None
    stdin: Optional[str] = ""
    problem_id: Optional[str] = None


class SubmissionRequest(BaseModel):
    problem_id: str
    user_id: str
    language: str
    code: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    client = get_mongodb_client()
    return {
        "status": "healthy",
        "mongodb_mode": "mock" if MOCK_MODE else "connected",
        "code_execution": "direct_subprocess"
    }


@app.get("/problem/{problem_id}")
async def get_problem(problem_id: str):
    """Fetch problem from MongoDB by ID, or return mock data if unavailable."""
    problem = get_problem_from_db(problem_id)
    return problem


@app.get("/question")
async def get_question():
    """Legacy endpoint - returns problem with ID 1."""
    return get_problem_from_db("1")


@app.post("/run")
async def run_code(req: RunRequest):
    """
    Execute code directly via subprocess.
    Supports: Python, Java, SQL.
    Saves execution result to database for code analysis.
    """
    try:
        # Extract code from files
        code_content = ""
        if req.files:
            for f in req.files:
                if isinstance(f, dict):
                    content = f.get("content", "")
                    if content and content.strip():
                        code_content = content
                        break

        if not code_content or not code_content.strip():
            return {
                "run": {
                    "stdout": "",
                    "stderr": "No code provided or code is empty",
                    "output": "No code provided or code is empty",
                    "code": 1
                }
            }

        lang = (req.language or "").lower().strip()
        stdin_data = (req.stdin or "").encode() if req.stdin else None

        print(f"[Executor] Running {lang} code...", flush=True)

        # Variable to store execution result
        execution_result = None

        # Python execution
        if lang == "python":
            result = subprocess.run(
                [sys.executable, "-c", code_content],
                input=stdin_data,
                capture_output=True,
                timeout=10,
                text=False
            )
            
            # Fetch constraint from problem if problem_id provided
            constraint = ""
            if req.problem_id:
                problem = get_problem_from_db(req.problem_id)
                constraint = problem.get("constraints", "")
            
            execution_result = {
                "language": "python",
                "code": code_content,
                "problem_id": req.problem_id or "",
                "constraint": constraint,
                "stdout": result.stdout.decode('utf-8', errors='replace'),
                "stderr": result.stderr.decode('utf-8', errors='replace'),
                "exit_code": result.returncode,
                "status": "success" if result.returncode == 0 else "error",
                "timestamp": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow()
            }
            
            # Save to database
            save_code_execution_to_db(execution_result)
            
            return {
                "run": {
                    "stdout": result.stdout.decode('utf-8', errors='replace'),
                    "stderr": result.stderr.decode('utf-8', errors='replace'),
                    "output": result.stdout.decode('utf-8', errors='replace') or result.stderr.decode('utf-8', errors='replace'),
                    "code": result.returncode
                }
            }

        # Java execution
        elif lang == "java":
            # Extract class name from code (look for "public class ClassName")
            class_match = re.search(r'public\s+class\s+(\w+)', code_content)
            class_name = class_match.group(1) if class_match else "Main"
            
            # Create temp directory for Java files
            temp_dir = tempfile.mkdtemp()
            java_file = os.path.join(temp_dir, f"{class_name}.java")
            
            # Write Java code to properly named file
            with open(java_file, 'w') as f:
                f.write(code_content)

            try:
                # Compile
                compile_result = subprocess.run(
                    ["javac", java_file],
                    capture_output=True,
                    timeout=10,
                    text=True,
                    cwd=temp_dir
                )
                
                if compile_result.returncode != 0:
                    # Fetch constraint from problem if problem_id provided
                    constraint = ""
                    if req.problem_id:
                        problem = get_problem_from_db(req.problem_id)
                        constraint = problem.get("constraints", "")
                    
                    execution_result = {
                        "language": "java",
                        "code": code_content,
                        "problem_id": req.problem_id or "",
                        "constraint": constraint,
                        "stdout": "",
                        "stderr": compile_result.stderr or "Compilation failed",
                        "exit_code": 1,
                        "status": "error",
                        "timestamp": datetime.utcnow().isoformat(),
                        "created_at": datetime.utcnow()
                    }
                    save_code_execution_to_db(execution_result)
                    
                    return {
                        "run": {
                            "stdout": "",
                            "stderr": compile_result.stderr or "Compilation failed",
                            "output": compile_result.stderr or "Compilation failed",
                            "code": 1
                        }
                    }

                # Run compiled Java class
                run_result = subprocess.run(
                    ["java", "-cp", temp_dir, class_name],
                    input=stdin_data,
                    capture_output=True,
                    timeout=10,
                    text=False,
                    cwd=temp_dir
                )

                stdout_str = run_result.stdout.decode('utf-8', errors='replace')
                stderr_str = run_result.stderr.decode('utf-8', errors='replace')
                
                # Fetch constraint from problem if problem_id provided
                constraint = ""
                if req.problem_id:
                    problem = get_problem_from_db(req.problem_id)
                    constraint = problem.get("constraints", "")
                
                execution_result = {
                    "language": "java",
                    "code": code_content,
                    "problem_id": req.problem_id or "",
                    "constraint": constraint,
                    "stdout": stdout_str,
                    "stderr": stderr_str,
                    "exit_code": run_result.returncode,
                    "status": "success" if run_result.returncode == 0 else "error",
                    "timestamp": datetime.utcnow().isoformat(),
                    "created_at": datetime.utcnow()
                }
                save_code_execution_to_db(execution_result)

                return {
                    "run": {
                        "stdout": stdout_str,
                        "stderr": stderr_str,
                        "output": stdout_str or stderr_str,
                        "code": run_result.returncode
                    }
                }
            finally:
                # Clean up temp directory
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass

        # SQL execution (via sqlite3) - Option 2: Structured with Schema + Test Data
        elif lang == "sql":
            import sqlite3
            try:
                # Fetch problem details if problem_id provided
                problem = None
                sql_schema = ""
                sql_test_data = ""
                sql_expected_output = ""
                constraint = ""
                
                if req.problem_id:
                    problem = get_problem_from_db(req.problem_id)
                    sql_schema = problem.get("sql_schema", "")
                    sql_test_data = problem.get("sql_test_data", "")
                    sql_expected_output = problem.get("sql_expected_output", "")
                    constraint = problem.get("constraints", "")
                
                conn = sqlite3.connect(':memory:')
                cursor = conn.cursor()
                all_output = []
                errors = []
                
                # Step 1: Execute schema (if provided)
                if sql_schema:
                    try:
                        for stmt in sql_schema.split(';'):
                            stmt = stmt.strip()
                            if stmt:
                                cursor.execute(stmt)
                    except sqlite3.Error as e:
                        errors.append(f"Schema error: {str(e)}")
                
                # Step 2: Execute test data (if provided)
                if sql_test_data:
                    try:
                        for stmt in sql_test_data.split(';'):
                            stmt = stmt.strip()
                            if stmt:
                                cursor.execute(stmt)
                    except sqlite3.Error as e:
                        errors.append(f"Test data error: {str(e)}")
                
                # Step 3: Validate user code is SELECT only
                user_code_upper = code_content.upper().strip()
                is_valid_select = user_code_upper.startswith('SELECT')
                
                if not is_valid_select and sql_schema:
                    # If schema is provided, enforce SELECT-only
                    errors.append("Error: Only SELECT queries allowed. Cannot use CREATE, INSERT, DROP, etc.")
                
                # Step 4: Execute user code
                if not errors:
                    try:
                        # Split by semicolon and execute
                        for statement in code_content.split(';'):
                            statement = statement.strip()
                            if not statement:
                                continue
                            
                            try:
                                cursor.execute(statement)
                                
                                # Fetch results from SELECT
                                if statement.upper().startswith('SELECT'):
                                    rows = cursor.fetchall()
                                    if rows:
                                        # Get column names
                                        col_names = [description[0] for description in cursor.description]
                                        all_output.append('|'.join(col_names))
                                        for row in rows:
                                            all_output.append('|'.join(str(v) for v in row))
                            except sqlite3.Error as e:
                                errors.append(f"Query error: {str(e)}")
                    except Exception as e:
                        errors.append(f"Execution error: {str(e)}")
                
                conn.commit()
                conn.close()
                
                # Format output
                output = '\n'.join(all_output) if all_output else "Query executed successfully"
                stderr_output = '\n'.join(errors) if errors else ""
                
                # Validate output if expected_output provided
                is_correct = False
                if sql_expected_output and output:
                    expected_normalized = sql_expected_output.strip().split('\n')
                    actual_normalized = output.strip().split('\n')
                    is_correct = expected_normalized == actual_normalized
                
                execution_result = {
                    "language": "sql",
                    "code": code_content,
                    "problem_id": req.problem_id or "",
                    "constraint": constraint,
                    "stdout": output,
                    "stderr": stderr_output,
                    "expected_output": sql_expected_output,
                    "is_correct": is_correct,
                    "exit_code": 0 if not errors else 1,
                    "status": "success" if not errors else "error",
                    "timestamp": datetime.utcnow().isoformat(),
                    "created_at": datetime.utcnow()
                }
                
                save_code_execution_to_db(execution_result)
                
                return {
                    "run": {
                        "stdout": output,
                        "stderr": stderr_output,
                        "output": output if not stderr_output else output,
                        "code": 0 if not errors else 1,
                        "expected_output": sql_expected_output,
                        "is_correct": is_correct
                    }
                }
            except Exception as e:
                return {
                    "run": {
                        "stdout": "",
                        "stderr": str(e),
                        "output": str(e),
                        "code": 1
                    }
                }

        else:
            return {
                "run": {
                    "stdout": "",
                    "stderr": f"Language '{lang}' not supported. Supported: python, java, sql",
                    "output": f"Language not supported",
                    "code": 1
                }
            }

    except subprocess.TimeoutExpired:
        return {
            "run": {
                "stdout": "",
                "stderr": "Execution timeout (> 10s)",
                "output": "Execution timeout",
                "code": 124
            }
        }
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return {
            "run": {
                "stdout": "",
                "stderr": f"Error: {str(e)}",
                "output": f"Error: {str(e)}",
                "code": 1
            }
        }


@app.post("/submission")
async def submit_code(req: SubmissionRequest):
    """
    Execute code and save submission to database.
    Returns execution result + stores in MongoDB.
    """
    try:
        # First, run the code (same execution logic as /run)
        code_content = req.code
        lang = (req.language or "").lower().strip()
        
        print(f"[Submission] problem_id={req.problem_id}, user_id={req.user_id}, language={lang}", flush=True)
        
        if not code_content or not code_content.strip():
            return {
                "success": False,
                "error": "No code provided"
            }
        
        # Execute based on language (simplified - uses same logic as /run)
        result = await run_code(RunRequest(language=lang, files=[{"content": code_content}]))
        exec_result = result.get("run", {})
        
        # Prepare submission object for database
        submission = {
            "problem_id": req.problem_id,
            "user_id": req.user_id,
            "language": lang,
            "code": code_content,
            "stdout": exec_result.get("stdout", ""),
            "stderr": exec_result.get("stderr", ""),
            "exit_code": exec_result.get("code", -1),
            "status": "success" if exec_result.get("code") == 0 else "error",
            "execution_time": 0,  # Would need to measure actual time
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow()
        }
        
        # Save to database
        db_result = save_submission_to_db(submission)
        
        return {
            "success": True,
            "execution": exec_result,
            "submission_id": db_result.get("submission_id"),
            "database_mode": "mock" if MOCK_MODE else "mongodb"
        }
    
    except Exception as e:
        print(f"[ERROR] submit_code: {str(e)}", flush=True)
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/submissions/{user_id}")
async def get_user_submissions(user_id: str):
    """
    Fetch all submissions for a user (for code analyzer team).
    """
    try:
        client = get_mongodb_client()
        
        if MOCK_MODE or client is None:
            # Return mock submissions in mock mode
            return {
                "user_id": user_id,
                "mode": "mock",
                "submissions": [
                    {
                        "problem_id": "1",
                        "language": "python",
                        "status": "success",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ],
                "total": 1
            }
        
        # Fetch from MongoDB
        db = client[DB_NAME]
        submissions = list(db.submissions.find({"user_id": user_id}).sort("created_at", -1))
        
        # Remove MongoDB's _id field
        for sub in submissions:
            sub.pop('_id', None)
        
        return {
            "user_id": user_id,
            "mode": "mongodb",
            "submissions": submissions,
            "total": len(submissions)
        }
    
    except Exception as e:
        print(f"[ERROR] get_user_submissions: {str(e)}", flush=True)
        return {
            "user_id": user_id,
            "error": str(e),
            "submissions": []
        }


