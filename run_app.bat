@echo off
title Smart Inventory & Billing Management System
color 0B
echo ============================================================
echo   Smart Inventory & Billing Management System - v1.0.0
echo   Author: Suman Mondal
echo ============================================================
echo.
echo Launching application...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Python execution exited with error code %ERRORLEVEL%.
    echo Please ensure dependencies are installed via: pip install -r requirements.txt
    pause
)
