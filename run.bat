@echo off
title Avocado Ripeness and Variety System - Control Center

if /i "%~1"=="1" goto RUN_APP
if /i "%~1"=="app" goto RUN_APP
if /i "%~1"=="2" goto RUN_TRAINER
if /i "%~1"=="trainer" goto RUN_TRAINER
if /i "%~1"=="3" goto RUN_DATASET
if /i "%~1"=="dataset" goto RUN_DATASET
if /i "%~1"=="4" goto RUN_EVAL
if /i "%~1"=="eval" goto RUN_EVAL
if /i "%~1"=="5" goto RUN_PUSH
if /i "%~1"=="push" goto RUN_PUSH

:MENU
cls
echo =========================================================================
echo   AVOCADO RIPENESS AND VARIETY DETECTION SYSTEM - CONTROL CENTER
echo =========================================================================
echo.
echo   Select an option:
echo.
echo    [1] Launch Real-Time Dual-Camera GUI App (app.py)
echo    [2] Open Variety Trainer and Labeler Studio (trainer_gui.py)
echo    [3] Generate / Refresh Synthetic Sample Dataset (generate_dataset.py)
echo    [4] Run ML Model Pipeline and Performance Evaluation (main.py --eval)
echo    [5] Commit and Push Changes to GitHub Repository
echo    [0] Exit
echo.
echo =========================================================================
set /p CHOICE="Enter choice (0-5): "

if "%CHOICE%"=="1" goto RUN_APP
if "%CHOICE%"=="2" goto RUN_TRAINER
if "%CHOICE%"=="3" goto RUN_DATASET
if "%CHOICE%"=="4" goto RUN_EVAL
if "%CHOICE%"=="5" goto RUN_PUSH
if "%CHOICE%"=="0" goto EXIT_APP

echo.
echo Invalid option. Please try again.
timeout /t 2 >nul
goto MENU

:RUN_APP
cls
echo =========================================================================
echo   [>] Launching Real-Time Dual-Camera GUI App...
echo =========================================================================
echo.
python "%~dp0app.py"
echo.
pause
goto MENU

:RUN_TRAINER
cls
echo =========================================================================
echo   [>] Launching Avocado Variety Trainer and Labeler Studio...
echo =========================================================================
echo.
python "%~dp0trainer_gui.py"
echo.
pause
goto MENU

:RUN_DATASET
cls
echo =========================================================================
echo   [>] Generating / Refreshing Synthetic Sample Dataset...
echo =========================================================================
echo.
python "%~dp0generate_dataset.py"
echo.
pause
goto MENU

:RUN_EVAL
cls
echo =========================================================================
echo   [>] Running Feature Extraction and ML Model Evaluation...
echo =========================================================================
echo.
python "%~dp0main.py" --eval
echo.
pause
goto MENU

:RUN_PUSH
cls
echo =========================================================================
echo   [>] Syncing and Pushing Changes to GitHub Repository...
echo =========================================================================
echo.
set /p COMMIT_MSG="Enter commit message (Press Enter for default): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Update project code, variety trainer, and models

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
