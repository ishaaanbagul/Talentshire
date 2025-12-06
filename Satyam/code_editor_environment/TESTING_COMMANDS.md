# Testing Commands - Complete Guide

## Overview
This document contains all commands used for testing the flexible_model application, including explanations and use cases.

---

## PART 1: SETUP & INFRASTRUCTURE COMMANDS

### 1.1 Build and Start Docker Services

```bash
docker compose up -d --build
```

**Explanation:**
- `docker compose up` - Start all services defined in docker-compose.yml
- `-d` - Run in detached mode (background)
- `--build` - Rebuild images before starting
- **What happens:** Downloads base images (python:3.11-slim, node:18), builds backend and frontend, starts both services
- **Result:** Backend runs on port 8000, Frontend runs on port 3000

**When to use:** 
- First time setup
- After code changes
- After Dockerfile modifications

---

### 1.2 Check Running Containers

```bash
docker ps
```

**Explanation:**
- Lists all currently running containers
- Shows container ID, names, ports, status
- **What to look for:** 
  - `codeplay-backend` running on `0.0.0.0:8000->8000/tcp`
  - `codeplay-frontend` running on `0.0.0.0:3000->3000/tcp`

**When to use:**
- After `docker compose up` to verify both services started
- To check if containers are still running

---

### 1.3 View Backend Logs

```bash
docker logs codeplay-backend
```

**Explanation:**
- Shows all output from backend container
- Useful for debugging errors, seeing startup messages
- **Key logs to look for:**
  - `Uvicorn running on 0.0.0.0:8000`
  - Any MongoDB connection attempts
  - Any errors during startup

**When to use:**
- After code changes to verify no errors
- When API calls fail
- To check if backend is really running

---

### 1.4 View Frontend Logs

```bash
docker logs codeplay-frontend
```

**Explanation:**
- Shows all output from frontend container
- Less useful than backend logs (mostly Nginx messages)
- **Key logs to look for:**
  - Any build errors
  - Port binding messages

**When to use:**
- When frontend doesn't load on localhost:3000

---

### 1.5 Stop All Services

```bash
docker compose down
```

**Explanation:**
- Stops and removes all containers
- Removes temporary volumes
- Keeps images for faster restart
- **Does NOT delete:**
  - Docker images (can reuse)
  - Source code
  - Permanent data

**When to use:**
- Before rebuilding
- Before testing different configurations
- To clean up

---

### 1.6 Full Rebuild

```bash
docker compose down ; docker compose up -d --build
```

**Explanation:**
- Stop all services
- Remove containers
- Rebuild fresh images
- Start everything again
- `;` - PowerShell command separator (like && in Linux)

**When to use:**
- After major code changes
- When you encounter "image build cache" issues
- Fresh start testing

---

## PART 2: HEALTH CHECK & BASIC CONNECTIVITY

### 2.1 Check Backend Health Endpoint

```powershell
curl -X GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "mongodb_mode": "mock",
  "code_execution_type": "direct_subprocess"
}
```

**Explanation:**
- GET request to `/health` endpoint
- Returns current mode:
  - `mongodb_mode: "mock"` = Database not connected (using hardcoded data)
  - `mongodb_mode: "connected"` = MongoDB connected
  - `code_execution_type: "direct_subprocess"` = Using direct execution (not Judge0/Piston)

**When to use:**
- After starting services to verify backend is alive
- Before running code execution tests
- To verify connection mode

---

### 2.2 Check Frontend is Running

```powershell
curl -X GET http://localhost:3000
```

**Response:**
- HTML content of React app
- If working, you'll see `<!DOCTYPE html>...`

**When to use:**
- Verify frontend is serving correctly
- Quick check before opening in browser

---

## PART 3: PROBLEM FETCHING TESTS

### 3.1 Fetch Problem with Mock Data

```powershell
curl -X GET http://localhost:8000/problem/1 | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Explanation:**
- GET `/problem/1` - Fetch problem with ID "1"
- `ConvertFrom-Json` - Parse JSON response
- `ConvertTo-Json -Depth 10` - Pretty print with 10 levels depth

**Response includes:**
```json
{
  "id": "1",
  "title": "Sum Two Numbers",
  "body": "Write a program that sums two numbers",
  "constraints": "1 <= a, b <= 1000",
  "languages": ["python", "java", "sql"],
  "sql_schema": "CREATE TABLE numbers (a INT, b INT);",
  "sql_test_data": "INSERT INTO numbers VALUES (3, 5), (0, 0), (1000000000, 1000000000);",
  "sql_expected_output": "8\n0\n2000000000"
}
```

**What it tells you:**
- Problem data loaded correctly
- All fields present (including SQL schema)
- Constraints available for display

**When to use:**
- Before code execution tests
- Verify problem data structure
- Debug missing fields

---

### 3.2 Fetch Non-Existent Problem

```powershell
curl -X GET http://localhost:8000/problem/999
```

**Response:**
```json
{
  "id": "999",
  "title": "Mock Problem (Not in Database)",
  "body": "Problem not found - using mock data for testing"
}
```

**Explanation:**
- When problem doesn't exist, returns mock data
- Shows app gracefully handles missing data
- Safe for offline/testing mode

**When to use:**
- Verify fallback mechanism works

---

## PART 4: PYTHON CODE EXECUTION TESTS

### 4.1 Simple Python Calculation

```powershell
$payload = @{
    language = "python"
    version = "latest"
    files = @(@{
        name = "main"
        content = "print(3+5)"
    })
    stdin = ""
} | ConvertTo-Json

curl -X POST http://localhost:8000/run `
  -ContentType "application/json" `
  -Body $payload
```

**Explanation:**
- `$payload` - Create request object in PowerShell
- `language: "python"` - Execute as Python code
- `files[0].content` - The Python code to run
- `print(3+5)` - Output should be "8"

**Expected Response:**
```json
{
  "run": {
    "stdout": "8\n",
    "stderr": "",
    "output": "8\n",
    "code": 0
  }
}
```

**Key fields:**
- `stdout` - Program output (should be "8\n")
- `stderr` - Error messages (empty if success)
- `code` - Exit code (0 = success, non-zero = error)

**When to use:**
- First test after docker starts
- Verify Python execution works
- Check output capture

---

### 4.2 Python with Input (stdin)

```powershell
$payload = @{
    language = "python"
    files = @(@{
        name = "main"
        content = "a = input(); print(int(a) * 2)"
    })
    stdin = "5"
} | ConvertTo-Json

curl -X POST http://localhost:8000/run `
  -ContentType "application/json" `
  -Body $payload
```

**Explanation:**
- `stdin: "5"` - Provide input to program (like piping input)
- `input()` - Reads from stdin
- Program doubles the input

**Expected Response:**
```json
{
  "stdout": "10\n",
  "stderr": "",
  "code": 0
}
```

**When to use:**
- Test stdin handling
- Verify input redirection works

---

### 4.3 Python with Error

```powershell
$payload = @{
    language = "python"
    files = @(@{
        name = "main"
        content = "print(1/0)"
    })
    stdin = ""
} | ConvertTo-Json

curl -X POST http://localhost:8000/run `
  -ContentType "application/json" `
  -Body $payload
```

**Expected Response:**
```json
{
  "stdout": "",
  "stderr": "Traceback (most recent call last):\n  File ...\nZeroDivisionError: division by zero",
  "output": "ZeroDivisionError: division by zero",
  "code": 1
}
```

**What it shows:**
- Error is captured in stderr
- Exit code is 1 (failure)
- Program didn't crash the backend

**When to use:**
- Test error handling
- Verify error messages captured

---

### 4.4 Python with Problem ID (Fetch Constraint)

```powershell
$payload = @{
    language = "python"
    files = @(@{
        name = "main"
        content = "print(3+5)"
    })
    stdin = ""
    problem_id = "1"
} | ConvertTo-Json

curl -X POST http://localhost:8000/run `
  -ContentType "application/json" `
  -Body $payload
```

**Explanation:**
- `problem_id: "1"` - Fetch problem from database
- Backend fetches problem, gets constraints
- Stores execution with problem_id and constraint

**Expected Response:**
```json
{
  "run": {
    "stdout": "8\n",
    "stderr": "",
    "code": 0
  },
  "problem_id": "1",
  "constraint": "1 <= a, b <= 1000"
}
```

**What it shows:**
- Problem fetching works
- Constraint included in response
- Execution linked to problem

**When to use:**
- Test problem integration
- Verify constraint propagation
- Test execution storage (with problem_id)

---

## PART 5: JAVA CODE EXECUTION TESTS

### 5.1 Simple Java Program

```powershell
$payload = @{
    language = "java"
    files = @(@{
        name = "Main"
        content = "public class Main { public static void main(String[] args) { System.out.println(3+5); } }"
    })
    stdin = ""
} | ConvertTo-Json

curl -X POST http://localhost:8000/run `
  -ContentType "application/json" `
  -Body $payload
```

**Explanation:**
- `language: "java"` - Compile and execute Java
- `name: "Main"` - File name (becomes Main.java)
- Class name **must match** file name for compilation
- Backend extracts class name from code using regex

**Expected Response:**
```json
{
  "run": {
    "stdout": "8\n",
    "stderr": "",
    "output": "8\n",
    "code": 0
  }
}
```

**Process:**
1. Backend creates `Main.java` with code
2. Runs `javac Main.java` (compiles)
3. Runs `java Main` (executes)
4. Captures output
5. Cleans up temp files

**When to use:**
- Test Java compilation
- Verify class name extraction
- Test compilation error handling

---

### 5.2 Java with Compilation Error

```powershell
$payload = @{
    language = "java"
    files = @(@{
        name = "Main"
        content = "public class Main { public static void main(String[] args) { System.out.println(3+5) } }"
    })
    stdin = ""
} | ConvertTo-Json

curl -X POST http://localhost:8000/run `
  -ContentType "application/json" `
  -Body $payload
```

**Explanation:**
- Missing `;` at end of println statement (syntax error)

**Expected Response:**
```json
{
  "run": {
    "stdout": "",
    "stderr": "Main.java:1: error: ';' expected",
    "output": "error: ';' expected",
    "code": 1
  }
}
```

**When to use:**
- Test compilation error capture
- Verify helpful error messages

---

### 5.3 Java with Input

```powershell
$payload = @{
    language = "java"
    files = @(@{
        name = "Main"
        content = "import java.util.Scanner; public class Main { public static void main(String[] args) { Scanner s = new Scanner(System.in); int x = s.nextInt(); System.out.println(x*2); } }"
    })
    stdin = "5"
} | ConvertTo-Json

curl -X POST http://localhost:8000/run `
  -ContentType "application/json" `
  -Body $payload
```

**Expected Response:**
```json
{
  "stdout": "10\n",
  "stderr": "",
  "code": 0
}
```

**When to use:**
- Test Java stdin handling
- Verify Scanner input works

---

## PART 6: SQL CODE EXECUTION TESTS

### 6.1 SQL Option 2 - Structured Mode (With Problem ID)

**Test Case: SELECT Query**

```powershell
$payload = @{
    language = "sql"
    files = @(@{
        name = "query"
        content = "SELECT a + b FROM numbers;"
    })
    stdin = ""
    problem_id = "1"
} | ConvertTo-Json

curl -X POST http://localhost:8000/run `
  -ContentType "application/json" `
  -Body $payload
```

**Explanation:**
- `problem_id: "1"` - Use Option 2 (structured mode)
- Backend loads:
  - `sql_schema`: CREATE TABLE numbers (a INT, b INT);
  - `sql_test_data`: INSERT INTO numbers VALUES (3, 5), (0, 0), (1000000000, 1000000000);
  - `sql_expected_output`: 8\n0\n2000000000
- Executes user's SELECT query
- Compares output with expected

**Expected Response:**
```json
{
  "run": {
    "stdout": "a + b\n8\n0\n2000000000",
    "stderr": "",
    "code": 0
  },
  "expected_output": "8\n0\n2000000000",
  "is_correct": false
}
```

**Analysis:**
- Query executed ✅
- Output captured: "a + b\n8\n0\n2000000000"
- Expected output: "8\n0\n2000000000"
- `is_correct: false` because column header "a + b" was included (mismatch)

**When to use:**
- Test SQL Option 2 structured mode
- Verify schema loading
- Verify output comparison

---

### 6.2 SQL Option 2 - Blocked INSERT

**Test Case: Attempt to INSERT in Structured Mode**

```powershell
$payload = @{
    language = "sql"
    files = @(@{
        name = "query"
        content = "INSERT INTO numbers VALUES (5, 10); SELECT * FROM numbers;"
    })
    stdin = ""
    problem_id = "1"
} | ConvertTo-Json

curl -X POST http://localhost:8000/run `
  -ContentType "application/json" `
  -Body $payload
```

**Expected Response:**
```json
{
  "run": {
    "stdout": "Query executed successfully",
    "stderr": "Error: Only SELECT queries allowed. Cannot use CREATE, INSERT, DROP, etc.",
    "code": 1
  },
  "is_correct": false
}
```

**What it shows:**
- INSERT detected and blocked ✅
- Error message clear ✅
- Exit code 1 (error) ✅
- Prevents data tampering ✅

**When to use:**
- Test query validation
- Verify INSERT blocking works
- Ensure security of structured problems

---

### 6.3 SQL Option 1 - Flexible Mode (Without Problem ID)

**Test Case: Any SQL Allowed**

```powershell
$payload = @{
    language = "sql"
    files = @(@{
        name = "query"
        content = "CREATE TABLE test (id INT, name TEXT); INSERT INTO test VALUES (1, 'Alice'), (2, 'Bob'); SELECT * FROM test;"
    })
    stdin = ""
} | ConvertTo-Json

curl -X POST http://localhost:8000/run `
  -ContentType "application/json" `
  -Body $payload
```

**Explanation:**
- NO `problem_id` provided
- Uses Option 1 (flexible mode)
- User can write CREATE, INSERT, SELECT freely
- No validation of query type

**Expected Response:**
```json
{
  "run": {
    "stdout": "id|name\n1|Alice\n2|Bob",
    "stderr": "",
    "code": 0
  },
  "is_correct": false
}
```

**What it shows:**
- CREATE TABLE ✅
- INSERT VALUES ✅
- SELECT results ✅
- All SQL allowed ✅
- Backward compatibility preserved ✅

**When to use:**
- Test SQL Option 1 (flexible)
- Test backward compatibility
- Verify freedom in flexible mode

---

### 6.4 SQL - CREATE TABLE Only

```powershell
$payload = @{
    language = "sql"
    files = @(@{
        name = "query"
        content = "CREATE TABLE temp (x INT, y INT);"
    })
    stdin = ""
} | ConvertTo-Json

curl -X POST http://localhost:8000/run `
  -ContentType "application/json" `
  -Body $payload
```

**Expected Response:**
```json
{
  "run": {
    "stdout": "Query executed successfully",
    "stderr": "",
    "code": 0
  }
}
```

**When to use:**
- Test CREATE TABLE execution
- Verify no error on structure creation

---

### 6.5 SQL - INSERT with SELECT

```powershell
$payload = @{
    language = "sql"
    files = @(@{
        name = "query"
        content = "CREATE TABLE users (id INT, name TEXT); INSERT INTO users VALUES (1, 'Alice'); SELECT COUNT(*) FROM users;"
    })
    stdin = ""
} | ConvertTo-Json

curl -X POST http://localhost:8000/run `
  -ContentType "application/json" `
  -Body $payload
```

**Expected Response:**
```json
{
  "run": {
    "stdout": "COUNT(*)\n1",
    "stderr": "",
    "code": 0
  }
}
```

**When to use:**
- Test complex SQL queries
- Verify aggregation functions work

---

## PART 7: SUBMISSION ENDPOINT TESTS

### 7.1 Submit Code Execution

```powershell
$payload = @{
    user_id = "student123"
    problem_id = "1"
    language = "python"
    code = "print(3+5)"
    stdin = ""
} | ConvertTo-Json

curl -X POST http://localhost:8000/submission `
  -ContentType "application/json" `
  -Body $payload
```

**Explanation:**
- POST to `/submission` endpoint
- Executes code AND stores result
- Different from `/run` (only executes)

**Expected Response:**
```json
{
  "user_id": "student123",
  "problem_id": "1",
  "language": "python",
  "code": "print(3+5)",
  "stdout": "8\n",
  "stderr": "",
  "status": "success",
  "timestamp": "2025-12-06T10:30:45.123456"
}
```

**When to use:**
- Test submission storage
- Verify execution + storage workflow

---

### 7.2 Retrieve User Submissions

```powershell
curl -X GET http://localhost:8000/submissions/student123
```

**Expected Response:**
```json
{
  "user_id": "student123",
  "submissions": [
    {
      "problem_id": "1",
      "language": "python",
      "code": "print(3+5)",
      "stdout": "8\n",
      "timestamp": "2025-12-06T10:30:45.123456"
    },
    {
      "problem_id": "2",
      "language": "java",
      "code": "...",
      "stdout": "...",
      "timestamp": "2025-12-06T10:35:20.654321"
    }
  ]
}
```

**Explanation:**
- Fetches all submissions for a user
- Used by Analyzer team to process results
- Shows execution history

**When to use:**
- Test data retrieval
- Verify submission history works

---

## PART 8: TIMEOUT & ERROR HANDLING TESTS

### 8.1 Python Infinite Loop (Timeout Test)

```powershell
$payload = @{
    language = "python"
    files = @(@{
        name = "main"
        content = "while True: pass"
    })
    stdin = ""
} | ConvertTo-Json

curl -X POST http://localhost:8000/run `
  -ContentType "application/json" `
  -Body $payload
```

**Expected Response (After ~10 seconds):**
```json
{
  "run": {
    "stdout": "",
    "stderr": "Execution timed out after 10 seconds",
    "output": "Execution timed out after 10 seconds",
    "code": -1
  }
}
```

**What it shows:**
- Timeout enforcement works ✅
- Backend protected from hanging ✅
- Error message clear ✅

**When to use:**
- Test timeout limits
- Verify protection from infinite loops

---

### 8.2 Java Timeout Test

```powershell
$payload = @{
    language = "java"
    files = @(@{
        name = "Main"
        content = "public class Main { public static void main(String[] args) { while(true) {} } }"
    })
    stdin = ""
} | ConvertTo-Json

curl -X POST http://localhost:8000/run `
  -ContentType "application/json" `
  -Body $payload
```

**Expected Response (After ~10 seconds):**
```json
{
  "run": {
    "stdout": "",
    "stderr": "Execution timed out after 10 seconds",
    "code": -1
  }
}
```

**When to use:**
- Test Java timeout limits
- Verify consistent timeout behavior

---

## PART 9: BATCH TESTING SCRIPT

**PowerShell Script to Run All Tests (save as `test_all.ps1`):**

```powershell
# Test 1: Health Check
Write-Host "Test 1: Health Check" -ForegroundColor Green
curl -X GET http://localhost:8000/health

# Test 2: Problem Fetching
Write-Host "`nTest 2: Fetch Problem" -ForegroundColor Green
curl -X GET http://localhost:8000/problem/1

# Test 3: Python Execution
Write-Host "`nTest 3: Python Execution" -ForegroundColor Green
$payload = @{ language = "python"; files = @(@{ name = "main"; content = "print(3+5)" }); stdin = "" } | ConvertTo-Json
curl -X POST http://localhost:8000/run -ContentType "application/json" -Body $payload

# Test 4: Java Execution
Write-Host "`nTest 4: Java Execution" -ForegroundColor Green
$payload = @{ language = "java"; files = @(@{ name = "Main"; content = "public class Main { public static void main(String[] args) { System.out.println(3+5); } }" }); stdin = "" } | ConvertTo-Json
curl -X POST http://localhost:8000/run -ContentType "application/json" -Body $payload

# Test 5: SQL Option 2
Write-Host "`nTest 5: SQL Option 2 (Structured)" -ForegroundColor Green
$payload = @{ language = "sql"; files = @(@{ name = "query"; content = "SELECT a + b FROM numbers;" }); stdin = ""; problem_id = "1" } | ConvertTo-Json
curl -X POST http://localhost:8000/run -ContentType "application/json" -Body $payload

Write-Host "`nAll tests completed!" -ForegroundColor Cyan
```

**Run with:**
```bash
powershell -ExecutionPolicy Bypass -File test_all.ps1
```

---

## PART 10: QUICK REFERENCE TABLE

| Test | Command | Expected Output | What It Tests |
|------|---------|-----------------|---------------|
| Health | `curl GET /health` | `{"status":"healthy"}` | Backend alive |
| Problem | `curl GET /problem/1` | Problem JSON with constraints | Problem fetching |
| Python Basic | `POST /run` with `print(3+5)` | `stdout: "8\n"` | Python execution |
| Python Error | `POST /run` with `print(1/0)` | Error in stderr | Error handling |
| Python Timeout | `POST /run` with `while True` | Timeout error after 10s | Timeout protection |
| Java Basic | `POST /run` with Java code | `stdout: "8\n"` | Java compilation + execution |
| Java Error | `POST /run` with syntax error | Error in stderr | Compilation errors |
| SQL Option 2 | `POST /run` with SELECT + problem_id | Results with is_correct | SQL validation |
| SQL Blocked | `POST /run` with INSERT + problem_id | Error in stderr | INSERT blocking |
| SQL Flexible | `POST /run` with CREATE + no problem_id | Results, no blocking | SQL flexibility |
| Submission | `POST /submission` | Execution result | Submission storage |
| Retrieve | `GET /submissions/user_id` | List of submissions | Data retrieval |

---

## PART 11: TROUBLESHOOTING

### Backend Not Starting

```bash
docker logs codeplay-backend
```

Look for:
- `Uvicorn running on 0.0.0.0:8000` = Success
- `ModuleNotFoundError` = Missing Python package
- `Connection refused` = Port 8000 already in use

---

### Code Execution Failing

```bash
# Check if Docker has enough resources
docker stats

# Restart containers
docker compose restart

# Rebuild everything
docker compose down
docker compose up -d --build
```

---

### Timeout Issues

Increase timeout in `backend/main.py` line 260:
```python
timeout=10  # Change to 15 or 30 for longer timeout
```

Then rebuild:
```bash
docker compose up -d --build
```

---

## PART 12: TESTING CHECKLIST

- [ ] Health endpoint returns `healthy`
- [ ] Problem endpoint returns mock data
- [ ] Python code executes and outputs correct result
- [ ] Java code compiles and executes
- [ ] SQL SELECT executes in structured mode
- [ ] SQL INSERT blocked in structured mode
- [ ] SQL flexible mode allows all queries
- [ ] Timeout protection works
- [ ] Error messages are clear
- [ ] Submissions stored correctly
- [ ] User submissions retrieved correctly
- [ ] Frontend loads on localhost:3000
- [ ] Offline mode works (no MongoDB)

---

## Summary

**Total Test Cases: 20+**
- Infrastructure tests: 6
- Health & connectivity: 2
- Problem fetching: 2
- Python execution: 4
- Java execution: 3
- SQL execution: 5
- Submission tests: 2
- Timeout & error: 2
- Reference table: 12

**All tests are:**
- ✅ Repeatable
- ✅ Documented with explanations
- ✅ Show expected outputs
- ✅ Include debugging tips
- ✅ Production-ready

Use these commands for:
- Initial verification after setup
- Integration testing
- Debugging issues
- Demonstrating features
- Regression testing after changes

