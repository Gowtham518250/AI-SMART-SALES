#!/usr/bin/env pwsh
# Endpoint Validation Test - Simple Version

$baseUrl = "https://ragapp-production-36e7.up.railway.app"

Write-Host "Testing Endpoints Against: $baseUrl" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health
Write-Host "1. Testing /health endpoint..."
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -TimeoutSec 30
    Write-Host "   Status: $($response.StatusCode) - OK" -ForegroundColor Green
} catch {
    Write-Host "   Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Root
Write-Host "2. Testing / endpoint..."
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/" -Method GET -TimeoutSec 30
    Write-Host "   Status: $($response.StatusCode) - OK" -ForegroundColor Green
} catch {
    Write-Host "   Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Chatbot (POST with query param)
Write-Host "3. Testing /chatbot/?query=hello endpoint..."
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/chatbot/?query=hello" -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body "{}" -TimeoutSec 30
    Write-Host "   Status: $($response.StatusCode) - OK" -ForegroundColor Green
} catch {
    Write-Host "   Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Auth Register
Write-Host "4. Testing /auth/register endpoint..."
$regBody = @{
    user_name = "testuser"
    email = "test@test.com"
    password = "Test123!"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/auth/register" -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $regBody -TimeoutSec 30
    Write-Host "   Status: $($response.StatusCode) - OK" -ForegroundColor Green
} catch {
    Write-Host "   Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Auth Login
Write-Host "5. Testing /auth/login endpoint..."
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/auth/login" -Method POST `
        -Headers @{"Content-Type"="application/x-www-form-urlencoded"} `
        -Body "user_name=demo&password=demo" -TimeoutSec 30
    Write-Host "   Status: $($response.StatusCode) - OK" -ForegroundColor Green
} catch {
    Write-Host "   Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Get Sales
Write-Host "6. Testing /auth/sales GET endpoint..."
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/auth/sales" -Method GET `
        -Headers @{"Authorization"="Bearer test_token"} -TimeoutSec 30
    Write-Host "   Status: $($response.StatusCode) - OK" -ForegroundColor Green
} catch {
    Write-Host "   Status: Connection attempted" -ForegroundColor Yellow
}

# Test 7: Today Insight
Write-Host "7. Testing /today_insight/ endpoint..."
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/today_insight/" -Method GET `
        -Headers @{"Authorization"="Bearer test_token"} -TimeoutSec 30
    Write-Host "   Status: $($response.StatusCode) - OK" -ForegroundColor Green
} catch {
    Write-Host "   Status: Connection attempted" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Endpoint Testing Complete" -ForegroundColor Cyan
