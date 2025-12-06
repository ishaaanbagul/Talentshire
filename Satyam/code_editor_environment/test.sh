#!/bin/bash

# Testing script for flexible_model - Bash/Linux/WSL version
# Usage: bash test.sh or ./test.sh (after chmod +x test.sh)

echo ""
echo "=========================================="
echo "Testing flexible_model - Bash Script"
echo "=========================================="
echo ""

echo "=========================================="
echo "Test 1: Health Check"
echo "=========================================="
echo "Command: GET /health"
curl -X GET http://localhost:8000/health
echo -e "\n\n"

echo "=========================================="
echo "Test 2: Fetch Problem"
echo "=========================================="
echo "Command: GET /problem/1"
curl -X GET http://localhost:8000/problem/1
echo -e "\n\n"

echo "=========================================="
echo "Test 3: Python Execution"
echo "=========================================="
echo "Code: print(3+5)"
echo "Command: POST /run with Python payload"
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"language":"python","files":[{"name":"main","content":"print(3+5)"}],"stdin":""}'
echo -e "\n\n"

echo "=========================================="
echo "Test 4: Java Execution"
echo "=========================================="
echo "Code: System.out.println(3+5)"
echo "Command: POST /run with Java payload"
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"language":"java","files":[{"name":"Main","content":"public class Main { public static void main(String[] args) { System.out.println(3+5); } }"}],"stdin":""}'
echo -e "\n\n"

echo "=========================================="
echo "Test 5: SQL Option 2 - Structured Mode"
echo "=========================================="
echo "Query: SELECT a + b FROM numbers;"
echo "Mode: Structured (with problem_id=1)"
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"language":"sql","files":[{"name":"query","content":"SELECT a + b FROM numbers;"}],"stdin":"","problem_id":"1"}'
echo -e "\n\n"

echo "=========================================="
echo "Test 6: SQL Option 2 - Blocked INSERT"
echo "=========================================="
echo "Query: INSERT INTO numbers VALUES (5, 10);"
echo "Mode: Structured (should be blocked)"
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"language":"sql","files":[{"name":"query","content":"INSERT INTO numbers VALUES (5, 10);"}],"stdin":"","problem_id":"1"}'
echo -e "\n\n"

echo "=========================================="
echo "Test 7: SQL Option 1 - Flexible Mode"
echo "=========================================="
echo "Query: CREATE and INSERT and SELECT"
echo "Mode: Flexible (no problem_id, all SQL allowed)"
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"language":"sql","files":[{"name":"query","content":"CREATE TABLE test (id INT, name TEXT); INSERT INTO test VALUES (1, '"'"'Alice'"'"'), (2, '"'"'Bob'"'"'); SELECT * FROM test;"}],"stdin":""}'
echo -e "\n\n"

echo "=========================================="
echo "All tests completed!"
echo "=========================================="
echo ""
