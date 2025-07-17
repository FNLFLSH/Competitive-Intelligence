# Intelligence Backend & Frontend Server Starter
Write-Host "🚀 Starting Intelligence Backend and Frontend Servers..." -ForegroundColor Green
Write-Host ""

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet
        return $connection.TcpTestSucceeded
    }
    catch {
        return $false
    }
}

# Kill any existing processes on ports 8000 and 3000
Write-Host "🔧 Checking for existing processes..." -ForegroundColor Yellow
if (Test-Port 8000) {
    Write-Host "⚠️  Port 8000 is in use. Killing existing process..." -ForegroundColor Yellow
    Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force -ErrorAction SilentlyContinue
}
if (Test-Port 3000) {
    Write-Host "⚠️  Port 3000 is in use. Killing existing process..." -ForegroundColor Yellow
    Get-Process | Where-Object {$_.ProcessName -eq "node"} | Stop-Process -Force -ErrorAction SilentlyContinue
}

Write-Host ""

# Start Backend Server
Write-Host "📊 Starting Backend Server (Port 8000)..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/k", "cd backend && python integrated_review_scraper.py" -WindowStyle Normal

# Wait for backend to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if backend is running
$backendRunning = $false
for ($i = 1; $i -le 10; $i++) {
    if (Test-Port 8000) {
        $backendRunning = $true
        Write-Host "✅ Backend server is running on port 8000" -ForegroundColor Green
        break
    }
    Write-Host "⏳ Waiting for backend... (attempt $i/10)" -ForegroundColor Yellow
    Start-Sleep -Seconds 2
}

if (-not $backendRunning) {
    Write-Host "❌ Backend server failed to start" -ForegroundColor Red
    exit 1
}

# Start Frontend Server
Write-Host "🌐 Starting Frontend Server (Port 3000)..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/k", "cd frontend && npm run dev" -WindowStyle Normal

# Wait for frontend to start
Write-Host "⏳ Waiting for frontend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if frontend is running
$frontendRunning = $false
for ($i = 1; $i -le 15; $i++) {
    if (Test-Port 3000) {
        $frontendRunning = $true
        Write-Host "✅ Frontend server is running on port 3000" -ForegroundColor Green
        break
    }
    Write-Host "⏳ Waiting for frontend... (attempt $i/15)" -ForegroundColor Yellow
    Start-Sleep -Seconds 2
}

if (-not $frontendRunning) {
    Write-Host "❌ Frontend server failed to start" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 Both servers are running successfully!" -ForegroundColor Green
Write-Host "📊 Backend: http://localhost:8000" -ForegroundColor White
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Yellow

# Keep the script running
try {
    while ($true) {
        Start-Sleep -Seconds 10
        $backendStatus = if (Test-Port 8000) { "✅ Running" } else { "❌ Stopped" }
        $frontendStatus = if (Test-Port 3000) { "✅ Running" } else { "❌ Stopped" }
        Write-Host "Status - Backend: $backendStatus | Frontend: $frontendStatus" -ForegroundColor Gray
    }
}
catch {
    Write-Host ""
    Write-Host "🛑 Stopping servers..." -ForegroundColor Red
    Get-Process | Where-Object {$_.ProcessName -eq "python" -or $_.ProcessName -eq "node"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Servers stopped" -ForegroundColor Green
} 