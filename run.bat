@echo off
title Avocado Ripeness and Variety System - Control Center

if /i "%~1"=="1" goto RUN_APP
if /i "%~1"=="app" goto RUN_APP
if /i "%~1"=="2" goto RUN_TRAINER
if /i "%~1"=="trainer" goto RUN_TRAINER
if /i "%~1"=="3" goto RUN_CLI
if /i "%~1"=="cli" goto RUN_CLI
if /i "%~1"=="4" goto BUILD_BIN
if /i "%~1"=="build" goto BUILD_BIN
if /i "%~1"=="5" goto BUILD_INSTALLER
if /i "%~1"=="installer" goto BUILD_INSTALLER
if /i "%~1"=="6" goto RUN_TESTS
if /i "%~1"=="test" goto RUN_TESTS

:MENU
cls
echo =========================================================================
echo   AVOCADO RIPENESS AND VARIETY DETECTION SYSTEM - CONTROL CENTER
echo =========================================================================
echo.
echo   Select an option:
echo.
echo    [1] Launch Desktop Inspection App (On-Demand Mode)
echo    [2] Open Variety Trainer Studio (scripts/run_trainer.py)
echo    [3] Run Interactive / Live Camera CLI (scripts/run_cli.py)
echo    [4] Build Standalone Application Package (scripts/build_standalone.py)
echo    [5] Build Native Windows Setup Installer (scripts/build_installer.py)
echo    [6] Run Automated Unit Tests (pytest / unittest)
echo    [0] Exit
echo.
echo =========================================================================
set /p CHOICE="Enter choice (0-6): "

if "%CHOICE%"=="1" goto RUN_APP
if "%CHOICE%"=="2" goto RUN_TRAINER
if "%CHOICE%"=="3" goto RUN_CLI
if "%CHOICE%"=="4" goto BUILD_BIN
if "%CHOICE%"=="5" goto BUILD_INSTALLER
if "%CHOICE%"=="6" goto RUN_TESTS
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
echo   [>] Running Interactive Avocado CLI...
echo =========================================================================
echo.
python "%~dp0scripts\run_cli.py" --interactive
echo.
pause
goto MENU

:BUILD_BIN
cls
echo =========================================================================
echo   [>] Building Standalone Application Package...
echo =========================================================================
echo.
python "%~dp0scripts\build_standalone.py" --output-dir package
echo.
pause
goto MENU

:BUILD_INSTALLER
cls
echo =========================================================================
echo   [>] Building Native Windows Setup Installer (Setup.exe)...
echo =========================================================================
echo.
python "%~dp0scripts\build_installer.py"
echo.
pause
goto MENU

:RUN_TESTS
cls
echo =========================================================================
echo   [>] Running Automated Tests...
echo =========================================================================
echo.
python -m unittest discover -s tests -p "test_*.py"
echo.
pause
goto MENU

:EXIT_APP
echo.
echo Exiting Avocado Control Center.
timeout /t 2 >nul
exit /b 0
