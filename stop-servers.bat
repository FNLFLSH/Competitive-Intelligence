@echo off
echo 🛑 Stopping Intelligence Backend and Frontend Servers...
echo.

echo 🔧 Killing Python processes (Backend)...
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul

echo 🔧 Killing Node processes (Frontend)...
taskkill /f /im node.exe 2>nul

echo.
echo ✅ All servers stopped
echo.
pause 