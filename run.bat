@echo off
title Avocado Ripeness Detection System — Unified Control Center
setlocal enabledelayedexpansion

:: Direct argument handling
if "%~1"=="app" goto RUN_APP
if "%~1"=="dataset" goto RUN_DATASET
if "%~1"=="eval" goto RUN_EVAL
if "%~1"=="push" goto RUN_PUSH

:MENU
cls
echo =================================================================
echo  [+] AVOCADO RIPENESS DETECTION SYSTEM — CONTROL CENTER
echo =================================================================
echo.
echo  Select an option:
echo.
echo   [1] Launch Real-Time Dual-Camera GUI App (app.py)
echo   [2] Generate / Refresh Sample Dataset (generate_dataset.py)
echo   [3] Run ML Model Pipeline & Performance Evaluation
echo   [4] Commit and Push Changes to GitHub Repository
echo   [0] Exit
echo.
echo =================================================================
set /p CHOICE="Enter choice (0-4): "

if "%CHOICE%"=="1" goto RUN_APP
if "%CHOICE%"=="2" goto RUN_DATASET
if "%CHOICE%"=="3" goto RUN_EVAL
if "%CHOICE%"=="4" goto RUN_PUSH
if "%CHOICE%"=="0" goto EXIT_APP

echo Invalid option. Please try again.
timeout /t 2 >nul
goto MENU

:RUN_APP
cls
echo =================================================================
echo  [>] Launching Real-Time Dual-Camera GUI App...
echo =================================================================
echo.
python "%~dp0app.py"
echo.
pause
goto MENU

:RUN_DATASET
cls
echo =================================================================
echo  [>] Generating / Refreshing Synthetic Sample Dataset...
echo =================================================================
echo.
python "%~dp0generate_dataset.py"
echo.
pause
goto MENU

:RUN_EVAL
cls
echo =================================================================
echo  [>] Running Feature Extraction & ML Model Evaluation...
echo =================================================================
echo.
python "%~dp0main.py" --eval
echo.
pause
goto MENU

:RUN_PUSH
cls
echo =================================================================
echo  [>] Syncing & Pushing Changes to GitHub Repository...
echo =================================================================
echo.
set /p COMMIT_MSG="Enter commit message (Press Enter for default): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Update project code and models

git add .
git commit -m "%COMMIT_MSG%"
git push origin main
echo.
echo [+] Git operation completed!
echo.
pause
goto MENU

:EXIT_APP
echo.
echo Exiting Avocado Control Center. Have a great day!
timeout /t 2 >nul
exit /b 0
