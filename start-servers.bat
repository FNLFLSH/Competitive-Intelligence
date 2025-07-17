@echo off
echo 🚀 Starting Intelligence Backend and Frontend Servers...
echo.

echo 📊 Starting Backend Server (Port 8000)...
start "Backend Server" cmd /k "cd backend && python integrated_review_scraper.py"

echo ⏳ Waiting 3 seconds for backend to initialize...
timeout /t 3 /nobreak > nul

echo 🌐 Starting Frontend Server (Port 3000)...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Both servers are starting...
echo 📊 Backend: http://localhost:8000
echo 🌐 Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
pause > nul 