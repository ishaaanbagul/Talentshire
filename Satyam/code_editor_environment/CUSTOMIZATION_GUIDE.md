# Customization Guide - Where to Make Changes

## Overview
This guide shows you exactly where to modify parameters for fetching problems and storing results.

---

## 1. FETCHING CODING PROBLEMS

### Current Default (Mock Data):
Returns: `id, title, body, sample_input, sample_output, constraints, difficulty, languages, time_limit, test_cases, sql_schema, sql_test_data, sql_expected_output`

### If You Want to ADD New Parameters

**Location:** `backend/main.py` → Function `get_problem_from_db()`

**Current Lines:** 60-115

**Example: Adding `author` and `tags` fields**

```python
# BEFORE (Line 75-85):
"languages": ["python", "java", "sql"],
"time_limit": 10,
"test_cases": [...]
}

# AFTER (Add these lines):
"languages": ["python", "java", "sql"],
"time_limit": 10,
"author": "admin_user",           # ← ADD THIS
"tags": ["array", "sorting"],     # ← ADD THIS
"test_cases": [...]
}
```

**Files to modify:**
1. `backend/main.py` - Mock data (lines 60-115)
2. MongoDB schema (Admin team's `coding_problems` collection) - Add fields there too

---

### If You Want to REMOVE Parameters

**Location:** `backend/main.py` → Function `get_problem_from_db()`

**Example: Remove `time_limit` and `test_cases`**

Simply delete these lines from the mock data returns:
```python
"time_limit": 10,
"test_cases": [...]
```

**Note:** Frontend won't use them if not provided

---

### If You Want to RENAME Parameters

**Location:** `backend/main.py` → Function `get_problem_from_db()`

**Example: Rename `sample_input` to `input_example`**

```python
# BEFORE:
"sample_input": "3 5",

# AFTER:
"input_example": "3 5",
```

**Then update Frontend:** `frontend/src/components/EditorPanel.jsx` (if displaying it)

---

## 2. STORING CODE EXECUTION RESULTS

### Current Default (Saved Fields):
For every code execution:
```
language, code, problem_id, constraint, stdout, stderr, 
expected_output (SQL only), is_correct (SQL only), 
exit_code, status, timestamp, created_at
```

### If You Want to ADD New Fields

**Location:** `backend/main.py` → Function `save_code_execution_to_db()`

**You need to modify 3 places:**

#### A. Python Execution (Lines 265-283)
```python
execution_result = {
    "language": "python",
    "code": code_content,
    "problem_id": req.problem_id or "",
    "constraint": constraint,
    "stdout": result.stdout.decode('utf-8', errors='replace'),
    "stderr": result.stderr.decode('utf-8', errors='replace'),
    "exit_code": result.returncode,
    "status": "success" if result.returncode == 0 else "error",
    "execution_time": 2.5,              # ← ADD THIS
    "memory_used": 512,                 # ← ADD THIS
    "timestamp": datetime.utcnow().isoformat(),
    "created_at": datetime.utcnow()
}
```

#### B. Java Execution - Compile Error (Lines 314-328)
Add same fields here

#### C. Java Execution - Success (Lines 337-355)
Add same fields here

#### D. SQL Execution (Lines 490-510)
Add same fields here

---

### Example: Add `execution_time` Field

**File:** `backend/main.py`

**For Python (Around line 260):**
```python
import time

# BEFORE execution:
start_time = time.time()
result = subprocess.run(...)
execution_time = time.time() - start_time

# IN execution_result dict (Add line):
"execution_time": round(execution_time, 3),
```

**For Java (Around line 338):**
```python
import time

start_time = time.time()
run_result = subprocess.run(...)
execution_time = time.time() - start_time

# IN execution_result dict (Add line):
"execution_time": round(execution_time, 3),
```

**For SQL (Around line 479):**
```python
import time

start_time = time.time()
# All the SQL operations...
execution_time = time.time() - start_time

# IN execution_result dict (Add line):
"execution_time": round(execution_time, 3),
```

---

### If You Want to REMOVE Fields

**Location:** `backend/main.py` → execution_result dictionaries

Simply delete lines you don't need. Example: Don't save `stderr`

```python
execution_result = {
    "language": "python",
    "code": code_content,
    "problem_id": req.problem_id or "",
    # "stderr": result.stderr.decode(...),  ← COMMENT OUT OR DELETE
    "exit_code": result.returncode,
    # ... rest
}
```

---

### If You Want to RENAME Fields

**Example: Rename `constraint` to `problem_constraint`**

```python
# BEFORE:
"constraint": constraint,

# AFTER:
"problem_constraint": constraint,
```

**Then also update Frontend:** If frontend displays this field, update `frontend/src/components/EditorPanel.jsx`

---

## 3. API REQUEST PARAMETERS

### If You Want to ADD/CHANGE Request Parameters

**Location:** `backend/main.py` → Class `RunRequest` (Lines 187-192)

**Current:**
```python
class RunRequest(BaseModel):
    language: str
    version: Optional[str] = None
    files: Optional[list] = None
    stdin: Optional[str] = ""
    problem_id: Optional[str] = None
```

**Example: Add `user_id` and `time_limit_override` parameters**

```python
class RunRequest(BaseModel):
    language: str
    version: Optional[str] = None
    files: Optional[list] = None
    stdin: Optional[str] = ""
    problem_id: Optional[str] = None
    user_id: Optional[str] = None              # ← ADD
    time_limit_override: Optional[int] = None  # ← ADD
```

**Then use in code execution:**
```python
@app.post("/run")
async def run_code(req: RunRequest):
    # Access like: req.user_id, req.time_limit_override
    if req.time_limit_override:
        timeout = req.time_limit_override
    else:
        timeout = 10
```

---

## 4. FRONTEND - WHAT PARAMETERS TO SEND

### Current Frontend Request

**Location:** `frontend/src/components/EditorPanel.jsx` (Lines 28-34)

```javascript
const payload = {
    language: language,
    version: null,
    files: [{ name: 'main', content: code }],
    stdin: stdin,
    problem_id: problem_id  // If fetched from /problem/{id}
}
```

### If You Want to ADD Parameters to Send

**File:** `frontend/src/components/EditorPanel.jsx`

```javascript
// ADD state for user_id (Lines 15-16):
const [userId, setUserId] = useState('user123')

// ADD to payload (Lines 28-34):
const payload = {
    language: language,
    version: null,
    files: [{ name: 'main', content: code }],
    stdin: stdin,
    problem_id: problem_id,
    user_id: userId  // ← ADD THIS
}
```

---

## 5. RESPONSE PARAMETERS

### If You Want to CHANGE What /run Returns

**Location:** `backend/main.py` → Return statements in `run_code()` function

**Current (Python - Lines 280-286):**
```python
return {
    "run": {
        "stdout": result.stdout.decode('utf-8', errors='replace'),
        "stderr": result.stderr.decode('utf-8', errors='replace'),
        "output": result.stdout.decode(...) or result.stderr.decode(...),
        "code": result.returncode
    }
}
```

**Example: Add `execution_time` to response**

```python
return {
    "run": {
        "stdout": result.stdout.decode('utf-8', errors='replace'),
        "stderr": result.stderr.decode('utf-8', errors='replace'),
        "output": result.stdout.decode(...) or result.stderr.decode(...),
        "code": result.returncode,
        "execution_time": 0.234  # ← ADD
    }
}
```

---

## 6. MONGODB STORAGE

### If Admin Team Wants to Store Different Problem Fields

**Collection:** `coding_problems`

**Current Schema:**
```json
{
  "id": "1",
  "title": "...",
  "body": "...",
  "constraints": "...",
  "languages": ["python", "java", "sql"],
  "sql_schema": "...",
  "sql_test_data": "...",
  "sql_expected_output": "..."
}
```

**To Add Fields:** Admin just inserts new fields in MongoDB
```json
{
  "id": "1",
  "title": "...",
  "author": "admin",           # ← New
  "difficulty": "Medium",      # ← New
  "custom_timeout": 15,        # ← New
  ...
}
```

**Your backend will automatically include them** (no code changes needed) because you return the entire problem object!

---

## 7. PRACTICAL EXAMPLES

### Example 1: Add User Tracking

**Step 1:** Add to RunRequest (`backend/main.py`):
```python
class RunRequest(BaseModel):
    # ... existing ...
    user_id: Optional[str] = None
    session_id: Optional[str] = None
```

**Step 2:** Save in execution_result (all 4 places - Python, Java SQL):
```python
execution_result = {
    # ... existing ...
    "user_id": req.user_id or "",
    "session_id": req.session_id or "",
}
```

**Step 3:** Frontend sends it:
```javascript
const payload = {
    // ... existing ...
    user_id: "student_123",
    session_id: "session_xyz"
}
```

---

### Example 2: Add Memory/Time Tracking

**Step 1:** Import time at top of `main.py`:
```python
import time
import resource  # For memory tracking
```

**Step 2:** Wrap Python execution:
```python
import psutil
import os

start_time = time.time()
process = subprocess.Popen([sys.executable, "-c", code_content], ...)
stdout, stderr = process.communicate(timeout=10)
execution_time = time.time() - start_time

# Get memory usage (if available)
try:
    process_info = psutil.Process(process.pid)
    memory_mb = process_info.memory_info().rss / 1024 / 1024
except:
    memory_mb = 0

execution_result = {
    # ...
    "execution_time": round(execution_time, 3),
    "memory_mb": round(memory_mb, 2)
}
```

---

### Example 3: Store Test Case Results

**Step 1:** Add to execution_result:
```python
test_results = [
    {"case": 1, "pass": True, "expected": "8", "actual": "8"},
    {"case": 2, "pass": False, "expected": "0", "actual": "1"}
]

execution_result = {
    # ...
    "test_case_results": test_results,
    "passed_cases": 1,
    "total_cases": 2
}
```

---

## Summary: Files to Modify

| If You Want To... | File | Lines | Function |
|-------------------|------|-------|----------|
| Add fetch parameters | `backend/main.py` | 60-115 | `get_problem_from_db()` |
| Remove fetch parameters | `backend/main.py` | 60-115 | `get_problem_from_db()` |
| Add storage fields | `backend/main.py` | 265-510 | `run_code()` (all language blocks) |
| Add request parameters | `backend/main.py` | 187-192 | `RunRequest` class |
| Add response fields | `backend/main.py` | All returns in `run_code()` | Return statements |
| Add frontend parameters | `frontend/src/components/EditorPanel.jsx` | 15-35 | `EditorPanel()` |
| Change MongoDB schema | MongoDB | N/A | Admin team's insertions |

---

## Testing After Changes

1. **Rebuild:** `docker compose down; docker compose up -d --build`
2. **Test:** Use the curl/PowerShell test commands
3. **Verify:** Check backend logs: `docker logs codeplay-backend`
4. **Check Database:** Query MongoDB to see stored results

---

## No Changes Needed If...

✅ Admin adds new fields to MongoDB `coding_problems` - automatically included  
✅ Frontend just needs to display new fields - no backend change  
✅ Code Analyzer team processes new result fields - they query MongoDB directly  

Everything is modular and flexible! 🎯

