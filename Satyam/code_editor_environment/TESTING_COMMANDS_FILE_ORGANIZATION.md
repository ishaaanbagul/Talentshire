# Testing Commands - File Organization Guide

## Overview
This document shows you **WHICH COMMANDS GO IN WHICH FILES** for different testing scenarios.

---

## PART 1: QUICK REFERENCE - Commands by File Type

| Scenario | File Type | File Name | Commands From |
|----------|-----------|-----------|----------------|
| **Quick Manual Tests** | PowerShell Script | `test_quick.ps1` | TESTING_COMMANDS.md (PowerShell section) |
| **Automated Testing** | Batch Script | `test_all.bat` | TESTING_COMMANDS_CMD.md (Part 9) |
| **JSON File-Based** | .json files | `test_python.json`, `test_java.json`, etc. | Create separately (examples below) |
| **Documentation** | Markdown | `TESTING_COMMANDS.md` | Already created (reference only) |
| **CI/CD Pipeline** | Bash/Shell | `test.sh` | Convert from batch script |

---

## PART 2: FILE-BY-FILE BREAKDOWN

### 2.1 PowerShell Script - `test_quick.ps1`

**Location:** `C:\Users\MSI\new_project\test_quick.ps1`

**Purpose:** Quick testing on any Windows PC with PowerShell

**Content - Copy from TESTING_COMMANDS.md Part 7:**

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

**How to run:**
```powershell
# Option 1: Direct execution
powershell -ExecutionPolicy Bypass -File C:\Users\MSI\new_project\test_quick.ps1

# Option 2: From PowerShell
cd C:\Users\MSI\new_project
./test_quick.ps1
```

---

### 2.2 Batch Script - `test_all.bat`

**Location:** `C:\Users\MSI\new_project\test_all.bat`

**Purpose:** Testing on Windows CMD (Command Prompt)

**Content - Copy from TESTING_COMMANDS_CMD.md Part 9:**

```batch
@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo Test 1: Health Check
echo ========================================
curl -X GET http://localhost:8000/health
echo.

echo.
echo ========================================
echo Test 2: Fetch Problem
echo ========================================
curl -X GET http://localhost:8000/problem/1
echo.

echo.
echo ========================================
echo Test 3: Python Execution
echo ========================================
set payload={"language":"python","files":[{"name":"main","content":"print(3+5)"}],"stdin":""}
echo !payload! > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
echo.

echo.
echo ========================================
echo Test 4: Java Execution
echo ========================================
set payload={"language":"java","files":[{"name":"Main","content":"public class Main { public static void main(String[] args) { System.out.println(3+5); } }"}],"stdin":""}
echo !payload! > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
echo.

echo.
echo ========================================
echo Test 5: SQL Option 2 (Structured)
echo ========================================
set payload={"language":"sql","files":[{"name":"query","content":"SELECT a + b FROM numbers;"}],"stdin":"","problem_id":"1"}
echo !payload! > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
echo.

echo.
echo ========================================
echo Test 6: SQL Blocked INSERT
echo ========================================
set payload={"language":"sql","files":[{"name":"query","content":"INSERT INTO numbers VALUES (5, 10);"}],"stdin":"","problem_id":"1"}
echo !payload! > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
echo.

echo.
echo ========================================
echo Test 7: SQL Flexible Mode
echo ========================================
set payload={"language":"sql","files":[{"name":"query","content":"CREATE TABLE test (id INT); INSERT INTO test VALUES (1); SELECT * FROM test;"}],"stdin":""}
echo !payload! > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
echo.

echo.
echo ========================================
echo All tests completed!
echo ========================================
pause
```

**How to run:**
```cmd
REM Option 1: Double-click test_all.bat
REM Option 2: From Command Prompt
cd C:\Users\MSI\new_project
test_all.bat
```

---

### 2.3 JSON Test Files (Individual Tests)

**Create these separate JSON files for easy testing:**

#### File: `test_python.json`
**Location:** `C:\Users\MSI\new_project\test_python.json`

```json
{
  "language": "python",
  "files": [
    {
      "name": "main",
      "content": "print(3+5)"
    }
  ],
  "stdin": ""
}
```

**Test with:**
```cmd
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @test_python.json
```

---

#### File: `test_java.json`
**Location:** `C:\Users\MSI\new_project\test_java.json`

```json
{
  "language": "java",
  "files": [
    {
      "name": "Main",
      "content": "public class Main { public static void main(String[] args) { System.out.println(3+5); } }"
    }
  ],
  "stdin": ""
}
```

**Test with:**
```cmd
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @test_java.json
```

---

#### File: `test_sql_structured.json`
**Location:** `C:\Users\MSI\new_project\test_sql_structured.json`

```json
{
  "language": "sql",
  "files": [
    {
      "name": "query",
      "content": "SELECT a + b FROM numbers;"
    }
  ],
  "stdin": "",
  "problem_id": "1"
}
```

**Test with:**
```cmd
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @test_sql_structured.json
```

---

#### File: `test_sql_blocked.json`
**Location:** `C:\Users\MSI\new_project\test_sql_blocked.json`

```json
{
  "language": "sql",
  "files": [
    {
      "name": "query",
      "content": "INSERT INTO numbers VALUES (5, 10); SELECT * FROM numbers;"
    }
  ],
  "stdin": "",
  "problem_id": "1"
}
```

**Test with:**
```cmd
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @test_sql_blocked.json
```

---

#### File: `test_sql_flexible.json`
**Location:** `C:\Users\MSI\new_project\test_sql_flexible.json`

```json
{
  "language": "sql",
  "files": [
    {
      "name": "query",
      "content": "CREATE TABLE test (id INT, name TEXT); INSERT INTO test VALUES (1, 'Alice'), (2, 'Bob'); SELECT * FROM test;"
    }
  ],
  "stdin": ""
}
```

**Test with:**
```cmd
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @test_sql_flexible.json
```

---

#### File: `test_submission.json`
**Location:** `C:\Users\MSI\new_project\test_submission.json`

```json
{
  "user_id": "student123",
  "problem_id": "1",
  "language": "python",
  "code": "print(3+5)",
  "stdin": ""
}
```

**Test with:**
```cmd
curl -X POST http://localhost:8000/submission -H "Content-Type: application/json" -d @test_submission.json
```

---

### 2.4 Bash Script - `test.sh` (For Linux/WSL)

**Location:** `C:\Users\MSI\new_project\test.sh`

**Purpose:** Testing on WSL or Linux

**Content:**

```bash
#!/bin/bash

echo "=========================================="
echo "Test 1: Health Check"
echo "=========================================="
curl -X GET http://localhost:8000/health
echo -e "\n"

echo "=========================================="
echo "Test 2: Fetch Problem"
echo "=========================================="
curl -X GET http://localhost:8000/problem/1
echo -e "\n"

echo "=========================================="
echo "Test 3: Python Execution"
echo "=========================================="
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"language":"python","files":[{"name":"main","content":"print(3+5)"}],"stdin":""}'
echo -e "\n"

echo "=========================================="
echo "Test 4: Java Execution"
echo "=========================================="
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"language":"java","files":[{"name":"Main","content":"public class Main { public static void main(String[] args) { System.out.println(3+5); } }"}],"stdin":""}'
echo -e "\n"

echo "=========================================="
echo "Test 5: SQL Option 2"
echo "=========================================="
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"language":"sql","files":[{"name":"query","content":"SELECT a + b FROM numbers;"}],"stdin":"","problem_id":"1"}'
echo -e "\n"

echo "=========================================="
echo "All tests completed!"
echo "=========================================="
```

**How to run:**
```bash
chmod +x test.sh
./test.sh
```

---

## PART 3: DIRECTORY STRUCTURE AFTER ADDING TEST FILES

```
new_project/
├── backend/
├── frontend/
├── docker-compose.yml
├── CUSTOMIZATION_GUIDE.md
├── TESTING_COMMANDS.md
├── TESTING_COMMANDS_CMD.md
├── TESTING_COMMANDS_FILE_ORGANIZATION.md (← This file)
├── test_quick.ps1                        (← PowerShell script)
├── test_all.bat                          (← Batch script)
├── test.sh                               (← Bash script)
├── test_python.json                      (← JSON files)
├── test_java.json
├── test_sql_structured.json
├── test_sql_blocked.json
├── test_sql_flexible.json
└── test_submission.json
```

---

## PART 4: WHICH FILE TO USE - DECISION TREE

```
Are you on Windows?
├─ YES
│  ├─ Do you prefer PowerShell?
│  │  ├─ YES → Use test_quick.ps1
│  │  └─ NO  → Use test_all.bat
│  └─ Want to test one endpoint at a time?
│     ├─ YES → Use individual test_*.json files
│     └─ NO  → Use batch script
│
└─ NO (Linux/Mac/WSL)
   └─ Use test.sh
```

---

## PART 5: USAGE EXAMPLES

### Scenario 1: Quick Test on Windows (PowerShell)

```powershell
# Navigate to project
cd C:\Users\MSI\new_project

# Run all tests
./test_quick.ps1
```

**Result:** All 5 tests run sequentially, shows output as it goes

---

### Scenario 2: Test Individual Python Endpoint (CMD)

```cmd
# Navigate to project
cd C:\Users\MSI\new_project

# Test Python only
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @test_python.json
```

**Result:** Runs one test, can repeat with different JSON files

---

### Scenario 3: Full Testing Suite (CMD)

```cmd
# Double-click or run
C:\Users\MSI\new_project\test_all.bat
```

**Result:** All tests run with pretty formatting, press any key at end

---

### Scenario 4: Integrate with CI/CD (Linux)

```bash
# In your CI/CD pipeline (GitHub Actions, GitLab, etc.)
cd new_project
bash test.sh > test_results.log
```

**Result:** Tests run, output saved to file

---

## PART 6: STEP-BY-STEP SETUP

### For Your Office PC Tomorrow:

1. **Unzip file:**
   ```cmd
   unzip flexible_model.zip
   cd new_project
   ```

2. **Start Docker:**
   ```cmd
   docker compose up -d --build
   ```

3. **Choose test method:**

   **Option A - PowerShell (Easiest):**
   ```powershell
   powershell -ExecutionPolicy Bypass -File test_quick.ps1
   ```

   **Option B - CMD (Most Compatible):**
   ```cmd
   test_all.bat
   ```

   **Option C - Individual Tests (Most Control):**
   ```cmd
   curl -X GET http://localhost:8000/health
   curl -X POST http://localhost:8000/run -d @test_python.json
   curl -X POST http://localhost:8000/run -d @test_java.json
   ```

4. **View results:**
   - If all green ✅ → Everything works!
   - If any fails → Check `docker logs codeplay-backend`

---

## PART 7: CONTENT MAPPING

| File | Contains Commands From | Purpose |
|------|----------------------|---------|
| `test_quick.ps1` | TESTING_COMMANDS.md Part 7 | PowerShell batch testing |
| `test_all.bat` | TESTING_COMMANDS_CMD.md Part 9 | CMD batch testing |
| `test_*.json` | Individual JSON payloads | Single test files |
| `test.sh` | Bash version of batch scripts | Linux/WSL testing |
| `TESTING_COMMANDS.md` | Complete reference | PowerShell command details |
| `TESTING_COMMANDS_CMD.md` | Complete reference | CMD command details |

---

## PART 8: COPY-PASTE CHEAT SHEET

**Quick copy-paste for your office PC:**

```cmd
REM Test 1: Health
curl http://localhost:8000/health

REM Test 2: Problem
curl http://localhost:8000/problem/1

REM Test 3: Python (from JSON file)
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @test_python.json

REM Test 4: Java (from JSON file)
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @test_java.json

REM Test 5: SQL (from JSON file)
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @test_sql_structured.json
```

---

## Summary

**Files in ZIP:**
- ✅ `test_quick.ps1` - For PowerShell users
- ✅ `test_all.bat` - For CMD users
- ✅ `test_*.json` - For individual testing
- ✅ `test.sh` - For Linux/WSL users
- ✅ `TESTING_COMMANDS.md` - Full documentation (PowerShell)
- ✅ `TESTING_COMMANDS_CMD.md` - Full documentation (CMD)
- ✅ `CUSTOMIZATION_GUIDE.md` - How to customize

**On your office PC:**
- Just run `test_all.bat` or `./test_quick.ps1`
- Or test individually with JSON files
- All commands already written and ready to use!

