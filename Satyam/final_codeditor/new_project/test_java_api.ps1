$javaCode = @"
import java.util.Scanner;

class Main {
    public static void main(String[] args) {
        Scanner s = new Scanner(System.in);
        int a = s.nextInt();
        int b = s.nextInt();
        System.out.println(a + b);
    }
}
"@

$payload = @{
    language = "java"
    files = @(@{ name = "Main"; content = $javaCode })
    stdin = "3`n5"
} | ConvertTo-Json

Write-Host "Testing Java Code Execution..."
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
    if ($output -eq "8") {
        Write-Host "✅ Test Case PASSED" -ForegroundColor Green
        Write-Host "Expected: 8 | Got: $output" -ForegroundColor Green
    } else {
        Write-Host "❌ Test Case FAILED" -ForegroundColor Red
        Write-Host "Expected: 8 | Got: $output" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error calling execution service: $_" -ForegroundColor Red
}
