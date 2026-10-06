@echo off
setlocal enabledelayedexpansion
title Avocado Ripeness and Variety System - Control Center

:: =========================================================================
:: Python Environment Resolution & Auto-Bootstrap
:: =========================================================================
set "PY_CMD="

:: 1. Check local virtual environment
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PY_CMD=%~dp0.venv\Scripts\python.exe"
    goto PYTHON_READY
)

:: 2. Check py launcher
py -3 -c "import sys" >nul 2>&1
if !errorlevel! equ 0 (
    set "PY_CMD=py -3"
    goto CHECK_VENV
)

:: 3. Check system python (verify not Microsoft Store dummy alias)
python -c "import sys" >nul 2>&1
if !errorlevel! equ 0 (
    set "PY_CMD=python"
    goto CHECK_VENV
)

:: 4. Check standard installation directories
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python310\python.exe"
) do (
    if exist %%P (
        set "PY_CMD=%%~P"
        goto CHECK_VENV
    )
)

:: 5. Python not found - Prompt user to install
:PYTHON_NOT_FOUND
cls
echo =========================================================================
echo   [!] PYTHON ENVIRONMENT NOT DETECTED
echo =========================================================================
echo.
echo   Avocado Ripeness System requires Python 3.10 or higher.
echo.
echo   Select an option to automatically setup Python:
echo.
echo    [1] Auto-Install Official Python 3.11 via Windows winget (Recommended)
echo    [2] Open Python.org Download Page in Browser
echo    [0] Exit
echo.
echo =========================================================================
set /p INST_CHOICE="Enter choice (1, 2, or 0): "

if "%INST_CHOICE%"=="1" (
    echo.
    echo [*] Installing Python 3.11 via winget... Please wait a moment...
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    echo.
    echo [+] Python installed. Restarting environment...
    timeout /t 3 >nul
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
    set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto CHECK_VENV
)

if "%INST_CHOICE%"=="2" (
    start https://www.python.org/downloads/windows/
    exit /b 0
)

exit /b 1

:: 6. Setup local virtual environment & dependencies if missing
:CHECK_VENV
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo.
    echo =========================================================================
    echo   [*] Initial Setup: Creating local Virtual Environment (.venv)...
    echo =========================================================================
    %PY_CMD% -m venv "%~dp0.venv"
    if exist "%~dp0.venv\Scripts\python.exe" (
        set "PY_CMD=%~dp0.venv\Scripts\python.exe"
        echo [*] Installing required dependencies (PyTorch, OpenCV, CustomTkinter)...
        !PY_CMD! -m pip install --upgrade pip
        !PY_CMD! -m pip install -r "%~dp0requirements.txt"
        !PY_CMD! -m pip install -e "%~dp0"
        echo [+] Setup completed successfully!
    )
) else (
    set "PY_CMD=%~dp0.venv\Scripts\python.exe"
)

:PYTHON_READY

:: Handle CLI shortcuts
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
echo   Python Runtime: !PY_CMD!
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
"%PY_CMD%" "%~dp0scripts\run_app.py"
echo.
pause
goto MENU

:RUN_TRAINER
cls
echo =========================================================================
echo   [>] Launching Avocado Variety Trainer Studio...
echo =========================================================================
echo.
"%PY_CMD%" "%~dp0scripts\run_trainer.py"
echo.
pause
goto MENU

:RUN_CLI
cls
echo =========================================================================
echo   [>] Running Interactive Avocado CLI...
echo =========================================================================
echo.
"%PY_CMD%" "%~dp0scripts\run_cli.py" --interactive
echo.
pause
goto MENU

:BUILD_BIN
cls
echo =========================================================================
echo   [>] Building Standalone Application Package...
echo =========================================================================
echo.
"%PY_CMD%" "%~dp0scripts\build_standalone.py" --output-dir package
echo.
pause
goto MENU

:BUILD_INSTALLER
cls
echo =========================================================================
echo   [>] Building Native Windows Setup Installer (Setup.exe)...
echo =========================================================================
echo.
"%PY_CMD%" "%~dp0scripts\build_installer.py"
echo.
pause
goto MENU

:RUN_TESTS
cls
echo =========================================================================
echo   [>] Running Automated Tests...
echo =========================================================================
echo.
"%PY_CMD%" -m unittest discover -s tests -p "test_*.py"
echo.
pause
goto MENU

:EXIT_APP
echo.
echo Exiting Avocado Control Center.
timeout /t 2 >nul
exit /b 0
