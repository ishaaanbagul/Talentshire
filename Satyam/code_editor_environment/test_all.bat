@echo off
REM Testing batch script for flexible_model
REM Usage: Double-click or run: test_all.bat

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo Testing flexible_model - CMD Batch Script
echo ==========================================
echo.

echo ==========================================
echo Test 1: Health Check
echo ==========================================
echo Command: GET /health
curl -X GET http://localhost:8000/health
echo.
echo.

echo ==========================================
echo Test 2: Fetch Problem
echo ==========================================
echo Command: GET /problem/1
curl -X GET http://localhost:8000/problem/1
echo.
echo.

echo ==========================================
echo Test 3: Python Execution
echo ==========================================
echo Code: print(3+5)
echo Command: POST /run with Python payload
set payload={"language":"python","files":[{"name":"main","content":"print(3+5)"}],"stdin":""}
echo !payload! > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
echo.
echo.

echo ==========================================
echo Test 4: Java Execution
echo ==========================================
echo Code: System.out.println(3+5)
echo Command: POST /run with Java payload
set payload={"language":"java","files":[{"name":"Main","content":"public class Main { public static void main(String[] args) { System.out.println(3+5); } }"}],"stdin":""}
echo !payload! > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
echo.
echo.

echo ==========================================
echo Test 5: SQL Option 2 - Structured Mode
echo ==========================================
echo Query: SELECT a + b FROM numbers;
echo Mode: Structured (with problem_id=1)
echo Command: POST /run with SQL payload and problem_id
set payload={"language":"sql","files":[{"name":"query","content":"SELECT a + b FROM numbers;"}],"stdin":"","problem_id":"1"}
echo !payload! > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
echo.
echo.

echo ==========================================
echo Test 6: SQL Option 2 - Blocked INSERT
echo ==========================================
echo Query: INSERT INTO numbers VALUES (5, 10);
echo Mode: Structured (should be blocked)
echo Command: POST /run - INSERT should fail
set payload={"language":"sql","files":[{"name":"query","content":"INSERT INTO numbers VALUES (5, 10);"}],"stdin":"","problem_id":"1"}
echo !payload! > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
echo.
echo.

echo ==========================================
echo Test 7: SQL Option 1 - Flexible Mode
echo ==========================================
echo Query: CREATE and INSERT and SELECT
echo Mode: Flexible (no problem_id, all SQL allowed)
echo Command: POST /run without problem_id
set payload={"language":"sql","files":[{"name":"query","content":"CREATE TABLE test (id INT, name TEXT); INSERT INTO test VALUES (1, 'Alice'), (2, 'Bob'); SELECT * FROM test;"}],"stdin":""}
echo !payload! > payload.json
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @payload.json
del payload.json
echo.
echo.

echo ==========================================
echo All tests completed!
echo ==========================================
echo.
pause
