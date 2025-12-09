$pysparkCode = @"
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("test").getOrCreate()
result = sum([1, 2, 3, 4, 5])
print(result)
"@

$payload = @{
    language = "pyspark"
    files = @(@{ name = "solution"; content = $pysparkCode })
    stdin = ""
} | ConvertTo-Json

Write-Host "Testing PySpark Code Execution..."
Write-Host "==============================" -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/run" -Method POST -Body $payload -ContentType "application/json"
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host "Status: " -ForegroundColor Green -NoNewline
    Write-Host $result.status
    
    $output = $result.run.stdout.Trim()
    Write-Host "Output: " -ForegroundColor Green -NoNewline
    Write-Host $output -ForegroundColor Yellow
    
    if ($result.run.stderr) {
        Write-Host "Error: " -ForegroundColor Red -NoNewline
        Write-Host $result.run.stderr
    }
    
    Write-Host ""
    if ($output -match "15") {
        Write-Host "✅ Test Case PASSED" -ForegroundColor Green
        Write-Host "Expected: 15 | Got: $output" -ForegroundColor Green
    } else {
        Write-Host "❌ Test Case FAILED" -ForegroundColor Red
        Write-Host "Expected: 15 | Got: $output" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error calling execution service: $_" -ForegroundColor Red
}
