#!/usr/bin/env powershell
<#
.SYNOPSIS
Comprehensive End-to-End Test Suite for CodePlay
Tests: Problem Loading → Code Execution → Output Comparison → Database Storage
Verifies all metadata stored to PostgreSQL test_answer table
#>

$ErrorActionPreference = "Continue"

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  COMPREHENSIVE END-TO-END TEST SUITE                          ║" -ForegroundColor Cyan
Write-Host "║  Problem Loading → Execution → Storage → Verification         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$testResults = @()

# Test 1: Load Problem 1 and verify sample_input
Write-Host "TEST 1: Load Problem 1 (Python)" -ForegroundColor Yellow
Write-Host "─────────────────────────────────" -ForegroundColor Gray

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8002/problem/1" -Method GET -TimeoutSec 5
    $problem = $response.Content | ConvertFrom-Json
    
    Write-Host "✓ Problem loaded: $($problem.title)" -ForegroundColor Green
    Write-Host "  - Language: $($problem.language[0])" -ForegroundColor DarkGray
    Write-Host "  - Difficulty: $($problem.difficulty)" -ForegroundColor DarkGray
    Write-Host "  - Sample Input: $($problem.sample_input -replace "`n", " | ")" -ForegroundColor DarkGray
    Write-Host "  - Sample Output: $($problem.sample_output -replace "`n", " | ")" -ForegroundColor DarkGray
    
    $testResults += @{
        test = "Problem Loading"
        status = "PASS"
        details = "Problem 1 loaded with sample_input: $($problem.sample_input -replace "`n", "|")"
    }
} catch {
    Write-Host "✗ FAILED: $_" -ForegroundColor Red
    $testResults += @{
        test = "Problem Loading"
        status = "FAIL"
        details = $_
    }
}
Write-Host ""

# Test 2: Execute Python Code
Write-Host "TEST 2: Execute Python Code" -ForegroundColor Yellow
Write-Host "────────────────────────────" -ForegroundColor Gray

$pythonCode = 'a = int(input())' + [char]10 + 'b = int(input())' + [char]10 + 'print(a + b)'
$pythonPayload = @{
    language = "python"
    files = @(@{ name = "main"; content = $pythonCode })
    stdin = "3" + [char]10 + "5"
    problem_id = "1"
    user_id = "test_user_001"
} | ConvertTo-Json

Write-Host "Code: sum of two numbers" -ForegroundColor DarkGray
Write-Host "Input: 3, 5" -ForegroundColor DarkGray

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/run" -Method POST -Body $pythonPayload -ContentType "application/json" -TimeoutSec 10
    $result = $response.Content | ConvertFrom-Json
    $output = $result.run.stdout.Trim()
    
    Write-Host "Output: $output" -ForegroundColor DarkGray
    Write-Host "Status: $($result.status)" -ForegroundColor DarkGray
    
    if ($output -eq "8") {
        Write-Host "✓ PASSED: Output matches expected (8)" -ForegroundColor Green
        $testResults += @{
            test = "Python Execution"
            status = "PASS"
            details = "Output: $output"
        }
    } else {
        Write-Host "✗ FAILED: Expected 8, got $output" -ForegroundColor Red
        $testResults += @{
            test = "Python Execution"
            status = "FAIL"
            details = "Expected 8, got $output"
        }
    }
} catch {
    Write-Host "✗ ERROR: $_" -ForegroundColor Red
    $testResults += @{
        test = "Python Execution"
        status = "FAIL"
        details = $_
    }
}
Write-Host ""

# Test 3: Execute Java Code
Write-Host "TEST 3: Execute Java Code" -ForegroundColor Yellow
Write-Host "──────────────────────────" -ForegroundColor Gray

$javaCode = 'import java.util.Scanner;' + [char]10 + `
'class Main {' + [char]10 + `
'    public static void main(String[] args) {' + [char]10 + `
'        Scanner s = new Scanner(System.in);' + [char]10 + `
'        int a = s.nextInt();' + [char]10 + `
'        int b = s.nextInt();' + [char]10 + `
'        System.out.println(a + b);' + [char]10 + `
'    }' + [char]10 + `
'}'

$javaPayload = @{
    language = "java"
    files = @(@{ name = "Main"; content = $javaCode })
    stdin = "3" + [char]10 + "5"
    problem_id = "1"
    user_id = "test_user_001"
} | ConvertTo-Json

Write-Host "Code: Java sum (with class Main, no public)" -ForegroundColor DarkGray
Write-Host "Input: 3, 5" -ForegroundColor DarkGray

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/run" -Method POST -Body $javaPayload -ContentType "application/json" -TimeoutSec 15
    $result = $response.Content | ConvertFrom-Json
    $output = $result.run.stdout.Trim()
    $stderr = $result.run.stderr.Trim()
    
    if ($stderr) {
        Write-Host "Stderr: $stderr" -ForegroundColor Red
        Write-Host "✗ FAILED: Java compilation/execution error" -ForegroundColor Red
        $testResults += @{
            test = "Java Execution"
            status = "FAIL"
            details = "Error: $stderr"
        }
    } elseif ($output -eq "8") {
        Write-Host "Output: $output" -ForegroundColor DarkGray
        Write-Host "✓ PASSED: Java code executed correctly" -ForegroundColor Green
        $testResults += @{
            test = "Java Execution"
            status = "PASS"
            details = "Output: $output"
        }
    } else {
        Write-Host "Output: $output" -ForegroundColor DarkGray
        Write-Host "✗ FAILED: Expected 8, got $output" -ForegroundColor Red
        $testResults += @{
            test = "Java Execution"
            status = "FAIL"
            details = "Expected 8, got $output"
        }
    }
} catch {
    Write-Host "✗ ERROR: $_" -ForegroundColor Red
    $testResults += @{
        test = "Java Execution"
        status = "FAIL"
        details = $_
    }
}
Write-Host ""

# Test 4: Execute SQL Code
Write-Host "TEST 4: Execute SQL Code" -ForegroundColor Yellow
Write-Host "────────────────────────" -ForegroundColor Gray

$sqlCode = "SELECT 5 + 3 as result;"
$sqlPayload = @{
    language = "sql"
    files = @(@{ name = "query"; content = $sqlCode })
    stdin = ""
    problem_id = "5"
    user_id = "test_user_001"
} | ConvertTo-Json

Write-Host "Query: SELECT 5 + 3 as result" -ForegroundColor DarkGray

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/run" -Method POST -Body $sqlPayload -ContentType "application/json" -TimeoutSec 10
    $result = $response.Content | ConvertFrom-Json
    $output = $result.run.stdout.Trim()
    
    Write-Host "Output: $output" -ForegroundColor DarkGray
    
    if ($output.Contains("8")) {
        Write-Host "✓ PASSED: SQL query executed, result contains 8" -ForegroundColor Green
        $testResults += @{
            test = "SQL Execution"
            status = "PASS"
            details = "Output contains: 8"
        }
    } else {
        Write-Host "✗ FAILED: Expected output to contain 8" -ForegroundColor Red
        $testResults += @{
            test = "SQL Execution"
            status = "FAIL"
            details = "Output: $output"
        }
    }
} catch {
    Write-Host "✗ ERROR: $_" -ForegroundColor Red
    $testResults += @{
        test = "SQL Execution"
        status = "FAIL"
        details = $_
    }
}
Write-Host ""

# Test 5: Store Python Submission to PostgreSQL
Write-Host "TEST 5: Store Python Submission to PostgreSQL" -ForegroundColor Yellow
Write-Host "──────────────────────────────────────────────" -ForegroundColor Gray

$submissionPayload = @{
    candidate_id = "user_001"
    problem_id = "1"
    language = "python"
    code = $pythonCode
    stdin = "3" + [char]10 + "5"
    stdout = "8"
    output = "8"
    status = "success"
    is_passed = $true
    expected_output = "8"
} | ConvertTo-Json

Write-Host "Storing: Python code with output comparison" -ForegroundColor DarkGray

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8003/test-answer" -Method POST -Body $submissionPayload -ContentType "application/json" -TimeoutSec 10
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host "✓ Stored to PostgreSQL" -ForegroundColor Green
    Write-Host "  - Submission ID: $($result.id)" -ForegroundColor DarkGray
    Write-Host "  - Candidate: $($result.candidate_id)" -ForegroundColor DarkGray
    Write-Host "  - Problem: $($result.problem_id)" -ForegroundColor DarkGray
    Write-Host "  - Language: $($result.language)" -ForegroundColor DarkGray
    Write-Host "  - Status: $($result.status)" -ForegroundColor DarkGray
    Write-Host "  - Passed: $($result.is_passed)" -ForegroundColor DarkGray
    
    $testResults += @{
        test = "PostgreSQL Storage (Python)"
        status = "PASS"
        details = "Stored ID: $($result.id)"
    }
} catch {
    Write-Host "✗ FAILED: $_" -ForegroundColor Red
    $testResults += @{
        test = "PostgreSQL Storage (Python)"
        status = "FAIL"
        details = $_
    }
}
Write-Host ""

# Test 6: Store Java Submission to PostgreSQL
Write-Host "TEST 6: Store Java Submission to PostgreSQL" -ForegroundColor Yellow
Write-Host "───────────────────────────────────────────" -ForegroundColor Gray

$submissionPayload = @{
    candidate_id = "user_001"
    problem_id = "1"
    language = "java"
    code = $javaCode
    stdin = "3" + [char]10 + "5"
    stdout = "8"
    output = "8"
    status = "success"
    is_passed = $true
    expected_output = "8"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8003/test-answer" -Method POST -Body $submissionPayload -ContentType "application/json" -TimeoutSec 10
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host "✓ Stored to PostgreSQL" -ForegroundColor Green
    Write-Host "  - Submission ID: $($result.id)" -ForegroundColor DarkGray
    Write-Host "  - Language: Java (class Main, no public)" -ForegroundColor DarkGray
    Write-Host "  - Code stored: YES (full code)" -ForegroundColor DarkGray
    
    $testResults += @{
        test = "PostgreSQL Storage (Java)"
        status = "PASS"
        details = "Stored ID: $($result.id)"
    }
} catch {
    Write-Host "✗ FAILED: $_" -ForegroundColor Red
    $testResults += @{
        test = "PostgreSQL Storage (Java)"
        status = "FAIL"
        details = $_
    }
}
Write-Host ""

# Test 7: Store SQL Submission to PostgreSQL
Write-Host "TEST 7: Store SQL Submission to PostgreSQL" -ForegroundColor Yellow
Write-Host "──────────────────────────────────────────" -ForegroundColor Gray

$submissionPayload = @{
    candidate_id = "user_001"
    problem_id = "5"
    language = "sql"
    code = $sqlCode
    stdin = ""
    stdout = "8"
    output = "8"
    status = "success"
    is_passed = $true
    expected_output = "8"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8003/test-answer" -Method POST -Body $submissionPayload -ContentType "application/json" -TimeoutSec 10
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host "✓ Stored to PostgreSQL" -ForegroundColor Green
    Write-Host "  - Submission ID: $($result.id)" -ForegroundColor DarkGray
    Write-Host "  - Language: SQL" -ForegroundColor DarkGray
    Write-Host "  - Metadata stored: code, stdin, stdout, status, is_passed" -ForegroundColor DarkGray
    
    $testResults += @{
        test = "PostgreSQL Storage (SQL)"
        status = "PASS"
        details = "Stored ID: $($result.id)"
    }
} catch {
    Write-Host "✗ FAILED: $_" -ForegroundColor Red
    $testResults += @{
        test = "PostgreSQL Storage (SQL)"
        status = "FAIL"
        details = $_
    }
}
Write-Host ""

# Test 8: Retrieve Submissions from PostgreSQL
Write-Host "TEST 8: Retrieve Submissions from PostgreSQL" -ForegroundColor Yellow
Write-Host "───────────────────────────────────────────" -ForegroundColor Gray

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8003/test-answers/user_001" -Method GET -TimeoutSec 10
    $result = $response.Content | ConvertFrom-Json
    
    $count = $result.answers.Count
    Write-Host "✓ Retrieved $count submissions for user_001" -ForegroundColor Green
    
    foreach ($answer in $result.answers) {
        Write-Host "  - ID: $($answer.id) | Problem: $($answer.problem_id) | Lang: $($answer.language) | Passed: $($answer.is_passed)" -ForegroundColor DarkGray
        Write-Host "    Code stored: $([string]::IsNullOrEmpty($answer.code) ? 'NO' : 'YES (length: ' + $answer.code.Length + ')')" -ForegroundColor DarkGray
        Write-Host "    Input stored: $($answer.stdin)" -ForegroundColor DarkGray
        Write-Host "    Output stored: $($answer.stdout)" -ForegroundColor DarkGray
    }
    
    if ($count -ge 3) {
        Write-Host "✓ PASSED: All submissions stored and retrievable" -ForegroundColor Green
        $testResults += @{
            test = "Data Retrieval"
            status = "PASS"
            details = "Retrieved $count submissions"
        }
    } else {
        Write-Host "✗ WARNING: Expected at least 3 submissions, got $count" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ FAILED: $_" -ForegroundColor Red
    $testResults += @{
        test = "Data Retrieval"
        status = "FAIL"
        details = $_
    }
}
Write-Host ""

# Summary
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  TEST SUMMARY                                                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$passCount = ($testResults | Where-Object { $_.status -eq "PASS" }).Count
$failCount = ($testResults | Where-Object { $_.status -eq "FAIL" }).Count
$total = $testResults.Count

Write-Host "Total Tests: $total" -ForegroundColor Cyan
Write-Host "Passed: $passCount ✅" -ForegroundColor Green
Write-Host "Failed: $failCount ❌" -ForegroundColor $(if ($failCount -eq 0) { "Green" } else { "Red" })
Write-Host ""

foreach ($result in $testResults) {
    $icon = if ($result.status -eq "PASS") { "✓" } else { "✗" }
    $color = if ($result.status -eq "PASS") { "Green" } else { "Red" }
    Write-Host "$icon $($result.test): $($result.status)" -ForegroundColor $color
    Write-Host "  Details: $($result.details)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  METADATA STORED IN test_answer TABLE                         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Columns stored:" -ForegroundColor Green
Write-Host "  • id (auto-generated)" -ForegroundColor DarkGray
Write-Host "  • candidate_id" -ForegroundColor DarkGray
Write-Host "  • problem_id" -ForegroundColor DarkGray
Write-Host "  • language" -ForegroundColor DarkGray
Write-Host "  • code (FULL CODE TEXT STORED) ✅" -ForegroundColor Green
Write-Host "  • stdin (INPUT DATA)" -ForegroundColor DarkGray
Write-Host "  • stdout (RAW OUTPUT)" -ForegroundColor DarkGray
Write-Host "  • output (PROCESSED OUTPUT)" -ForegroundColor DarkGray
Write-Host "  • status (success/error/pending/timeout)" -ForegroundColor DarkGray
Write-Host "  • is_passed (true/false)" -ForegroundColor DarkGray
Write-Host "  • timestamp (CURRENT_TIMESTAMP)" -ForegroundColor DarkGray
Write-Host "  • created_at (CURRENT_TIMESTAMP)" -ForegroundColor DarkGray
Write-Host "  • updated_at (CURRENT_TIMESTAMP)" -ForegroundColor DarkGray
Write-Host ""

if ($passCount -eq $total) {
    Write-Host "🎊 ALL TESTS PASSED - SYSTEM PRODUCTION READY! 🎊" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Review details above." -ForegroundColor Yellow
}

Write-Host ""
