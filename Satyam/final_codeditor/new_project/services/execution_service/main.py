"""
Code Execution Microservice
Handles: Python, Java, SQL, PySpark execution
Port: 8001
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import subprocess
import sys
import tempfile
import os
import shutil
import re
from datetime import datetime
import json

app = FastAPI(title="Code Execution Service", version="1.0.0")

# MongoDB Configuration with Authentication
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://root:password@mongodb:27017/codeplay?authSource=admin")

# Request Model
class RunRequest(BaseModel):
    language: str
    files: Optional[List[dict]] = None
    stdin: Optional[str] = ""
    problem_id: Optional[str] = None
    user_id: Optional[str] = None

# ========================= EXECUTION FUNCTIONS =========================

def execute_python(code_content: str, stdin_data: str = "") -> dict:
    """Execute Python code"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code_content],
            input=stdin_data.encode() if stdin_data else b"",
            capture_output=True,
            timeout=10
        )
        
        stdout = result.stdout.decode('utf-8', errors='replace')
        stderr = result.stderr.decode('utf-8', errors='replace')
        
        return {
            "language": "python",
            "code": code_content,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": result.returncode,
            "status": "success" if result.returncode == 0 else "error",
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow()
        }
    except subprocess.TimeoutExpired:
        return {
            "language": "python",
            "code": code_content,
            "stdout": "",
            "stderr": "Execution timed out after 10 seconds",
            "exit_code": -1,
            "status": "timeout",
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow()
        }
    except Exception as e:
        return {
            "language": "python",
            "code": code_content,
            "stdout": "",
            "stderr": str(e),
            "exit_code": 1,
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow()
        }

def execute_java(code_content: str, stdin_data: str = "") -> dict:
    """Execute Java code"""
    try:
        # Extract class name using regex - matches both public and non-public classes
        class_name_match = re.search(r'(?:public\s+)?class\s+(\w+)', code_content)
        if not class_name_match:
            return {
                "language": "java",
                "code": code_content,
                "stdout": "",
                "stderr": "Error: No class found in code",
                "exit_code": 1,
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow()
            }
        
        class_name = class_name_match.group(1)
        temp_dir = tempfile.mkdtemp()
        java_file = os.path.join(temp_dir, f"{class_name}.java")
        
        # Write code to file
        with open(java_file, 'w') as f:
            f.write(code_content)
        
        # Compile
        compile_result = subprocess.run(
            ["javac", java_file],
            capture_output=True,
            timeout=10,
            cwd=temp_dir
        )
        
        if compile_result.returncode != 0:
            stderr = compile_result.stderr.decode('utf-8', errors='replace')
            shutil.rmtree(temp_dir)
            return {
                "language": "java",
                "code": code_content,
                "stdout": "",
                "stderr": stderr,
                "exit_code": 1,
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow()
            }
        
        # Execute
        run_result = subprocess.run(
            ["java", "-cp", temp_dir, class_name],
            input=stdin_data.encode() if stdin_data else b"",
            capture_output=True,
            timeout=10
        )
        
        stdout = run_result.stdout.decode('utf-8', errors='replace')
        stderr = run_result.stderr.decode('utf-8', errors='replace')
        
        shutil.rmtree(temp_dir)
        
        return {
            "language": "java",
            "code": code_content,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": run_result.returncode,
            "status": "success" if run_result.returncode == 0 else "error",
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow()
        }
        
    except subprocess.TimeoutExpired:
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)
        return {
            "language": "java",
            "code": code_content,
            "stdout": "",
            "stderr": "Execution timed out after 10 seconds",
            "exit_code": -1,
            "status": "timeout",
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow()
        }
    except Exception as e:
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)
        return {
            "language": "java",
            "code": code_content,
            "stdout": "",
            "stderr": str(e),
            "exit_code": 1,
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow()
        }

def execute_sql(code_content: str, stdin_data: str = "") -> dict:
    """Execute SQL code"""
    try:
        import sqlite3
        
        # Create in-memory database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Execute user code
        cursor.execute(code_content)
        
        # Fetch results if SELECT
        if code_content.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            
            # Format output
            if results:
                # Get column names
                col_names = [description[0] for description in cursor.description]
                output = "|".join(col_names) + "\n"
                for row in results:
                    output += "|".join(str(x) for x in row) + "\n"
            else:
                output = "No results"
        else:
            output = "Query executed successfully"
        
        conn.close()
        
        return {
            "language": "sql",
            "code": code_content,
            "stdout": output,
            "stderr": "",
            "exit_code": 0,
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow()
        }
        
    except Exception as e:
        return {
            "language": "sql",
            "code": code_content,
            "stdout": "",
            "stderr": str(e),
            "exit_code": 1,
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow()
        }

def execute_pyspark(code_content: str, stdin_data: str = "") -> dict:
    """Execute PySpark code"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code_content],
            input=stdin_data.encode() if stdin_data else b"",
            capture_output=True,
            timeout=30,  # Longer timeout for Spark
            env={
                **os.environ,
                "JAVA_HOME": "/usr/lib/jvm/default-java",
                "SPARK_LOCAL_IP": "127.0.0.1"
            }
        )
        
        stdout = result.stdout.decode('utf-8', errors='replace')
        stderr = result.stderr.decode('utf-8', errors='replace')
        
        return {
            "language": "pyspark",
            "code": code_content,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": result.returncode,
            "status": "success" if result.returncode == 0 else "error",
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow()
        }
    except subprocess.TimeoutExpired:
        return {
            "language": "pyspark",
            "code": code_content,
            "stdout": "",
            "stderr": "Execution timed out after 30 seconds",
            "exit_code": -1,
            "status": "timeout",
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow()
        }
    except Exception as e:
        return {
            "language": "pyspark",
            "code": code_content,
            "stdout": "",
            "stderr": str(e),
            "exit_code": 1,
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow()
        }

# ========================= API ENDPOINTS =========================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Code Execution Service",
        "port": 8001,
        "supported_languages": ["python", "java", "sql", "pyspark"]
    }

@app.post("/run")
async def run_code(req: RunRequest):
    """Execute code and return result"""
    
    # Extract code from files
    code_content = ""
    if req.files and len(req.files) > 0:
        code_content = req.files[0].get('content', '')
    
    if not code_content:
        raise HTTPException(status_code=400, detail="No code provided")
    
    # Route to appropriate executor
    if req.language == "python":
        result = execute_python(code_content, req.stdin or "")
    elif req.language == "java":
        result = execute_java(code_content, req.stdin or "")
    elif req.language == "sql":
        result = execute_sql(code_content, req.stdin or "")
    elif req.language == "pyspark":
        result = execute_pyspark(code_content, req.stdin or "")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {req.language}")
    
    # Add problem_id if provided
    if req.problem_id:
        result["problem_id"] = req.problem_id
    
    if req.user_id:
        result["user_id"] = req.user_id
    
    # Return execution result
    return {
        "run": {
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "output": result.get("stdout", "") or result.get("stderr", ""),
            "code": result.get("exit_code", 1)
        },
        "language": result.get("language"),
        "status": result.get("status"),
        "problem_id": req.problem_id,
        "user_id": req.user_id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
