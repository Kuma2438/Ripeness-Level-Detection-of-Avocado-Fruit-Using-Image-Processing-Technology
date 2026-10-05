# 🥑 Avocado Ripeness & Variety Detection System

[![Platform: Raspberry Pi 5 / Linux / Windows](https://img.shields.io/badge/Platform-Raspberry%20Pi%205%20%7C%20Linux%20%7C%20Windows-blue.svg)](https://www.raspberrypi.com/products/raspberry-pi-5/)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![PyTorch: 2.0+](https://img.shields.io/badge/PyTorch-2.0%2B-red.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end computer vision and deep learning system for **on-demand avocado ripeness level estimation** and **variety classification**, designed for standalone deployment on **Raspberry Pi 5** with **Dual USB Webcams**.

---

## 🌟 Key Features

- **On-Demand Inspection Workflow**:
  - **Standby Mode**: Lightweight continuous 30 FPS camera preview with alignment guide box and **zero AI CPU load**.
  - **Click to Capture & Analyze**: Trigger instant fruit inspection via the large UI button or keyboard shortcuts (**Spacebar** / **Enter**).
  - **Frozen Inspected Frame**: Locks the captured frame, draws bounding boxes, classifies variety & ripeness stage, and sets the ripeness gauge.
  - **Reset / Next Fruit**: Instantly return to standby for the next avocado.
- **Dual USB Webcams**: Simultaneously inspects both sides of the avocado fruit with automatic camera device detection and simulation fallback.
- **Lightweight PyTorch CNN**: Custom CNN architecture (`AvocadoCNN`) optimized for fast CPU inference on ARM64 (Raspberry Pi 5 Cortex-A76).
- **Interactive Ripeness Gauge**: Real-time speedometer gauge displaying ripeness percentage (0–100%) and stage (*Unripe*, *Mid-ripe*, *Ripe*).
- **Trainer & Labeler Studio**: Built-in GUI to register new avocado varieties, capture training snapshots directly from the camera, and retrain the CNN on-device.
- **Standalone Binary Packaging**: Automated PyInstaller builder to create single-directory standalone executables with zero Python dependency prerequisites on target devices.

---

## 🏗️ Project Architecture

```
Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology/
├── configs/
│   └── default.yaml                # Camera IDs, model paths, thresholds, classes
├── dataset/                        # Training datasets
│   ├── mid_ripe/
│   ├── ripe/
│   ├── unripe/
│   └── varieties/                  # Variety-specific subfolders (e.g., Hass, Pinkerton)
├── models/                         # Pre-trained CNN weights
│   ├── ripeness_cnn.pth
│   └── variety_cnn.pth
├── src/
│   └── avocado/
│       ├── __init__.py
│       ├── config.py               # YAML & dynamic path configuration loader
│       ├── core/
│       │   ├── model.py            # AvocadoCNN architecture & serialization
│       │   ├── classifier.py       # Ripeness & Variety inference engine
│       │   └── trainer.py          # PyTorch training & evaluation pipeline
│       ├── camera/
│       │   └── manager.py          # Dual USB camera manager (V4L2 / DirectShow)
│       ├── ui/
│       │   ├── app.py              # On-Demand Desktop Inspector GUI (Standby/Capture)
│       │   ├── trainer_gui.py      # Dataset Collector & Model Training Studio
│       │   └── widgets/
│       │       └── gauge.py        # Tkinter Canvas Speedometer Gauge widget
│       └── utils/
│           └── dataset_gen.py      # Synthetic dataset generator
├── scripts/
│   ├── run_app.py                  # Launch desktop Inspection GUI
│   ├── run_trainer.py              # Launch Trainer & Labeler Studio
│   ├── run_cli.py                  # Interactive on-demand CLI for single/live inspection
│   ├── build_standalone.py         # PyInstaller standalone binary builder
│   └── setup_pi5.sh                # Automated setup script for Raspberry Pi 5
├── tests/
│   ├── test_model.py               # Model architecture & weight tests
│   ├── test_classifier.py          # Classification & scoring tests
│   └── test_camera.py              # Camera fallback & frame generation tests
├── pyproject.toml                  # Modern Python packaging configuration
├── requirements.txt                # Pinned dependency requirements
├── run.bat                         # Windows Control Center launcher
└── run.sh                          # Linux / Raspberry Pi 5 launcher
```

---

## 🍓 Raspberry Pi 5 Setup Guide

### 1. Hardware Requirements
- **Raspberry Pi 5** (4GB or 8GB recommended)
- **Raspberry Pi OS 64-bit (Debian 12 Bookworm)**
- **2x USB Webcams** connected to USB 3.0 ports (probed as `/dev/video0` and `/dev/video2`)
- Optional: Touchscreen display / Monitor or headless SSH connection

### 2. Quick Automated Installation
Open a terminal on your Raspberry Pi 5 and run:

```bash
cd Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology
chmod +x scripts/setup_pi5.sh run.sh
./scripts/setup_pi5.sh
```

---

## 🚀 Running the Application

### 🎮 Option 1: Desktop GUI (On-Demand Inspection)
```bash
python scripts/run_app.py
```
**Controls:**
- **Spacebar / Enter / Click Button**: Capture synchronized snapshot & run analysis.
- **Spacebar / Enter (after scan)**: Reset back to standby for next fruit.
- **Trainer Studio**: Open on-device label manager and model trainer.
- **Snapshot**: Save annotated scan photos to `snapshots/`.

---

### 🖥️ Option 2: Interactive Terminal CLI
```bash
# Interactive on-demand inspection via terminal:
python scripts/run_cli.py --interactive

# Continuous live streaming CLI:
python scripts/run_cli.py --live

# Output structured JSON (for PLC/robotics/microcontrollers):
python scripts/run_cli.py --interactive --json
```

---

### 📦 Option 3: Build Standalone Executable
To package the app into a single standalone binary for distribution:

```bash
python scripts/build_standalone.py
```
Output executable will be placed in `dist/avocado-inspector/`.

---

## ⚙️ Configuration (`configs/default.yaml`)

```yaml
camera:
  cam1_id: 0                  # Primary USB camera index (/dev/video0)
  cam2_id: 1                  # Secondary USB camera index (/dev/video2)
  width: 640
  height: 480
  fps: 30
  auto_fallback: true         # Fallback to simulation if a camera is disconnected

models:
  ripeness_model_path: "models/ripeness_cnn.pth"
  variety_model_path: "models/variety_cnn.pth"
  device: "auto"              # "cpu", "cuda", or "auto"

inference:
  ripeness_weight_color: 0.35
  ripeness_weight_cnn: 0.65
  unripe_threshold: 35.0
  mid_ripe_threshold: 70.0
```

---

## 🧪 Running Automated Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📄 License
This project is open-source under the MIT License.
