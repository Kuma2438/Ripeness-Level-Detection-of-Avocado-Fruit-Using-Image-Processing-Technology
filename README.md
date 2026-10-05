# 🥑 Avocado Ripeness & Variety Detection System

[![Platform: Raspberry Pi 5 / Linux / Windows](https://img.shields.io/badge/Platform-Raspberry%20Pi%205%20%7C%20Linux%20%7C%20Windows-blue.svg)](https://www.raspberrypi.com/products/raspberry-pi-5/)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![PyTorch: 2.0+](https://img.shields.io/badge/PyTorch-2.0%2B-red.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end computer vision and deep learning system for **real-time avocado ripeness level estimation** and **variety classification**, optimized for standalone deployment on **Raspberry Pi 5** with **Dual USB Webcams**.

---

## 🌟 Key Features

- **Dual USB Webcam Support**: Simultaneously reads from two USB webcams to inspect both sides of the avocado with automatic device fallback and simulation mode.
- **Lightweight PyTorch CNN**: Custom CNN architecture (`AvocadoCNN`) optimized for low-latency CPU inference on ARM64 (Raspberry Pi 5 Cortex-A76).
- **Interactive Ripeness Gauge**: Real-time speedometer gauge displaying ripeness percentage (0–100%) and stage (*Unripe*, *Mid-ripe*, *Ripe*).
- **Trainer & Labeler Studio**: Built-in GUI to register new avocado varieties, capture training snapshots directly from the camera, and retrain the CNN on-device.
- **Headless CLI & JSON Streaming**: Run in headless terminal mode on embedded devices, outputting live JSON metrics for automated sorting belts or robotics.
- **Clean Standard Architecture**: Structured into `src/avocado/`, `configs/`, `scripts/`, and `tests/` with YAML configuration.

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
│       │   ├── app.py              # Main Dual-Camera Desktop Inspector GUI
│       │   ├── trainer_gui.py      # Dataset Collector & Model Training Studio
│       │   └── widgets/
│       │       └── gauge.py        # Tkinter Canvas Speedometer Gauge widget
│       └── utils/
│           └── dataset_gen.py      # Synthetic dataset generator
├── scripts/
│   ├── run_app.py                  # Launch desktop Inspection GUI
│   ├── run_trainer.py              # Launch Trainer & Labeler Studio
│   ├── run_cli.py                  # Headless CLI for single/batch/live inspection
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

This script will:
1. Install system packages (`python3-tk`, `libgl1`, `libglib2.0-0`, `v4l-utils`).
2. Add your user to the `video` group for USB camera access.
3. Create a Python virtual environment (`.venv`).
4. Install all dependencies (`torch`, `torchvision`, `opencv-python`, `customtkinter`, `pyyaml`).

---

## 💻 Desktop Setup (Windows / macOS / Linux)

### Using `uv` (Recommended)
```bash
# Create venv and install dependencies
uv venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
uv pip install -e .
```

### Using standard `pip`
```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

pip install -r requirements.txt
pip install -e .
```

---

## 🚀 Running the Application

### Option 1: Interactive Launcher
- **Windows**: Double-click [`run.bat`](file:///C:/P-CCP/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology/run.bat) or run `run.bat` in CMD/PowerShell.
- **Linux / Raspberry Pi 5**: Run `./run.sh`.

### Option 2: Desktop Inspection Dashboard (GUI)
```bash
python scripts/run_app.py
```
- Real-time dual USB camera feeds.
- Live Ripeness Gauge indicator.
- Variety classification and latency metrics.
- One-click snapshot button.

### Option 3: Variety Trainer & Labeler Studio (GUI)
```bash
python scripts/run_trainer.py
```
- Add/delete avocado variety labels (e.g. `Hass`, `Pinkerton`, `Booth 7`).
- Capture training sample images from the USB camera.
- Train the `AvocadoCNN` model on-device in a background thread.

### Option 4: Headless CLI (Raspberry Pi 5 / Automated Sorting)
```bash
# 1. Live stream continuous classification to terminal:
python scripts/run_cli.py --live

# 2. Live stream with JSON output (for integration with robotic arms / PLCs):
python scripts/run_cli.py --live --json

# 3. Classify a single image:
python scripts/run_cli.py --image path/to/avocado.jpg --json

# 4. Batch process a directory of images:
python scripts/run_cli.py --dir path/to/folder/
```

---

## ⚙️ Configuration (`configs/default.yaml`)

You can customize camera indexes, resolution, thresholds, and training parameters in [`configs/default.yaml`](file:///C:/P-CCP/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology/configs/default.yaml):

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

Run the test suite using `pytest` or `unittest`:

```bash
# Run pytest:
pytest

# Or run standard unittest discovery:
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📄 License
This project is open-source under the MIT License.
