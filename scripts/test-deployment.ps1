# MirrorMind Deployment Test Script (PowerShell)
# Tests if backend and frontend are properly deployed

Write-Host "🧪 Testing MirrorMind Deployment..." -ForegroundColor Cyan
Write-Host ""

# Get URLs from user
$BACKEND_URL = Read-Host "Enter your backend URL (e.g., https://mirrormind-backend.onrender.com)"
$FRONTEND_URL = Read-Host "Enter your frontend URL (e.g., https://mirrormind.vercel.app)"

Write-Host ""
Write-Host "Testing backend at: $BACKEND_URL"
Write-Host "Testing frontend at: $FRONTEND_URL"
Write-Host ""

# Test 1: Backend Health Check
Write-Host "1️⃣  Testing backend health check..."
try {
    $response = Invoke-WebRequest -Uri "$BACKEND_URL/" -Method Get -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Backend is responding" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Backend API Endpoints
Write-Host "2️⃣  Testing backend API endpoints..."
try {
    $response = Invoke-WebRequest -Uri "$BACKEND_URL/api/agents" -Method Get -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Agents API is working" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Agents API failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Frontend Accessibility
Write-Host "3️⃣  Testing frontend accessibility..."
try {
    $response = Invoke-WebRequest -Uri "$FRONTEND_URL" -Method Get -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Frontend is accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Frontend failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: CORS Check
Write-Host "4️⃣  Testing CORS configuration..."
try {
    $headers = @{
        "Origin" = $FRONTEND_URL
        "Access-Control-Request-Method" = "POST"
    }
    $response = Invoke-WebRequest -Uri "$BACKEND_URL/api/agents" -Method Options -Headers $headers -UseBasicParsing
    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 204) {
        Write-Host "✓ CORS is configured correctly" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ CORS might need configuration" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Deployment test complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Visit $FRONTEND_URL in your browser"
Write-Host "2. Try creating a debate"
Write-Host "3. Test the agent builder"
Write-Host ""
