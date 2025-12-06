# Quick Testing Script for flexible_model
# Usage: ./test_quick.ps1 or powershell -ExecutionPolicy Bypass -File test_quick.ps1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Testing flexible_model - PowerShell" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "Test 1: Health Check" -ForegroundColor Green
Write-Host "Command: GET /health" -ForegroundColor Gray
$response = curl -X GET http://localhost:8000/health
Write-Host $response -ForegroundColor White
Write-Host "`n"

# Test 2: Problem Fetching
Write-Host "Test 2: Fetch Problem" -ForegroundColor Green
Write-Host "Command: GET /problem/1" -ForegroundColor Gray
$response = curl -X GET http://localhost:8000/problem/1
Write-Host $response -ForegroundColor White
Write-Host "`n"

# Test 3: Python Execution
Write-Host "Test 3: Python Execution (print(3+5))" -ForegroundColor Green
$payload = @{ 
    language = "python"
    files = @(@{ name = "main"; content = "print(3+5)" })
    stdin = "" 
} | ConvertTo-Json
Write-Host "Sending payload to POST /run" -ForegroundColor Gray
$response = curl -X POST http://localhost:8000/run -ContentType "application/json" -Body $payload
Write-Host $response -ForegroundColor White
Write-Host "`n"

# Test 4: Java Execution
Write-Host "Test 4: Java Execution (System.out.println(3+5))" -ForegroundColor Green
$payload = @{ 
    language = "java"
    files = @(@{ name = "Main"; content = "public class Main { public static void main(String[] args) { System.out.println(3+5); } }" })
    stdin = "" 
} | ConvertTo-Json
Write-Host "Sending payload to POST /run" -ForegroundColor Gray
$response = curl -X POST http://localhost:8000/run -ContentType "application/json" -Body $payload
Write-Host $response -ForegroundColor White
Write-Host "`n"

# Test 5: SQL Option 2 (Structured)
Write-Host "Test 5: SQL Option 2 - Structured Mode (SELECT from schema)" -ForegroundColor Green
$payload = @{ 
    language = "sql"
    files = @(@{ name = "query"; content = "SELECT a + b FROM numbers;" })
    stdin = ""
    problem_id = "1"
} | ConvertTo-Json
Write-Host "Sending payload to POST /run with problem_id=1" -ForegroundColor Gray
$response = curl -X POST http://localhost:8000/run -ContentType "application/json" -Body $payload
Write-Host $response -ForegroundColor White
Write-Host "`n"

# Test 6: SQL Option 2 - Blocked INSERT
Write-Host "Test 6: SQL Option 2 - Blocked INSERT" -ForegroundColor Green
$payload = @{ 
    language = "sql"
    files = @(@{ name = "query"; content = "INSERT INTO numbers VALUES (5, 10);" })
    stdin = ""
    problem_id = "1"
} | ConvertTo-Json
Write-Host "Sending payload to POST /run (should be blocked)" -ForegroundColor Gray
$response = curl -X POST http://localhost:8000/run -ContentType "application/json" -Body $payload
Write-Host $response -ForegroundColor White
Write-Host "`n"

# Test 7: SQL Option 1 - Flexible Mode
Write-Host "Test 7: SQL Option 1 - Flexible Mode (no problem_id)" -ForegroundColor Green
$payload = @{ 
    language = "sql"
    files = @(@{ name = "query"; content = "CREATE TABLE test (id INT, name TEXT); INSERT INTO test VALUES (1, 'Alice'), (2, 'Bob'); SELECT * FROM test;" })
    stdin = ""
} | ConvertTo-Json
Write-Host "Sending payload to POST /run (no problem_id, all SQL allowed)" -ForegroundColor Gray
$response = curl -X POST http://localhost:8000/run -ContentType "application/json" -Body $payload
Write-Host $response -ForegroundColor White
Write-Host "`n"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All tests completed!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
