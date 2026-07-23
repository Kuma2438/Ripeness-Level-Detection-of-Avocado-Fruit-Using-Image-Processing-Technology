@echo off
chcp 65001 >nul
title 🥑 ระบบตรวจวัดระดับความสุกและสายพันธุ์อะโวคาโด — Control Center
setlocal enabledelayedexpansion

:: Direct argument shortcuts
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
echo   🥑 AVOCADO RIPENESS & VARIETY DETECTION SYSTEM — CONTROL CENTER
echo =========================================================================
echo.
echo   กรุณาเลือกเมนูใช้งาน (Select an option):
echo.
echo    [1] 🥑 เปิดแอปหลัก ตรวจวัดความสุกและสายพันธุ์กล้องคู่ (app.py)
echo    [2] 🎓 เปิดสตูดิโอ ถ่ายรูป/สร้าง Label และเทรนสายพันธุ์ (trainer_gui.py)
echo    [3] ⚡ สุ่มสร้าง / รีเฟรชชุดข้อมูลภาพจำลอง (generate_dataset.py)
echo    [4] 🧪 ทดสอบประสิทธิภาพความเร็วและโมเดล AI (main.py --eval)
echo    [5] 🐙 ซิงก์และ Push โค้ดขึ้น GitHub Repository
echo    [0] ❌ ออกจากโปรแกรม (Exit)
echo.
echo =========================================================================
set /p CHOICE="พิมพ์ตัวเลขเมนู (0-5) แล้วกด Enter: "

if "%CHOICE%"=="1" goto RUN_APP
if "%CHOICE%"=="2" goto RUN_TRAINER
if "%CHOICE%"=="3" goto RUN_DATASET
if "%CHOICE%"=="4" goto RUN_EVAL
if "%CHOICE%"=="5" goto RUN_PUSH
if "%CHOICE%"=="0" goto EXIT_APP

echo.
echo ⚠️ ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง...
timeout /t 2 >nul
goto MENU

:RUN_APP
cls
echo =========================================================================
echo   [>] กำลังเปิดโปรแกรมหลัก (Real-Time Dual-Camera GUI App)...
echo =========================================================================
echo.
python "%~dp0app.py"
echo.
pause
goto MENU

:RUN_TRAINER
cls
echo =========================================================================
echo   [>] กำลังเปิดสตูดิโอเทรนและสร้าง Label สายพันธุ์ (Trainer & Labeler)...
echo =========================================================================
echo.
python "%~dp0trainer_gui.py"
echo.
pause
goto MENU

:RUN_DATASET
cls
echo =========================================================================
echo   [>] กำลังสุ่มสร้าง / รีเฟรชชุดข้อมูลภาพจำลอง (Synthetic Dataset)...
echo =========================================================================
echo.
python "%~dp0generate_dataset.py"
echo.
pause
goto MENU

:RUN_EVAL
cls
echo =========================================================================
echo   [>] กำลังทดสอบประสิทธิภาพความเร็วและ Accuracy ของโมเดล AI...
echo =========================================================================
echo.
python "%~dp0main.py" --eval
echo.
pause
goto MENU

:RUN_PUSH
cls
echo =========================================================================
echo   [>] กำลังซิงก์และ Push อัปเดตขึ้น GitHub Repository...
echo =========================================================================
echo.
set /p COMMIT_MSG="พิมพ์ข้อความอธิบายการอัปเดต (กด Enter หากใช้ข้อความเริ่มต้น): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Update project code, variety trainer, and models

git add .
git commit -m "%COMMIT_MSG%"
git push origin main
echo.
echo [✓] อัปเดตขึ้น GitHub สำเร็จเรียบร้อยแล้ว!
echo.
pause
goto MENU

:EXIT_APP
echo.
echo ขอบคุณที่ใช้งานระบบตรวจวัดระดับความสุกอะโวคาโด ขอให้มีความสุขกับการทำงานครับ!
timeout /t 2 >nul
exit /b 0
