# 🔌 Integration Guide for Your Team

## Quick Start for Integration

### Step 1: Update PostgreSQL Credentials
Edit `docker-compose.yml`:
```yaml
environment:
  POSTGRES_HOST: your-database-host
  POSTGRES_PORT: 5432
  POSTGRES_USER: your-username
  POSTGRES_PASSWORD: your-password
  POSTGRES_DB: your-database-name
```

### Step 2: Create Database Table
Run this SQL on your PostgreSQL database:
```sql
CREATE TABLE IF NOT EXISTS test_answer (
    id SERIAL PRIMARY KEY,
    candidate_id VARCHAR(100),
    problem_id VARCHAR(100),
    language VARCHAR(50),
    code TEXT,
    stdin TEXT,
    stdout TEXT,
    output TEXT,
    status VARCHAR(50),
    is_passed BOOLEAN,
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_candidate ON test_answer(candidate_id);
CREATE INDEX idx_problem ON test_answer(problem_id);
CREATE INDEX idx_status ON test_answer(status);
```

### Step 3: Start the System
```bash
docker-compose up -d
```

### Step 4: Test Integration
```bash
# Test all languages
powershell -ExecutionPolicy Bypass -File test_java_api.ps1
powershell -ExecutionPolicy Bypass -File test_python_api.ps1
powershell -ExecutionPolicy Bypass -File test_sql_api.ps1
powershell -ExecutionPolicy Bypass -File test_pyspark_api.ps1
```

---

## API Endpoints for Integration

### 1. Execute Code
```
POST http://your-server:8001/run
Content-Type: application/json

{
  "language": "python",
  "files": [{"name": "main", "content": "print(5+3)"}],
  "stdin": "",
  "problem_id": "1",
  "user_id": "user_123"
}

Response:
{
  "status": "success",
  "run": {
    "stdout": "8",
    "stderr": "",
    "output": "8"
  }
}
```

### 2. Get Problem
```
GET http://your-server:8002/problem/1

Response:
{
  "problem_id": "1",
  "title": "Sum Two Numbers",
  "description": "...",
  "sample_input": "3\n5",
  "expected_output": "8"
}
```

### 3. Save Test Answer
```
POST http://your-server:8003/test-answer
Content-Type: application/json

{
  "candidate_id": "user_123",
  "problem_id": "1",
  "language": "python",
  "code": "print(5+3)",
  "stdin": "",
  "stdout": "8",
  "output": "8",
  "status": "success",
  "is_passed": true,
  "expected_output": "8"
}

Response:
{
  "id": 1,
  "candidate_id": "user_123",
  "problem_id": "1",
  "status": "success",
  "is_passed": true,
  "timestamp": "2025-12-09T04:00:00"
}
```

### 4. Retrieve Test Results
```
GET http://your-server:8003/test-answers/user_123

Response:
{
  "candidate_id": "user_123",
  "count": 5,
  "test_answers": [
    {
      "id": 1,
      "problem_id": "1",
      "language": "python",
      "code": "...",
      "stdout": "8",
      "output": "8",
      "is_passed": true,
      "timestamp": "2025-12-09T04:00:00"
    },
    ...
  ]
}
```

### 5. Auto-Save Draft
```
POST http://your-server:8003/draft
{
  "candidate_id": "user_123",
  "problem_id": "1",
  "language": "python",
  "code": "x = 5\ny = 3\nprint(x+y)",
  "cursor_position": 20,
  "status": "draft"
}
```

---

## Supported Languages

| Language | Status | Tested | Example |
|----------|--------|--------|---------|
| Python | ✅ | Yes | `print(5+3)` → 8 |
| Java | ✅ | Yes | `class Main { ... }` → 8 |
| SQL | ✅ | Yes | `SELECT 5+3` → 8 |
| PySpark | ✅ | Yes | `sum([1,2,3,4,5])` → 15 |

---

## Data Flow for Test Submission

```
User Interface
      ↓
1. Execute Code (Execution Service)
      ↓
2. Get Raw Output (stdout)
      ↓
3. Compare with Expected Output
      ↓
4. Save Result to PostgreSQL
      ├─ candidate_id
      ├─ problem_id
      ├─ code (FULL TEXT)
      ├─ stdin
      ├─ stdout (raw output)
      ├─ output (processed)
      ├─ status (success/error)
      └─ is_passed (boolean)
      ↓
5. Return Result to User
```

---

## Key Features

### ✅ Full Code Storage
- Entire source code stored in `code` column
- Not truncated
- Useful for code review

### ✅ Dual Output Storage
- `stdout`: Raw program output (with newlines)
- `output`: Processed/trimmed output (for comparison)

### ✅ Auto-Save
- Drafts saved every 5 seconds
- Recovered automatically on page reload
- Cleared after successful submission

### ✅ Test Validation
- Automatic comparison with expected output
- Visual pass/fail indicators
- Detailed comparison messages

### ✅ Multi-Language
- Python, Java, SQL, PySpark
- Each handles input/output differently
- Tested and working

---

## Monitoring & Debugging

### Check System Health
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f execution-service
docker-compose logs -f submission-service
docker-compose logs -f problem-service
```

### Query Database
```sql
-- All test results
SELECT * FROM test_answer ORDER BY timestamp DESC LIMIT 10;

-- Results for specific user
SELECT * FROM test_answer WHERE candidate_id = 'user_123';

-- Passed test cases
SELECT * FROM test_answer WHERE is_passed = true;

-- Failed test cases
SELECT * FROM test_answer WHERE is_passed = false;
```

---

## Common Issues & Solutions

### Issue: Database Connection Fails
```
Solution: Update POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD in docker-compose.yml
```

### Issue: Execution Timeout
```
Solution: Increase timeout in execution_service/main.py
Current: 10 seconds
Modify: Execution timeout in run() function
```

### Issue: Cache Problems
```
Solution: Full cleanup and rebuild
docker-compose down -v
docker system prune -af
docker-compose up -d --build
```

### Issue: Port Already in Use
```
Solution: Change ports in docker-compose.yml
Current:
  - 5173 → 80 (frontend)
  - 8001 → 8001 (execution)
  - 8002 → 8002 (problem)
  - 8003 → 8003 (submission)
```

---

## Team Handoff Checklist

- [ ] Update PostgreSQL credentials
- [ ] Create test_answer table in your database
- [ ] Update docker-compose.yml with your config
- [ ] Run `docker-compose up -d`
- [ ] Test with all 4 languages
- [ ] Verify data is stored in your PostgreSQL
- [ ] Set up monitoring/logging
- [ ] Configure backups
- [ ] Update API documentation in your team wiki
- [ ] Train team on new endpoints

---

**Ready for production integration!** ✅
