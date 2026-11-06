@echo off
title Sync & Organize GitHub Repository
color 0A

echo ============================================================
echo   Smart Inventory Billing System - GitHub Sync
echo   Author: Suman Mondal
echo ============================================================
echo.

set GIT_PATH=C:\Users\suman\AppData\Local\GitHubDesktop\app-3.6.7\resources\app\git\cmd\git.exe

if not exist "%GIT_PATH%" (
    where git >nul 2>&1
    if %errorlevel% equ 0 (
        set GIT_PATH=git
    ) else (
        echo [!] Git executable not found automatically.
        echo Please open GitHub Desktop app on your PC and click "Push origin"!
        pause
        exit /b 1
    )
)

echo [✓] Found Git executable!
"%GIT_PATH%" --version
echo.

echo [>] Syncing complete 30-day repository and release tags (Day 1 to Day 30 - v1.0.0)...
echo     Repository: https://github.com/suman778m-sudo/Smart-Inventory-Billing-Management-System.git
echo.

"%GIT_PATH%" push -u origin main
"%GIT_PATH%" push origin --tags

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo   SUCCESS! Your GitHub repository is now perfectly arranged!
    echo   All folders (services/, models/, ui/, docs/, tests/) and
    echo   daily commit history are live on GitHub!
    echo   View: https://github.com/suman778m-sudo/Smart-Inventory-Billing-Management-System
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo   Push needs authorization or GitHub Desktop.
    echo   Option A: Complete the sign-in prompt if one appeared.
    echo   Option B: Open GitHub Desktop app -> Click "Push origin".
    echo ============================================================
)

echo.
pause
