@echo off
title Zeni Translate Launcher
echo =====================================================
echo    ✨ Launching Zeni Translate Web Application... ✨
echo =====================================================
echo.
cd /d "%~dp0"

echo Opening browser at http://127.0.0.1:5050 ...
timeout /t 2 /nobreak > nul
start http://127.0.0.1:5050

echo Starting Python server...
python app.py
pause
