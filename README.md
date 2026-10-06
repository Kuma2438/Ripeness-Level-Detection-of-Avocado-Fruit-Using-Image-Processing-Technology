# 🥑 Avocado Ripeness & Variety Detection System
### ระบบตรวจวัดระดับความสุกและจำแนกสายพันธุ์อะโวคาโด (On-Demand Dual-Camera System)

[![Platform: Raspberry Pi 5 / Linux / Windows](https://img.shields.io/badge/Platform-Raspberry%20Pi%205%20%7C%20Linux%20%7C%20Windows-blue.svg)](https://www.raspberrypi.com/products/raspberry-pi-5/)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![PyTorch: 2.0+](https://img.shields.io/badge/PyTorch-2.0%2B-red.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

ระบบ AI ตรวจวัดระดับความสุกและจำแนกสายพันธุ์ผลอะโวคาโดแบบ **On-Demand (Standby Preview + กดถ่ายภาพเพื่อวิเคราะห์)** รองรับกล้อง **Dual USB Webcams** ออกแบบให้สามารถพอร์ตและติดตั้งใช้งานได้ทั้งบน **Windows** และ **Linux / Raspberry Pi 5** อย่างสมบูรณ์แบบ

---

## 🌟 ฟีเจอร์หลัก (Key Features)

- **On-Demand Inspection (Standby + Click to Capture)**:
  - **โหมด Standby**: กล้องแสดงภาพสด 30 FPS พร้อมกรอบเล็งตำแหน่งผล โดย**ไม่มีการรันโมเดล AI ตลอดเวลา** (ประหยัด CPU 0% AI Load)
  - **กดตรวจวัด**: กดปุ่ม **"📸 ตรวจวัดความสุก"** หรือกดปุ่ม **`Spacebar` / `Enter`** บนคีย์บอร์ด ระบบจะ Freeze ภาพจากกล้องทั้ง 2 ตัว รันโมเดล AI คำนวณเปอร์เซ็นต์ความสุก และแสดงผลลัพธ์ทันที
  - **ตรวจผลถัดไป**: กด **`Spacebar` / `Enter`** อีกครั้งเพื่อรีเซ็ตกลับสู่โหมด Standby
- **Dual USB Webcams**: เชื่อมต่อกล้อง USB 2 ตัวพร้อมกันเพื่อตรวจผลอะโวคาโดจาก 2 ฝั่ง (หน้า-หลัง) พร้อมระบบจำลองภาพอัตโนมัติหากไม่ได้ต่อกล้อง
- **Lightweight Pure PyTorch CNN**: โมเดลโครงข่ายประสาทเทียมขนาดเบา ประมวลผลบน CPU ได้เร็วพิเศษ (<15ms บน Raspberry Pi 5) โดยไม่ต้องพึ่งพา torchvision
- **Ripeness Gauge Meter**: เกจวัดความเร็วเข็มไมล์แสดงระดับความสุกแบบไดนามิก 0–100% (*ดิบ / กึ่งสุก / สุก*)
- **Trainer & Labeler Studio**: หน้าต่าง GUI สำหรับสร้าง Label สายพันธุ์ใหม่ ถ่ายภาพสะสมตัวอย่าง และเทรนโมเดลใหม่ได้บนตัวเครื่องทันที
- **Native Setup Installers**: มีตัวติดตั้งพร้อมใช้งานทั้ง Setup Wizard บน Windows และ Script ติดตั้งระบบ Desktop บน Linux / Raspberry Pi 5

---

## 🏗️ โครงสร้างโปรเจกต์ (Project Structure)

```
Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology/
├── configs/
│   └── default.yaml                # ตั้งค่ากล้อง, พาธโมเดล, ค่า Threshold ความสุก
├── dataset/                        # ชุดข้อมูลภาพฝึกสอนโมเดล (Unripe, Mid-ripe, Ripe)
│   └── varieties/                  # โฟลเดอร์เก็บสายพันธุ์ (Hass, Pinkerton, Booth 7 ฯลฯ)
├── installer/
│   └── setup.iss                   # สคริปต์คอมไพล์ Inno Setup
├── models/                         # น้ำหนักโมเดล PyTorch Pre-trained (.pth)
│   ├── ripeness_cnn.pth
│   └── variety_cnn.pth
├── package/                        # ไฟล์ตัวติดตั้งและไฟล์ Binary ที่พร้อมแจกจ่าย
│   ├── AvocadoInspector-Setup.exe  # [Windows] ตัวติดตั้ง Setup Wizard
│   ├── avocado-inspector/          # [Windows] โฟลเดอร์ Portable รันได้ทันที
│   └── avocado-inspector-windows-x64.zip
├── src/
│   └── avocado/
│       ├── config.py               # โหลดการตั้งค่าจาก YAML และจัดการ Path
│       ├── core/
│       │   ├── model.py            # สถาปัตยกรรม AvocadoCNN
│       │   ├── classifier.py       # ระบบตรวจจับ ROI และคำนวณคะแนนความสุก
│       │   └── trainer.py          # กระบวนการเทรนและประเมินผลโมเดล
│       ├── camera/
│       │   └── manager.py          # ระบบจัดการกล้อง Dual USB (V4L2 / DirectShow)
│       ├── ui/
│       │   ├── app.py              # หน้าจอหลัก On-Demand Inspector Dashboard
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
│   ├── build_installer.py          # สคริปต์สร้างไฟล์ Setup.exe บน Windows
│   └── install_linux.sh            # สคริปต์ติดตั้งระบบอัตโนมัติบน Linux / Pi 5
├── tests/                          # Automated Unit & Integration Tests
├── pyproject.toml                  # Python Packaging & Metadata
├── requirements.txt                # รายการ Dependencies
├── run.bat                         # เมนูควบคุมบน Windows
└── run.sh                          # เมนูควบคุมบน Linux / Raspberry Pi 5
```

---

## 💻 คู่มือการติดตั้งและใช้งานบน Windows (Windows Guide)

### วิธีที่ 1: ติดตั้งผ่าน Setup Wizard Installer (แนะนำสำหรับผู้ใช้งานทั่วไป)
1. เข้าไปที่โฟลเดอร์ [`package/`](file:///C:/P-CCP/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology/package)
2. ดับเบิ้ลคลิกไฟล์ [**`AvocadoInspector-Setup.exe`**](file:///C:/P-CCP/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology/package/AvocadoInspector-Setup.exe)
3. เลือกโฟลเดอร์ที่ต้องการติดตั้ง ติ๊กเลือก **"Create a Desktop shortcut"** แล้วกด **Install**
4. เปิดโปรแกรมจากไอคอน **Avocado Ripeness Inspector** บนหน้าจอ Desktop ได้ทันที (ไม่ต้องติดตั้ง Python หรือไลบรารีใดๆ)

---

### วิธีที่ 2: รันจาก Source Code / พัฒนาต่อ (Developer Mode)
1. **เตรียม Environment:**
   ```powershell
   # ติดตั้ง uv (แนะนำ) หรือใช้ python venv ปกติ
   uv venv .venv
   .venv\Scripts\activate
   uv pip install -r requirements.txt
   uv pip install -e .
   ```
2. **เปิดโปรแกรม:**
   - ดับเบิ้ลคลิกไฟล์ [`run.bat`](file:///C:/P-CCP/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology/run.bat) แล้วเลือกเมนู **`[1]`**
   - หรือรันคำสั่ง:
     ```powershell
     python scripts/run_app.py
     ```

---

## 🍓 คู่มือการพอร์ตและติดตั้งบน Linux / Raspberry Pi 5 (Linux / Pi 5 Guide)

ระบบนี้รองรับ **Raspberry Pi 5 (4GB / 8GB)** ที่ใช้ระบบปฏิบัติการ **Raspberry Pi OS 64-bit (Debian 12 Bookworm)** หรือ Ubuntu Linux

### ขั้นตอนที่ 1: การเชื่อมต่อกล้อง (Dual Camera Hardware Setup)
ระบบรองรับกล้องคู่ได้ 2 รูปแบบอย่างยืดหยุ่น:
- **แบบที่ 1: กล้องคู่ MIPI CSI บน Raspberry Pi 5 (แนะนำสำหรับกล้อง OV5647 5MP / IMX series)**
  - เสียบสายแพกล้อง **OV5647 ตัวที่ 1** เข้าที่พอร์ต `CAM0` บนบอร์ด Raspberry Pi 5
  - เสียบสายแพกล้อง **OV5647 ตัวที่ 2** เข้าที่พอร์ต `CAM1` บนบอร์ด Raspberry Pi 5
  - ระบบจะตรวจจับและเปิดใช้งานผ่านไดรเวอร์ `Picamera2` อัตโนมัติ
- **แบบที่ 2: กล้องคู่ Dual USB Webcams**
  - เสียบสาย USB กล้องตัวที่ 1 เข้าช่อง USB 3.0 (`/dev/video0`)
  - เสียบสาย USB กล้องตัวที่ 2 เข้าช่อง USB 3.0 (`/dev/video2`)
  - ระบบจะเปิดใช้งานผ่านไดรเวอร์ `V4L2` อัตโนมัติ (และรองรับการสลับกล้องรุ่นอื่นในอนาคตได้อย่างอิสระ)

### ขั้นตอนที่ 2: รันสคริปต์ติดตั้งแบบอัตโนมัติ (One-Click Installer)
เปิด Terminal บน Raspberry Pi 5 แล้วรันคำสั่ง:

```bash
cd Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology
chmod +x scripts/install_linux.sh run.sh
sudo bash scripts/install_linux.sh
```

**สิ่งที่สคริปต์จะทำให้โดยอัตโนมัติ:**
1. ติดตั้งไลบรารีของระบบที่จำเป็น (`python3-tk`, `libgl1`, `libglib2.0-0`, `v4l-utils`)
2. กำหนดสิทธิ์การเข้าถึงกล้อง USB Video โดยไม่ต้องใช้ root (`sudo usermod -a -G video $USER`)
3. ติดตั้งโปรแกรมไปที่ไดเรกทอรี `/opt/avocado-inspector` พร้อม Python Virtual Environment
4. สร้างคำสั่งระบบ `/usr/local/bin/avocado-inspector`
5. สร้างไอคอนเมนูเปิดโปรแกรมบน **Desktop และ Applications Menu** ของ Raspberry Pi

---

### ขั้นตอนที่ 3: วิธีเปิดใช้งานบน Raspberry Pi 5

#### 🖥️ แบบที่ 1: เปิดหน้าต่าง GUI Desktop
- ดับเบิ้ลคลิกไอคอน **Avocado Ripeness Inspector** บน Desktop
- หรือพิมพ์คำสั่งใน Terminal:
  ```bash
  avocado-inspector
  # หรือ
  ./run.sh 1
  ```

#### ⚙️ แบบที่ 2: รันแบบ Headless Interactive Terminal (ไม่ต้องต่อจอภาพ)
หากนำไปประกอบตู้คัดแยกหรือเครื่องจักร สามารถรันในโหมด Command Line ได้:
```bash
python3 scripts/run_cli.py --interactive
```
*ระบบจะรอให้ผู้ใช้กด `Enter` เมื่อวางผลอะโวคาโด แล้ววิเคราะห์แสดงผลความสุกทันที*

#### 🤖 แบบที่ 3: ส่งข้อมูล JSON เข้าแขนกล / PLC / Node-RED
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
  "latency_ms": 12.4
}
```

---

## 🎮 การควบคุมและการใช้งาน (Controls & Shortcuts)

| คำสั่ง / ปุ่ม | ปุ่มลัด | หน้าที่การทำงาน |
| :--- | :--- | :--- |
| **📸 ตรวจวัดความสุก (Capture & Analyze)** | `Spacebar` / `Enter` | จับภาพจากกล้องทั้ง 2 ตัวพร้อมกัน แล้ววิเคราะห์ความสุก + สายพันธุ์ |
| **🔄 ตรวจผลถัดไป (Reset / Next Fruit)** | `Spacebar` / `Enter` | เคลียร์ผลการตรวจวัด และกลับสู่โหมด Standby รอผลถัดไป |
| **🎓 Trainer Studio** | - | เปิดหน้าต่างสร้าง Label สายพันธุ์ใหม่ และฝึกสอนโมเดล AI |
| **📸 บันทึกภาพ (Snapshot)** | - | บันทึกรูปภาพผลการตรวจวัดลงในโฟลเดอร์ `snapshots/` |

---

## ⚙️ การตั้งค่าระบบ (`configs/default.yaml`)

สามารถปรับแต่งพอร์ตกล้อง ความละเอียด และเกณฑ์ตัดสินความสุกได้ที่ไฟล์ [`configs/default.yaml`](file:///C:/P-CCP/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology/configs/default.yaml):

```yaml
camera:
  cam1_id: 0                  # พอร์ตกล้องตัวที่ 1 (/dev/video0 บน Linux, 0 บน Windows)
  cam2_id: 1                  # พอร์ตกล้องตัวที่ 2 (/dev/video2 บน Linux, 1 บน Windows)
  width: 640                  # ความกว้างภาพ
  height: 480                 # ความสูงภาพ
  fps: 30
  auto_fallback: true         # สลับเป็นภาพจำลองอัตโนมัติหากกล้องไม่พร้อมใช้งาน

models:
  ripeness_model_path: "models/ripeness_cnn.pth"
  variety_model_path: "models/variety_cnn.pth"
  device: "auto"              # "cpu" สำหรับ Pi 5 หรือ "cuda" สำหรับ PC ที่มีการ์ดจอ

inference:
  ripeness_weight_color: 0.35 # น้ำหนักการคำนวณจากสี HSV
  ripeness_weight_cnn: 0.65   # น้ำหนักการคำนวณจาก PyTorch CNN
  unripe_threshold: 35.0      # เกณฑ์แบ่ง ดิบ / กึ่งสุก
  mid_ripe_threshold: 70.0    # เกณฑ์แบ่ง กึ่งสุก / สุก
```

---

## 🛠️ วิธีคอมไพล์ตัวติดตั้งใหม่ (Rebuilding Installers)

### 1. คอมไพล์โปรแกรม Standalone (`package/avocado-inspector/`):
```bash
python scripts/build_standalone.py --output-dir package
```

### 2. คอมไพล์ไฟล์ Windows Setup Wizard Installer (`package/AvocadoInspector-Setup.exe`):
```bash
python scripts/build_installer.py
```

---

## 🧪 การทดสอบระบบ (Automated Tests)

รันชุดทดสอบความถูกต้องของโมเดล กล้อง และหน้าต่าง UI:
```bash
python -m unittest discover -s tests -p "test_*.py"
# หรือ
pytest
```

---

## 📄 License
โปรเจกต์นี้เผยแพร่ภายใต้สัญญาอนุญาต **MIT License**
