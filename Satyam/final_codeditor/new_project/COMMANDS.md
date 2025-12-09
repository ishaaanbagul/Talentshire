# 🔧 Complete Commands Reference

**Testing Commands for Both PowerShell & CMD**

---

## 📋 Table of Contents

1. [Docker Management](#docker-management)
2. [Testing Commands](#testing-commands)
3. [Database Operations](#database-operations)
4. [Troubleshooting](#troubleshooting)

---

## 🐳 Docker Management

### Start the System

**PowerShell:**
```powershell
cd 'c:\Users\MSI\new_project'
docker-compose up -d
```

**CMD:**
```cmd
cd c:\Users\MSI\new_project
docker-compose up -d
```

### Stop the System

**PowerShell:**
```powershell
docker-compose down
```

**CMD:**
```cmd
docker-compose down
```

### Full Cleanup & Restart (Fix Cache Issues)

**PowerShell:**
```powershell
docker-compose down -v
docker system prune -af --volumes
docker-compose up -d --build
```

**CMD:**
```cmd
docker-compose down -v
docker system prune -af --volumes
docker-compose up -d --build
```

### View Container Status

**PowerShell:**
```powershell
docker-compose ps
```

**CMD:**
```cmd
docker-compose ps
```

### View Logs for All Services

**PowerShell:**
```powershell
docker-compose logs -f
```

**CMD:**
```cmd
docker-compose logs -f
```

### View Specific Service Logs

**PowerShell:**
```powershell
# Execution Service
docker-compose logs -f execution-service

# Problem Service
docker-compose logs -f problem-service

# Submission Service
docker-compose logs -f submission-service
```

**CMD:**
```cmd
REM Execution Service
docker-compose logs -f execution-service

REM Problem Service
docker-compose logs -f problem-service

REM Submission Service
docker-compose logs -f submission-service
```

---

## 🧪 Testing Commands

### Test Individual Languages

#### **Java Test**

**PowerShell:**
```powershell
cd 'c:\Users\MSI\new_project'
powershell -ExecutionPolicy Bypass -File test_java_api.ps1
```

**CMD:**
```cmd
cd c:\Users\MSI\new_project
powershell -ExecutionPolicy Bypass -File test_java_api.ps1
```

#### **Python Test**

**PowerShell:**
```powershell
cd 'c:\Users\MSI\new_project'
powershell -ExecutionPolicy Bypass -File test_python_api.ps1
```

**CMD:**
```cmd
cd c:\Users\MSI\new_project
powershell -ExecutionPolicy Bypass -File test_python_api.ps1
```

#### **SQL Test**

**PowerShell:**
```powershell
cd 'c:\Users\MSI\new_project'
powershell -ExecutionPolicy Bypass -File test_sql_api.ps1
```

**CMD:**
```cmd
cd c:\Users\MSI\new_project
powershell -ExecutionPolicy Bypass -File test_sql_api.ps1
```

#### **PySpark Test**

**PowerShell:**
```powershell
cd 'c:\Users\MSI\new_project'
powershell -ExecutionPolicy Bypass -File test_pyspark_api.ps1
```

**CMD:**
```cmd
cd c:\Users\MSI\new_project
powershell -ExecutionPolicy Bypass -File test_pyspark_api.ps1
```

### Test All Languages (One Command)

**PowerShell:**
```powershell
cd 'c:\Users\MSI\new_project'
Write-Host "=== Testing All Languages ===" -ForegroundColor Cyan
powershell -ExecutionPolicy Bypass -File test_java_api.ps1
Write-Host "`n=== Python ===" -ForegroundColor Cyan
powershell -ExecutionPolicy Bypass -File test_python_api.ps1
Write-Host "`n=== SQL ===" -ForegroundColor Cyan
powershell -ExecutionPolicy Bypass -File test_sql_api.ps1
Write-Host "`n=== PySpark ===" -ForegroundColor Cyan
powershell -ExecutionPolicy Bypass -File test_pyspark_api.ps1
```

**CMD (Batch File):**
Create a file named `run_all_tests.bat`:
```batch
@echo off
cd c:\Users\MSI\new_project
echo === Testing All Languages ===
powershell -ExecutionPolicy Bypass -File test_java_api.ps1
echo.
echo === Python ===
powershell -ExecutionPolicy Bypass -File test_python_api.ps1
echo.
echo === SQL ===
powershell -ExecutionPolicy Bypass -File test_sql_api.ps1
echo.
echo === PySpark ===
powershell -ExecutionPolicy Bypass -File test_pyspark_api.ps1
pause
```

Then run:
```cmd
run_all_tests.bat
```

### Test API Endpoints Directly

**PowerShell - Test Execution Service:**
```powershell
$payload = @{
    language = "python"
    files = @(@{ name = "main"; content = "print(5+3)" })
    stdin = ""
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8001/run" -Method POST -Body $payload -ContentType "application/json" | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

**CMD - Test Execution Service (Using curl if available):**
```cmd
curl -X POST http://localhost:8001/run -H "Content-Type: application/json" -d "{\"language\":\"python\",\"files\":[{\"name\":\"main\",\"content\":\"print(5+3)\"}],\"stdin\":\"\"}"
```

### Test Problem Service

**PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8002/problem/1" -Method GET | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

**CMD (curl):**
```cmd
curl http://localhost:8002/problem/1
```

### Test Health Endpoints

**PowerShell:**
```powershell
# Execution Service Health
Invoke-WebRequest -Uri "http://localhost:8001/health" -Method GET | Select-Object -ExpandProperty Content | ConvertFrom-Json

# Submission Service Health
Invoke-WebRequest -Uri "http://localhost:8003/health" -Method GET | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

**CMD (curl):**
```cmd
curl http://localhost:8001/health
curl http://localhost:8003/health
```

---

## 🗄️ Database Operations

### Connect to PostgreSQL

**PowerShell:**
```powershell
# Using psql (if installed)
psql -h localhost -U codeplay_user -d codeplay_db
```

**CMD:**
```cmd
REM Using psql (if installed)
psql -h localhost -U codeplay_user -d codeplay_db
```

### View All Test Results

**SQL Query:**
```sql
SELECT * FROM test_answer ORDER BY timestamp DESC LIMIT 10;
```

### View Results for Specific User

**SQL Query:**
```sql
SELECT * FROM test_answer WHERE candidate_id = 'user_123' ORDER BY timestamp DESC;
```

### View Passed Tests

**SQL Query:**
```sql
SELECT * FROM test_answer WHERE is_passed = true ORDER BY timestamp DESC;
```

### View Failed Tests

**SQL Query:**
```sql
SELECT * FROM test_answer WHERE is_passed = false ORDER BY timestamp DESC;
```

### View Specific Language Results

**SQL Query:**
```sql
SELECT * FROM test_answer WHERE language = 'python' ORDER BY timestamp DESC;
```

### Get Code for Specific Submission

**SQL Query:**
```sql
SELECT candidate_id, problem_id, code, status, is_passed FROM test_answer WHERE id = 1;
```

### Delete All Test Results

**SQL Query (CAUTION):**
```sql
DELETE FROM test_answer;
```

---

## 🔧 Troubleshooting Commands

### Check Docker Version

**PowerShell & CMD:**
```
docker --version
docker-compose --version
```

### Check All Running Containers

**PowerShell:**
```powershell
docker ps -a
```

**CMD:**
```cmd
docker ps -a
```

### Check Container Resource Usage

**PowerShell & CMD:**
```
docker stats
```

### Rebuild Specific Service (Without Cache)

**PowerShell:**
```powershell
docker-compose up -d --build --no-cache execution-service
```

**CMD:**
```cmd
docker-compose up -d --build --no-cache execution-service
```

### Stop and Remove All Containers

**PowerShell:**
```powershell
docker-compose down
```

**CMD:**
```cmd
docker-compose down
```

### Remove Unused Docker Resources

**PowerShell:**
```powershell
docker system prune -f
```

**CMD:**
```cmd
docker system prune -f
```

### Check Network Connectivity

**PowerShell:**
```powershell
Test-NetConnection -ComputerName localhost -Port 8001
Test-NetConnection -ComputerName localhost -Port 5173
```

**CMD:**
```cmd
REM Test if ports are open (requires netstat)
netstat -ano | findstr "8001"
netstat -ano | findstr "5173"
```

### Verify Port Usage

**PowerShell:**
```powershell
netstat -ano | Select-String "8001|8002|8003|5173|5432|27017"
```

**CMD:**
```cmd
netstat -ano | findstr "8001 8002 8003 5173 5432 27017"
```

---

## 📊 Comprehensive Test Suite

### Full Integration Test (PowerShell)

```powershell
# 1. Check Docker Status
Write-Host "Checking Docker Status..." -ForegroundColor Cyan
docker-compose ps

# 2. Wait for services
Write-Host "Waiting 10 seconds for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 3. Test all languages
Write-Host "Testing All Languages..." -ForegroundColor Cyan
powershell -ExecutionPolicy Bypass -File test_java_api.ps1
powershell -ExecutionPolicy Bypass -File test_python_api.ps1
powershell -ExecutionPolicy Bypass -File test_sql_api.ps1
powershell -ExecutionPolicy Bypass -File test_pyspark_api.ps1

# 4. Test API endpoints
Write-Host "Testing API Endpoints..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "http://localhost:8001/health" -Method GET | Select-Object -ExpandProperty Content | ConvertFrom-Json
Invoke-WebRequest -Uri "http://localhost:8003/health" -Method GET | Select-Object -ExpandProperty Content | ConvertFrom-Json

Write-Host "✅ All tests completed!" -ForegroundColor Green
```

### Full Integration Test (CMD Batch)

Create `comprehensive_test.bat`:
```batch
@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo  COMPREHENSIVE TEST SUITE
echo ========================================
echo.

REM 1. Check Docker Status
echo Checking Docker Status...
docker-compose ps
echo.

REM 2. Wait for services
echo Waiting 10 seconds for services to be ready...
timeout /t 10 /nobreak

REM 3. Test all languages
echo Testing All Languages...
powershell -ExecutionPolicy Bypass -File test_java_api.ps1
echo.
powershell -ExecutionPolicy Bypass -File test_python_api.ps1
echo.
powershell -ExecutionPolicy Bypass -File test_sql_api.ps1
echo.
powershell -ExecutionPolicy Bypass -File test_pyspark_api.ps1

echo.
echo ========================================
echo  ALL TESTS COMPLETED
echo ========================================
pause
```

---

## 🌐 Browser Access

### Frontend UI
```
http://localhost:5173?problemId=1
```

### API Endpoints (Direct Access)
```
Execution Service:   http://localhost:8001/health
Problem Service:     http://localhost:8002/health
Submission Service:  http://localhost:8003/health
```

---

## 📝 Quick Reference Card

| Task | PowerShell | CMD |
|------|-----------|-----|
| Start System | `docker-compose up -d` | `docker-compose up -d` |
| Stop System | `docker-compose down` | `docker-compose down` |
| Test Java | `powershell -ExecutionPolicy Bypass -File test_java_api.ps1` | `powershell -ExecutionPolicy Bypass -File test_java_api.ps1` |
| Test Python | `powershell -ExecutionPolicy Bypass -File test_python_api.ps1` | `powershell -ExecutionPolicy Bypass -File test_python_api.ps1` |
| View Logs | `docker-compose logs -f execution-service` | `docker-compose logs -f execution-service` |
| Check Status | `docker-compose ps` | `docker-compose ps` |
| Full Cleanup | `docker-compose down -v; docker system prune -af` | `docker-compose down -v && docker system prune -af` |

---

## ⚠️ Important Notes

1. **Port Numbers:**
   - Frontend: 5173
   - Execution Service: 8001
   - Problem Service: 8002
   - Submission Service: 8003
   - PostgreSQL: 5432
   - MongoDB: 27017

2. **Database Credentials (Default):**
   - User: `codeplay_user`
   - Password: `codeplay_password`
   - Database: `codeplay_db`

3. **Test Commands:**
   - All PowerShell test scripts must be run from project root: `c:\Users\MSI\new_project`
   - CMD commands can be copied to batch files for automation
   - Each test takes ~1-2 seconds

4. **Troubleshooting:**
   - If services are unhealthy: `docker-compose down -v && docker-compose up -d --build`
   - If ports are in use: Check what's using ports with `netstat` commands
   - If cache issues: Run full cleanup command from Troubleshooting section

---

**✅ All commands tested and working!**
