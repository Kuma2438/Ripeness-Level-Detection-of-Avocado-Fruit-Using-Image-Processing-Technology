@echo off
title Avocado Ripeness and Variety System - Control Center

if /i "%~1"=="1" goto RUN_APP
if /i "%~1"=="app" goto RUN_APP
if /i "%~1"=="2" goto RUN_TRAINER
if /i "%~1"=="trainer" goto RUN_TRAINER
if /i "%~1"=="3" goto RUN_CLI
if /i "%~1"=="cli" goto RUN_CLI
if /i "%~1"=="4" goto RUN_TESTS
if /i "%~1"=="test" goto RUN_TESTS

:MENU
cls
echo =========================================================================
echo   AVOCADO RIPENESS AND VARIETY DETECTION SYSTEM - CONTROL CENTER
echo =========================================================================
echo.
echo   Select an option:
echo.
echo    [1] Launch Desktop Inspection App (scripts/run_app.py)
echo    [2] Open Variety Trainer Studio (scripts/run_trainer.py)
echo    [3] Run Headless Live Camera CLI (scripts/run_cli.py --live)
echo    [4] Run Automated Unit Tests (pytest)
echo    [0] Exit
echo.
echo =========================================================================
set /p CHOICE="Enter choice (0-4): "

if "%CHOICE%"=="1" goto RUN_APP
if "%CHOICE%"=="2" goto RUN_TRAINER
if "%CHOICE%"=="3" goto RUN_CLI
if "%CHOICE%"=="4" goto RUN_TESTS
if "%CHOICE%"=="0" goto EXIT_APP

echo.
echo Invalid option. Please try again.
timeout /t 2 >nul
goto MENU

:RUN_APP
cls
echo =========================================================================
echo   [>] Launching Avocado Inspection App...
echo =========================================================================
echo.
python "%~dp0scripts\run_app.py"
echo.
pause
goto MENU

:RUN_TRAINER
cls
echo =========================================================================
echo   [>] Launching Avocado Variety Trainer Studio...
echo =========================================================================
echo.
python "%~dp0scripts\run_trainer.py"
echo.
pause
goto MENU

:RUN_CLI
cls
echo =========================================================================
echo   [>] Running Headless Live Camera CLI...
echo =========================================================================
echo.
python "%~dp0scripts\run_cli.py" --live
echo.
pause
goto MENU

:RUN_TESTS
cls
echo =========================================================================
echo   [>] Running Automated Tests...
echo =========================================================================
echo.
pytest
echo.
pause
goto MENU

:EXIT_APP
echo.
echo Exiting Avocado Control Center.
timeout /t 2 >nul
exit /b 0
