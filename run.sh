#!/usr/bin/env bash

# ==============================================================================
# 🥑 Avocado Inspector Launcher for Raspberry Pi 5 (Debian 12 Bookworm)
# Hardware: Raspberry Pi 5 | Camera: OV5647 5MP 1080p (Picamera2 / libcamera)
# ==============================================================================

# Determine Script Directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR" || exit 1

# Ensure DISPLAY is set for GUI on Wayland/X11
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
fi

# 1. System Package Setup (Fix PEP 668 & Raspberry Pi OS Bookworm dependencies)
setup_rpi_env() {
    echo "======================================================================"
    echo " 📦 Installing Raspberry Pi 5 System Dependencies..."
    echo "======================================================================"
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv python3-opencv \
                        python3-pil python3-pil.imagetk python3-tk \
                        python3-picamera2 libcamera-apps v4l-utils
    
    # Create Virtual Environment if not exists
    if [ ! -d "$SCRIPT_DIR/venv" ]; then
        echo "🌱 Creating Python Virtual Environment (venv)..."
        python3 -m venv --system-site-packages "$SCRIPT_DIR/venv"
    fi

    echo "⚡ Installing PyTorch & CustomTkinter into venv..."
    "$SCRIPT_DIR/venv/bin/pip" install --upgrade pip
    "$SCRIPT_DIR/venv/bin/pip" install torch torchvision customtkinter opencv-python pillow
    echo "✅ Setup Complete!"
}

# Auto-Create Virtual Environment with System Site Packages (for Picamera2 access)
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "🌱 Initializing Python Virtual Environment for Raspberry Pi 5..."
    python3 -m venv --system-site-packages "$SCRIPT_DIR/venv" 2>/dev/null
fi

# Activate Virtual Environment
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# CLI Flag Shortcut Handlers
if [ "$1" == "--app" ] || [ "$1" == "1" ]; then
    echo "🚀 Starting Main Dashboard Inspector..."
    $PYTHON_CMD app.py
    exit 0
elif [ "$1" == "--trainer" ] || [ "$1" == "2" ]; then
    echo "🎓 Starting Variety Trainer Studio..."
    $PYTHON_CMD trainer_gui.py
    exit 0
elif [ "$1" == "--eval" ] || [ "$1" == "3" ]; then
    echo "🧪 Running Model Performance Evaluation..."
    $PYTHON_CMD main.py --eval
    exit 0
elif [ "$1" == "--dataset" ] || [ "$1" == "4" ]; then
    echo "📂 Generating Sample Dataset..."
    $PYTHON_CMD main.py --dataset
    exit 0
fi

# Interactive Terminal Menu
show_menu() {
    clear
    echo "======================================================================"
    echo " 🥑 ระบบตรวจวัดระดับความสุกและสายพันธุ์อะโวคาโด (Raspberry Pi 5 Edition)"
    echo "    Hardware: Raspberry Pi 5 | Camera: OV5647 5MP (Picamera2 / libcamera)"
    echo "======================================================================"
    echo ""
    echo "  [1] เปิดแอปพลิเคชันหลัก (Main Dashboard Inspector)"
    echo "  [2] เปิดสตูดิโอเทรนสายพันธุ์ (Variety Trainer Studio)"
    echo "  [3] ทดสอบวัดประสิทธิภาพโมเดล (Model Evaluation 70/30)"
    echo "  [4] สร้างชุดข้อมูลจำลอง (Generate Sample Dataset)"
    echo "  [5] ตรวจสอบกล้อง OV5647 (Test Raspberry Pi 5 Picamera2/V4L2)"
    echo "  [6] ติดตั้งสภาพแวดล้อม Pi 5 อัตโนมัติ (Auto Setup RPi 5 Packages)"
    echo "  [7] ออกจากโปรแกรม (Exit)"
    echo ""
    echo "======================================================================"
    read -rp "กรุณาเลือกเมนู [1-7]: " CHOICE

    case $CHOICE in
        1)
            echo "🚀 กำลังเปิดหน้าจอหลัก..."
            $PYTHON_CMD app.py
            read -rp "กด Enter เพื่อกลับสู่เมนูหลัก..."
            show_menu
            ;;
        2)
            echo "🎓 กำลังเปิดสตูดิโอเทรน..."
            $PYTHON_CMD trainer_gui.py
            read -rp "กด Enter เพื่อกลับสู่เมนูหลัก..."
            show_menu
            ;;
        3)
            echo "🧪 กำลังทดสอบวัดประสิทธิภาพโมเดล..."
            $PYTHON_CMD main.py --eval
            read -rp "กด Enter เพื่อกลับสู่เมนูหลัก..."
            show_menu
            ;;
        4)
            echo "📂 กำลังสร้างชุดข้อมูลจำลอง..."
            $PYTHON_CMD main.py --dataset
            read -rp "กด Enter เพื่อกลับสู่เมนูหลัก..."
            show_menu
            ;;
        5)
            echo "📹 กำลังทดสอบกล้อง Raspberry Pi 5 (OV5647)..."
            $PYTHON_CMD -c "
try:
    from picamera2 import Picamera2
    print('✅ Picamera2 is INSTALLED and READY!')
    picam2 = Picamera2()
    print('Picamera2 object initialized successfully!')
except Exception as e:
    print('⚠️ Picamera2 Note:', e)

import cv2
print('Testing OpenCV Video Capture devices...')
for idx in range(4):
    cap = cv2.VideoCapture(idx)
    if cap.isOpened():
        ret, frame = cap.read()
        print(f' - /dev/video{idx}: Active (Read status: {ret})')
        cap.release()
    else:
        print(f' - /dev/video{idx}: Not Available')
"
            read -rp "กด Enter เพื่อกลับสู่เมนูหลัก..."
            show_menu
            ;;
        6)
            setup_rpi_env
            read -rp "กด Enter เพื่อกลับสู่เมนูหลัก..."
            show_menu
            ;;
        7)
            echo "👋 ปิดโปรแกรม เรียบร้อยแล้ว"
            exit 0
            ;;
        *)
            echo "❌ ตัวเลือกไม่ถูกต้อง!"
            sleep 1
            show_menu
            ;;
    esac
}

show_menu
