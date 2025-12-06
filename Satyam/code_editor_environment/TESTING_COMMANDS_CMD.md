# Testing Commands - CMD (Command Prompt) Version

## Overview
All testing commands converted to work with Windows CMD (Command Prompt), not PowerShell.

---

## PART 1: SETUP & INFRASTRUCTURE COMMANDS

### 1.1 Build and Start Docker Services

```cmd
docker compose up -d --build
```

**Same on both CMD and PowerShell** ✅

---

### 1.2 Check Running Containers

```cmd
docker ps
```

**Same on both** ✅

---

### 1.3 View Backend Logs

```cmd
docker logs codeplay-backend
```

**Same on both** ✅

---

### 1.4 View Frontend Logs

```cmd
docker logs codeplay-frontend
```

**Same on both** ✅

---

### 1.5 Stop All Services

```cmd
docker compose down
```

**Same on both** ✅

---

### 1.6 Full Rebuild

```cmd
docker compose down && docker compose up -d --build
```

**Key difference:**
- PowerShell uses `;` 
- CMD uses `&&` ✅

---

## PART 2: HEALTH CHECK & BASIC CONNECTIVITY

### 2.1 Check Backend Health Endpoint (CMD)

```cmd
curl -X GET http://localhost:8000/health
```

**Result:**
```json
{"status":"healthy","mongodb_mode":"mock","code_execution_type":"direct_subprocess"}
```

**Works on both CMD and PowerShell** ✅

---

### 2.2 Check Frontend is Running (CMD)

```cmd
curl -X GET http://localhost:3000
```

**Same on both** ✅

---

## PART 3: PROBLEM FETCHING TESTS

### 3.1 Fetch Problem (CMD)

```cmd
curl -X GET http://localhost:8000/problem/1
```

**Result:**
```json
{
  "id": "1",
  "title": "Sum Two Numbers",
  "constraints": "1 <= a, b <= 1000",
  "sql_schema": "CREATE TABLE numbers (a INT, b INT);",
  "sql_test_data": "INSERT INTO numbers VALUES (3, 5), (0, 0), (1000000000, 1000000000);",
  "sql_expected_output": "8\n0\n2000000000"
}
```

**Same on both** ✅

---

## PART 4: PYTHON CODE EXECUTION (CMD Format)

### 4.1 Simple Python Calculation

**CMD - Create payload in temporary file:**

```cmd
@echo off
set payload={"language":"python","version":"latest","files":[{"name":"main","content":"print(3+5)"}],"stdin":""}
echo %payload% > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
```

**Explanation:**
- Create JSON payload in file (no native JSON support in CMD)
- Send with curl using `@` to read file
- Delete temp file after

**Alternative - Single line (if no spaces in code):**

```cmd
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d "{\"language\":\"python\",\"files\":[{\"name\":\"main\",\"content\":\"print(3+5)\"}],\"stdin\":\"\"}"
```

**Expected Response:**
```json
{"run":{"stdout":"8\n","stderr":"","output":"8\n","code":0}}
```

---

### 4.2 Python with Input (stdin)

**CMD Script:**

```cmd
@echo off
set payload={"language":"python","files":[{"name":"main","content":"a = input(); print(int(a) * 2)"}],"stdin":"5"}
echo %payload% > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
```

**Expected Output:** `10\n`

---

### 4.3 Python with Error

```cmd
@echo off
set payload={"language":"python","files":[{"name":"main","content":"print(1/0)"}],"stdin":""}
echo %payload% > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
```

**Expected:** Error in stderr, code 1

---

### 4.4 Python with Problem ID

```cmd
@echo off
set payload={"language":"python","files":[{"name":"main","content":"print(3+5)"}],"stdin":"","problem_id":"1"}
echo %payload% > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
```

---

## PART 5: JAVA CODE EXECUTION (CMD Format)

### 5.1 Simple Java Program

```cmd
@echo off
set payload={"language":"java","files":[{"name":"Main","content":"public class Main { public static void main(String[] args) { System.out.println(3+5); } }"}],"stdin":""}
echo %payload% > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
```

**Expected:** `8\n`

---

### 5.2 Java with Compilation Error

```cmd
@echo off
set payload={"language":"java","files":[{"name":"Main","content":"public class Main { public static void main(String[] args) { System.out.println(3+5) } }"}],"stdin":""}
echo %payload% > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
```

**Expected:** Compilation error in stderr

---

### 5.3 Java with Input

```cmd
@echo off
set payload={"language":"java","files":[{"name":"Main","content":"import java.util.Scanner; public class Main { public static void main(String[] args) { Scanner s = new Scanner(System.in); int x = s.nextInt(); System.out.println(x*2); } }"}],"stdin":"5"}
echo %payload% > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
```

**Expected:** `10\n`

---

## PART 6: SQL CODE EXECUTION (CMD Format)

### 6.1 SQL Option 2 - SELECT Query

```cmd
@echo off
set payload={"language":"sql","files":[{"name":"query","content":"SELECT a + b FROM numbers;"}],"stdin":"","problem_id":"1"}
echo %payload% > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
```

**Expected:** Output with results

---

### 6.2 SQL Option 2 - Blocked INSERT

```cmd
@echo off
set payload={"language":"sql","files":[{"name":"query","content":"INSERT INTO numbers VALUES (5, 10); SELECT * FROM numbers;"}],"stdin":"","problem_id":"1"}
echo %payload% > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
```

**Expected:** Error - "Only SELECT queries allowed"

---

### 6.3 SQL Option 1 - Flexible Mode

```cmd
@echo off
set payload={"language":"sql","files":[{"name":"query","content":"CREATE TABLE test (id INT, name TEXT); INSERT INTO test VALUES (1, 'Alice'), (2, 'Bob'); SELECT * FROM test;"}],"stdin":""}
echo %payload% > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
```

**Expected:** Success with results

---

## PART 7: SUBMISSION TESTS (CMD Format)

### 7.1 Submit Code Execution

```cmd
@echo off
set payload={"user_id":"student123","problem_id":"1","language":"python","code":"print(3+5)","stdin":""}
echo %payload% > payload.json
curl -X POST http://localhost:8000/submission -H "Content-Type: application/json" -d @payload.json
del payload.json
```

---

### 7.2 Retrieve User Submissions

```cmd
curl -X GET http://localhost:8000/submissions/student123
```

---

## PART 8: TIMEOUT & ERROR HANDLING (CMD Format)

### 8.1 Python Infinite Loop (Timeout Test)

```cmd
@echo off
set payload={"language":"python","files":[{"name":"main","content":"while True: pass"}],"stdin":""}
echo %payload% > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
```

**Expected:** Timeout error after 10 seconds

---

### 8.2 Java Infinite Loop

```cmd
@echo off
set payload={"language":"java","files":[{"name":"Main","content":"public class Main { public static void main(String[] args) { while(true) {} } }"}],"stdin":""}
echo %payload% > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
```

---

## PART 9: BATCH TESTING SCRIPT FOR CMD

**Save as `test_all.bat`:**

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

**Run with:**
```cmd
test_all.bat
```

---

## PART 10: KEY DIFFERENCES - CMD vs PowerShell

| Feature | CMD | PowerShell |
|---------|-----|-----------|
| **Command Separator** | `&&` | `;` |
| **Variables** | `%var%` | `$var` |
| **Delayed Expansion** | `!var!` (need `setlocal enabledelayedexpansion`) | `$var` |
| **JSON File Input** | `@filename` | `ConvertTo-Json` |
| **Multi-line Commands** | Use `^` for continuation | Use backtick `` ` `` |
| **Loops** | `for` loop | `foreach` loop |
| **If Statements** | `if` | `if` |
| **Echo** | `echo` | `Write-Host` |

---

## PART 11: TROUBLESHOOTING CMD ISSUES

### Issue: Special Characters in JSON

**Problem:** JSON contains quotes, colons, etc. - CMD treats them specially

**Solution:** Escape with backslash or use file method

```cmd
REM Method 1: Use file (recommended)
echo {"code":"print(3+5)"} > payload.json
curl -X POST http://localhost:8000/run -d @payload.json

REM Method 2: Escape quotes
curl -X POST http://localhost:8000/run -d "{\"code\":\"print(3+5)\"}"
```

---

### Issue: Path Too Long

**Problem:** CMD has 260 character limit for paths

**Solution:** Use shorter paths or enable long path support

```cmd
REM Enable long paths (Windows 10+)
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1
```

---

### Issue: Curl Not Found

**Problem:** curl command not recognized

**Solution:** Install curl or use full path

```cmd
REM Check if curl is installed
where curl

REM If not installed, download from: https://curl.se/download.html
REM Or use WSL if available
wsl curl -X GET http://localhost:8000/health
```

---

## PART 12: SIMPLER CMD APPROACH (Using Text Files)

If you find JSON escaping too complicated, create separate JSON files:

**Create `test_python.json`:**
```json
{
  "language": "python",
  "files": [{"name": "main", "content": "print(3+5)"}],
  "stdin": ""
}
```

**Then test with CMD:**
```cmd
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @test_python.json
```

**Much simpler!** ✅

---

## PART 13: QUICK CMD TESTING CHECKLIST

```cmd
REM Copy-paste these one at a time

REM 1. Health check
curl -X GET http://localhost:8000/health

REM 2. Problem fetch
curl -X GET http://localhost:8000/problem/1

REM 3. Python test
set p={"language":"python","files":[{"name":"main","content":"print(3+5)"}],"stdin":""}
echo %p% > p.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @p.json
del p.json

REM 4. Java test
set p={"language":"java","files":[{"name":"Main","content":"public class Main { public static void main(String[] args) { System.out.println(3+5); } }"}],"stdin":""}
echo %p% > p.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @p.json
del p.json

REM 5. SQL test
set p={"language":"sql","files":[{"name":"query","content":"SELECT a + b FROM numbers;"}],"stdin":"","problem_id":"1"}
echo %p% > p.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @p.json
del p.json
```

---

## PART 14: RECOMMENDATIONS

**For Windows CMD Users:**

1. **Use JSON files method** - Simpler and less error-prone
   ```cmd
   echo {"language":"python","files":[{"name":"main","content":"print(3+5)"}],"stdin":""} > test.json
   curl -X POST http://localhost:8000/run -d @test.json
   ```

2. **Use the batch script** - Run `test_all.bat` for all tests at once

3. **Consider PowerShell** - Better for complex testing with native JSON support

4. **Use WSL** - If installed, can use Linux bash commands
   ```cmd
   wsl bash -c 'curl -X GET http://localhost:8000/health'
   ```

---

## Summary

**CMD Commands:**
- ✅ **Docker commands** - Same as PowerShell
- ✅ **curl GET requests** - Same as PowerShell
- ✅ **curl POST with files** - Recommended method
- ⚠️ **curl POST with inline JSON** - Possible but complex escaping

**Best Practice:**
Use JSON files instead of inline JSON - much simpler and less error-prone!

