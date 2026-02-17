# Phase 7 Demo Script (PowerShell)
# Run from repo root: powershell -ExecutionPolicy Bypass -File .\scripts\demo_phase7.ps1

$baseUrl = "http://127.0.0.1:8000"

Write-Host "Step 1: Assign PRJ001 to Arjun/D001" -ForegroundColor Cyan
$assignBody = '{"mission_id":"PRJ001","pilot_name":"Arjun","drone_id":"D001"}'
try {
    $assignResp = Invoke-WebRequest -Uri "$baseUrl/api/assign_mission" -Method POST -Body $assignBody -ContentType "application/json" -UseBasicParsing
    Write-Host "Assign response:" -ForegroundColor Green
    Write-Host $assignResp.Content
} catch {
    Write-Host "Assign failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "" 
Write-Host "Step 2: Manually set pilot Arjun status to 'On Leave' in Google Sheets" -ForegroundColor Yellow
Write-Host "Then press Enter to continue." -ForegroundColor Yellow
Read-Host

Write-Host "Step 3: Trigger urgent reassignment for PRJ001" -ForegroundColor Cyan
try {
    $urgentResp = Invoke-WebRequest -Uri "$baseUrl/api/urgent_reassign/PRJ001" -Method POST -UseBasicParsing
    Write-Host "Urgent reassignment response:" -ForegroundColor Green
    Write-Host $urgentResp.Content
} catch {
    Write-Host "Urgent reassignment failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "" 
Write-Host "Step 4: Fetch missions to verify updates" -ForegroundColor Cyan
try {
    $missionsResp = Invoke-WebRequest -Uri "$baseUrl/api/missions" -UseBasicParsing
    Write-Host $missionsResp.Content
} catch {
    Write-Host "Fetch missions failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "" 
Write-Host "Step 5: Fetch reassignment log" -ForegroundColor Cyan
try {
    $logResp = Invoke-WebRequest -Uri "$baseUrl/api/reassignment_log" -UseBasicParsing
    Write-Host $logResp.Content
} catch {
    Write-Host "Fetch log failed: $($_.Exception.Message)" -ForegroundColor Red
}
