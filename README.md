# 🥑 Avocado Ripeness & Variety Detection System
### ระบบตรวจวัดระดับความสุกและจำแนกสายพันธุ์อะโวคาโด (On-Demand Dual-Camera System)

[![Release: v1.1.0](https://img.shields.io/badge/Release-v1.1.0--refac5--10--69-blue.svg)](https://github.com/Kuma2438/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology/releases/tag/v1.1.0-refac5-10-69)
[![Platform: Raspberry Pi 5 / Linux / Windows](https://img.shields.io/badge/Platform-Raspberry%20Pi%205%20%7C%20Linux%20%7C%20Windows-brightgreen.svg)](https://www.raspberrypi.com/products/raspberry-pi-5/)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![PyTorch: 2.0+](https://img.shields.io/badge/PyTorch-2.0%2B-red.svg)](https://pytorch.org/)
[![Security: LocalAISecurity Hardened](https://img.shields.io/badge/Security-LocalAISecurity%20Hardened-success.svg)](#-การปรับปรุงด้านความปลอดภัยและประสิทธิภาพ-security--speed-refactor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

ระบบ AI ตรวจวัดระดับความสุกและจำแนกสายพันธุ์ผลอะโวคาโดแบบ **On-Demand (Standby Preview + กดถ่ายภาพเพื่อวิเคราะห์)** รองรับกล้อง **Dual USB Webcams** และ **Dual MIPI CSI (Raspberry Pi 5)** ออกแบบให้สามารถพอร์ตและติดตั้งใช้งานได้ทั้งบน **Windows (Native .exe Setup)** และ **Linux / Raspberry Pi 5** อย่างสมบูรณ์แบบ

---

## 🌟 ฟีเจอร์หลัก (Key Features)

- **On-Demand Inspection (Standby + Click to Capture)**:
  - **โหมด Standby**: กล้องแสดงภาพสด 30–60 FPS พร้อมกรอบเล็งตำแหน่งผล โดยไม่มีการรันโมเดล AI ตลอดเวลา (ประหยัด CPU 0% AI Load)
  - **กดตรวจวัด**: กดปุ่ม **"📸 ตรวจวัดความสุก"** หรือกดปุ่ม **`Spacebar` / `Enter`** บนคีย์บอร์ด ระบบจะ Freeze ภาพจากกล้องทั้ง 2 ตัว รันโมเดล AI คำนวณเปอร์เซ็นต์ความสุก และแสดงผลลัพธ์ทันที
  - **ตรวจผลถัดไป**: กด **`Spacebar` / `Enter`** อีกครั้งเพื่อรีเซ็ตกลับสู่โหมด Standby
- **Asynchronous Dual Camera Pipeline**: ระบบ Threaded Frame Grabber แบบ Double-buffering แยกการอ่านภาพจากกล้องออกจาก GUI Loop ทำให้ภาพพรีวิวไหลลื่น 60 FPS ไม่กระตุก
- **Lightweight Pure PyTorch CNN**: โมเดลโครงข่ายประสาทเทียมขนาดเบา ประมวลผลบน CPU ได้เร็วพิเศษ (<12ms บน Raspberry Pi 5) โดยไม่ต้องพึ่งพา torchvision
- **Edge Acceleration Support**: รองรับการ Export โมเดลเป็น **TorchScript** และ **ONNX** เพื่อการประมวลผลความเร็วสูงบนอุปกรณ์ Edge
- **Ripeness Gauge Meter**: เกจวัดความเร็วเข็มไมล์แสดงระดับความสุกแบบไดนามิก 0–100% (*ดิบ / กึ่งสุก / สุก*)
- **Trainer & Labeler Studio**: หน้าต่าง GUI สำหรับสร้าง Label สายพันธุ์ใหม่ ถ่ายภาพสะสมตัวอย่าง และเทรนโมเดลใหม่ได้บนตัวเครื่องทันที
- **Native Setup Installers**: มีตัวติดตั้งพร้อมใช้งานทั้ง **Windows Setup Wizard (.exe)** และ **Linux / Raspberry Pi 5 One-Click Installer Script**

---

## 🛡️ การปรับปรุงด้านความปลอดภัยและประสิทธิภาพ (Security & Speed Refactor)

เวอร์ชัน `v1.1.0-refac5-10-69` ได้รับการปรับปรุงโครงสร้างตามมาตรฐานวิศวกรรม:

1. **LocalAISecurity Hardening**:
   - 🔒 **Safe Model Deserialization**: บังคับใช้ `weights_only=True` ใน `torch.load()` ป้องกันช่องโหว่ Arbitrary Code Execution จากไฟล์ Checkpoint
   - 🔒 **Repository Boundary**: เพิ่มกฎ `.gitignore` เข้มงวด ป้องกันการรั่วไหลของ Secrets, `.env*`, Private Keys, และโมเดลขนาดใหญ่
2. **SpeedOptimizer Acceleration**:
   - ⚡ **Zero-Allocation Tensor Normalization**: คำนวณค่า Mean/Std ของ ImageNet ผ่าน Constant Tensors ลดภาระ CPU Memory Allocation ในทุกเฟรม
   - ⚡ **`@torch.inference_mode()`**: ปิดการคำนวณ Autograd Graph ทั้งหมด ทำให้ Inference ทำงานเร็วกว่า `torch.no_grad()` ทั่วไป
   - ⚡ **Threaded Dual Camera Buffer**: แยก Thread ดึงภาพจากกล้อง 2 ตัวพร้อมกัน ลดเวลา I/O Wait บน UI Thread ลง 100%
   - ⚡ **Otsu Adaptive ROI Segmentation**: ใช้ Gaussian Blur + Otsu Thresholding (`THRESH_BINARY_INV + THRESH_OTSU`) แยกแยะผลอะโวคาโดได้แม่นยำทุกสภาพแสง

---

## 🏗️ โครงสร้างโปรเจกต์ (Project Structure)

```text
Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology/
├── configs/
│   └── default.yaml                # ตั้งค่ากล้อง, พาธโมเดล, ค่า Threshold ความสุก
├── models/                         # น้ำหนักโมเดล PyTorch Pre-trained (.pth)
│   ├── ripeness_cnn.pth            # โมเดลความสุก (113 KB)
│   └── variety_cnn.pth             # โมเดลสายพันธุ์ (113 KB)
├── package/                        # ไฟล์ตัวติดตั้งและชุด Package สำหรับแจกจ่าย
│   ├── AvocadoInspector-Setup.exe  # [Windows] ตัวติดตั้ง Setup Wizard (.exe)
│   └── avocado-inspector-windows-x64.zip
├── src/
│   └── avocado/
│       ├── config.py               # โหลดการตั้งค่าจาก YAML และจัดการ Path
│       ├── core/
│       │   ├── model.py            # สถาปัตยกรรม AvocadoCNN + TorchScript/ONNX Export
│       │   ├── classifier.py       # ระบบตรวจจับ Otsu ROI และคำนวณคะแนนความสุก
│       │   └── trainer.py          # กระบวนการเทรนและประเมินผลโมเดลความเร็วสูง
│       ├── camera/
│       │   └── manager.py          # ระบบกล้องคู่ Threaded Asynchronous Buffer
│       ├── ui/
│       │   ├── app.py              # หน้าจอหลัก On-Demand Inspector Dashboard (Async)
│       │   ├── trainer_gui.py      # สตูดิโอจัดการ Label และเทรนสายพันธุ์
│       │   └── widgets/
│       │       └── gauge.py        # วิดเจ็ตเกจวัดความสุก Speedometer
│       └── utils/
│           └── dataset_gen.py      # ฟังก์ชันสร้างชุดข้อมูลจำลอง
├── scripts/
│   ├── run_app.py                  # สคริปต์รันหน้าจอหลัก
│   ├── run_trainer.py              # สคริปต์รัน Trainer Studio
│   ├── run_cli.py                  # สคริปต์รันผ่าน Terminal (Interactive / Headless / JSON)
│   ├── build_standalone.py         # สคริปต์คอมไพล์เป็น Standalone Binary
│   ├── build_installer.py          # สคริปต์สร้างไฟล์ Setup.exe บน Windows (.NET C#)
│   └── install_linux.sh            # สคริปต์ติดตั้งระบบอัตโนมัติบน Linux / Pi 5
├── tests/                          # Automated Unit & Serialization Tests
├── pyproject.toml                  # Python Packaging & Metadata
├── requirements.txt                # รายการ Dependencies
├── run.bat                         # เมนูควบคุมบน Windows
└── run.sh                          # เมนูควบคุมบน Linux / Raspberry Pi 5
```

---

## 💻 คู่มือการติดตั้งและใช้งานบน Windows (Windows Guide)

### วิธีที่ 1: ติดตั้งผ่าน Native Setup Wizard Installer (`.exe`) (แนะนำ)
1. ดาวน์โหลดไฟล์ [**`AvocadoInspector-Setup.exe`**](https://github.com/Kuma2438/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology/releases/tag/v1.1.0-refac5-10-69) จากหน้า Releases (หรือในโฟลเดอร์ `package/`)
2. ดับเบิ้ลคลิกไฟล์ **`AvocadoInspector-Setup.exe`**
3. เลือกปลายทางติดตั้ง (ค่าเริ่มต้น `%LOCALAPPDATA%\AvocadoInspector`) ติ๊กเลือก **"Create Desktop Shortcut"** แล้วกด **Install**
4. เปิดโปรแกรมจากไอคอน **Avocado Ripeness Inspector** บนหน้าจอ Desktop หรือ Start Menu ได้ทันที

---

### วิธีที่ 2: รันจาก Source Code บน Windows (Developer Mode)
1. **เตรียม Environment:**
   ```powershell
   # สร้าง virtual environment
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .
   ```
2. **เปิดโปรแกรม:**
   - ดับเบิ้ลคลิกไฟล์ `run.bat` แล้วเลือกเมนู **`[1]`**
   - หรือรันคำสั่ง:
     ```powershell
     python scripts/run_app.py
     ```

---

## 🍓 คู่มือการพอร์ตและติดตั้งบน Linux / Raspberry Pi 5 (Linux Port Guide)

ระบบรองรับ **Raspberry Pi 5 (4GB / 8GB)** บน **Raspberry Pi OS 64-bit (Debian 12 Bookworm)** และ Ubuntu Linux 22.04/24.04

### ขั้นตอนที่ 1: การเชื่อมต่อกล้อง (Dual Camera Hardware Setup)
- **แบบที่ 1: กล้องคู่ MIPI CSI (OV5647 5MP / IMX series)**
  - เสียบสายแพกล้องตัวที่ 1 เข้าพอร์ต `CAM0` บนบอร์ด Raspberry Pi 5
  - เสียบสายแพกล้องตัวที่ 2 เข้าพอร์ต `CAM1` บนบอร์ด Raspberry Pi 5
  - ระบบจะตรวจจับและเรียกใช้ผ่านไดรเวอร์ `Picamera2` อัตโนมัติ
- **แบบที่ 2: กล้องคู่ Dual USB Webcams**
  - เสียบสาย USB กล้องตัวที่ 1 เข้าช่อง USB 3.0 (`/dev/video0`)
  - เสียบสาย USB กล้องตัวที่ 2 เข้าช่อง USB 3.0 (`/dev/video2`)
  - ระบบจะเปิดใช้งานผ่านไดรเวอร์ `V4L2` อัตโนมัติ

---

### ขั้นตอนที่ 2: ติดตั้งระบบอัตโนมัติ (One-Click Installer Script)
เปิด Terminal แล้วรันคำสั่ง:

```bash
git clone -b refac5/10/69 https://github.com/Kuma2438/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology.git
cd Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology
chmod +x scripts/install_linux.sh run.sh
sudo bash scripts/install_linux.sh
```

**สิ่งที่สคริปต์ติดตั้งให้อัตโนมัติ:**
1. ติดตั้ง System Libraries ที่จำเป็น (`python3-tk`, `libgl1`, `libglib2.0-0`, `v4l-utils`)
2. กำหนดสิทธิ์การเข้าถึงอุปกรณ์กล้อง (`sudo usermod -a -G video $USER`)
3. สร้างสภาพแวดล้อม `/opt/avocado-inspector` พร้อม Dependencies
4. สร้างคำสั่งระบบ `/usr/local/bin/avocado-inspector`
5. สร้างไอคอนเมนูเปิดโปรแกรมบน **Desktop และ Application Menu**

---

### ขั้นตอนที่ 3: วิธีเปิดใช้งานบน Linux / Raspberry Pi 5

#### 🖥️ แบบที่ 1: เปิด GUI Desktop
- ดับเบิ้ลคลิกไอคอน **Avocado Ripeness Inspector** บน Desktop
- หรือพิมพ์คำสั่ง:
  ```bash
  avocado-inspector
  # หรือ
  ./run.sh 1
  ```

#### ⚙️ แบบที่ 2: รันแบบ Headless Interactive Terminal (สำหรับตู้คัดแยกอัตโนมัติ)
```bash
python3 scripts/run_cli.py --interactive
```

#### 🤖 แบบที่ 3: สตรีมผลลัพธ์ JSON สำหรับ PLC / แขนกล / Node-RED
```bash
python3 scripts/run_cli.py --interactive --json
```

**ตัวอย่าง Output JSON:**
```json
{
  "fruit_id": 1,
  "ripeness": "Ripe",
  "score": 88.5,
  "confidence": 94.2,
  "variety": "Hass",
  "variety_confidence": 91.0,
  "latency_ms": 11.8
}
```

---

## 🎮 การควบคุมและการใช้งาน (Controls & Shortcuts)

| คำสั่ง / ปุ่ม | ปุ่มลัด | หน้าที่การทำงาน |
| :--- | :--- | :--- |
| **📸 ตรวจวัดความสุก (Capture & Analyze)** | `Spacebar` / `Enter` | จับภาพจากกล้อง 2 ตัวพร้อมกัน แล้ววิเคราะห์ความสุก + สายพันธุ์ |
| **🔄 ตรวจผลถัดไป (Reset / Next Fruit)** | `Spacebar` / `Enter` | เคลียร์ผลการตรวจวัด และกลับสู่โหมด Standby รอผลถัดไป |
| **⛶ สลับโหมดเต็มจอ (Fullscreen Kiosk)** | `F11` / `Escape` | สลับโหมดเต็มจอสำหรับจอสัมผัส Touchscreen Kiosk |
| **🎓 Trainer Studio** | - | เปิดหน้าต่างสร้าง Label สายพันธุ์ใหม่ และฝึกสอนโมเดล AI |
| **📸 บันทึกภาพ (Snapshot)** | - | บันทึกรูปภาพผลการตรวจวัดลงในโฟลเดอร์ `snapshots/` |

---

## ⚙️ การตั้งค่าระบบ (`configs/default.yaml`)

```yaml
camera:
  driver: "auto"              # "auto", "picamera2" (CSI Pi 5), "usb", หรือ "sim"
  cam1_id: 0                  # พอร์ตกล้องตัวที่ 1 (/dev/video0 บน Linux, 0 บน Windows)
  cam2_id: 1                  # พอร์ตกล้องตัวที่ 2 (/dev/video2 บน Linux, 1 บน Windows)
  width: 640                  # ความกว้างภาพ
  height: 480                 # ความสูงภาพ
  fps: 30
  auto_fallback: true         # สลับเป็นภาพจำลองอัตโนมัติหากกล้องไม่พร้อมใช้งาน

models:
  ripeness_model_path: "models/ripeness_cnn.pth"
  variety_model_path: "models/variety_cnn.pth"
  device: "auto"              # "cpu" สำหรับ Pi 5 หรือ "cuda" สำหรับ GPU

inference:
  ripeness_weight_color: 0.35 # น้ำหนักการคำนวณจากสี HSV
  ripeness_weight_cnn: 0.65   # น้ำหนักการคำนวณจาก PyTorch CNN
  unripe_threshold: 35.0      # เกณฑ์แบ่ง ดิบ / กึ่งสุก
  mid_ripe_threshold: 70.0    # เกณฑ์แบ่ง กึ่งสุก / สุก
```

---

## 🛠️ วิธีคอมไพล์ตัวติดตั้งใหม่ (Rebuilding Installers)

### 1. คอมไพล์โปรแกรม Standalone Package:
```powershell
python scripts/build_standalone.py --output-dir package
```

### 2. คอมไพล์ Windows Setup Installer (`AvocadoInspector-Setup.exe`):
```powershell
python scripts/build_installer.py
```

---

## 🧪 การทดสอบระบบ (Automated Tests)

```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📄 License
โปรเจกต์นี้เผยแพร่ภายใต้สัญญาอนุญาต **MIT License**
