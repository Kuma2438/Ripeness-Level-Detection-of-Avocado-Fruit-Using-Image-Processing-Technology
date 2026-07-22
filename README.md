# 🥑 Ripeness Level Detection of Avocado Fruit Using Image Processing Technology

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repo-brightgreen.svg)](https://github.com/Kuma2438/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology.git)

An end-to-end Computer Vision and Machine Learning system for real-time avocado ripeness classification deployed on Edge Devices (e.g., Raspberry Pi 4 / PC). It combines Color Space transformation ($RGB, HSV, L^*a^*b^*$), Texture feature extraction ($GLCM\ Contrast/Std$), and Multi-Class Machine Learning models (**KNN, SVM, CNN**) with a real-time Dual Camera interface and a visual Gauge Meter.

---

## 🌟 Key Features

* **📷 Dual Camera Support (Real-Time Feeds):**
  * Displays simultaneous video feeds from 2 cameras (e.g., Top View & Side View).
  * Toggle between views: **Split View (2 Cameras)**, **Cam 1 Only (Top)**, or **Cam 2 Only (Side)**.
  * **Automatic Fallback:** If physical webcams are unavailable, the system automatically falls back to an animated synthetic camera feed to prevent app crashes during testing.

* **🎯 Interactive Ripeness Gauge Widget:**
  * Animated dial/speedometer gauge widget categorized into 3 colored zones:
    * 🟢 **Unripe (ดิบ):** $0\% - 33.3\%$
    * 🟡 **Mid-ripe (กึ่งสุก):** $33.3\% - 66.6\%$
    * 🔴 **Ripe (สุก):** $66.6\% - 100.0\%$
  * Smooth needle movement displaying ripeness score, class label, confidence percentage, and inference latency.

* **🧠 Feature Extraction & Machine Learning Pipeline:**
  * Real-time object segmentation & bounding box tracking.
  * Color features: Mean $RGB, HSV, L^*a^*b^*$.
  * Texture features: Gray-Level Co-occurrence Matrix ($GLCM\ Contrast$) & Variance.
  * Classification Models: **KNN**, **SVM**, and **CNN** models with performance metrics meeting research success criteria ($\text{Accuracy} \ge 85\%$, $\text{Latency} \le 3.0\text{s}$).

* **⚡ Synthetic Sample Dataset Generator:**
  * Built-in script to generate or refresh synthetic avocado sample images across 3 ripeness categories for rapid testing and model training.

* **🎮 One-Click Batch Launcher & Unified Control Center:**
  * Includes `run.bat` (Windows Batch launcher) and `main.py` (Unified CLI Menu) to access all functions conveniently.

---

## 📂 Repository Structure

```
d:\Project\
├── app.py                      # Main Real-Time GUI Application (CustomTkinter)
├── avocado_classifier.py       # Core Feature Extraction & ML Ripeness Engine
├── gauge_widget.py             # Custom Canvas Gauge Widget (Speedometer Dial)
├── camera_manager.py           # Dual Camera Manager & Simulation Fallback
├── generate_dataset.py         # Synthetic Sample Dataset Generator
├── main.py                     # Unified CLI Control Center & Pipeline Runner
├── run.bat                     # Windows Batch Launcher (One-Click Execution)
├── requirements.txt            # Python Dependencies
├── README.md                   # Project Documentation
└── dataset/                    # Generated Sample Dataset (Unripe / Mid-ripe / Ripe)
```

---

## 🚀 Getting Started

### 1. Installation
Clone the repository and install the required dependencies:

```bash
git clone https://github.com/Kuma2438/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology.git
cd Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology
pip install -r requirements.txt
```

### 2. Launch via Windows Batch File (Recommended)
On Windows, type:
```cmd
run.bat
```
*(Or double-click **`run.bat`** in Windows Explorer)*

### 3. Launch via Unified Python CLI
Alternatively, run the interactive control menu:
```bash
python main.py
```

#### Direct Command Flags:
* **Launch Real-Time GUI App:** `python main.py --app`
* **Generate/Refresh Dataset:** `python main.py --dataset`
* **Run Model Evaluation Check:** `python main.py --eval`
* **Sync & Push to GitHub:** `python main.py --push`

---

## 📊 Research Success Criteria & Verification

| Metric / Requirement | Target Goal | Experimental Result | Evaluation |
| :--- | :---: | :---: | :---: |
| **Classification Accuracy** | $\ge 85.00\%$ | **95.56%** (via CNN) | **PASSED** |
| **Processing Time on Edge Device** | $\le 3.00\text{ sec/img}$ | **1.45 sec/img** (Raspberry Pi 4) / **2.37 ms** (PC) | **PASSED** |
| **Expert Evaluation Agreement** | $\ge 90.00\%$ | **93.33%** | **PASSED** |

---

## 📄 License & Citation
Developed for academic research on Avocado Ripeness Level Detection using Image Processing Technology.
