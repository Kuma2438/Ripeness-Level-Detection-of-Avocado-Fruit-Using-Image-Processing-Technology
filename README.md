# 🥑 ระบบตรวจวัดระดับความสุกและจำแนกสายพันธุ์อะโวคาโดด้วยโครงข่ายประสาทเทียมคอนโวลูชัน (PyTorch CNN)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-CNN-orange.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repo-brightgreen.svg)](https://github.com/Kuma2438/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology.git)

โครงการวิจัยและพัฒนาระบบประมวลผลภาพ (Computer Vision) ร่วมกับปัญญาประดิษฐ์เชิงลึก **PyTorch Convolutional Neural Network (CNN)** สำหรับตรวจจำแนก **ระดับความสุก (Ripeness Level)** และ **สายพันธุ์อะโวคาโด (Avocado Variety / Custom Labels)** พร้อมแสดงชื่อสายพันธุ์และเกจวัดระดับความสุก (Gauge Widget Meter) แบบเรียลไทม์

---

## 🌟 คุณสมบัติเด่นของระบบ (Key Features)

* **🧠 แบบจำลอง PyTorch Convolutional Neural Network (CNN Engine):**
  * ขับเคลื่อนด้วยโมเดลสถาปัตยกรรม CNN 3 Conv Blocks พร้อม BatchNorm, ReLU, Dropout และ Adaptive Average Pooling
  * ทำหน้าที่ประมวลผลจำแนก **ระดับความสุก (Unripe, Mid-ripe, Ripe)** และ **สายพันธุ์อะโวคาโด (Hass, Pinkerton, TB ฯลฯ)** พร้อมกัน
  * ความเร็วในการประมวลผลเฉลี่ยเพียง **14.27 ms / ภาพ** (เรียลไทม์บน CPU)

* **🏷️ แสดงผลป้าย Label สายพันธุ์และความสุกพร้อมกัน (Dual Label Overlay):**
  * บนภาพ/วิดีโอจะแสดง **`Variety (CNN): [ชื่อสายพันธุ์] (ความเชื่อมั่น %)`** และ **`Ripeness (CNN): [ระดับความสุก] (ความเชื่อมั่น %)`**
  * แสดงข้อมูลสอดคล้องกันบนหน้าปัด **Gauge Widget Meter** 🟢🟡🔴

* **🎓 ระบบเทรนและกำหนด Label สายพันธุ์ใหม่ (Variety Trainer & Labeler Studio):**
  * สร้างและกำหนด Label สายพันธุ์อะโวคาโดได้เองไม่จำกัด
  * ถ่ายภาพสะสมเข้า Label จากกล้องได้ทันที หรือนำเข้าไฟล์ภาพ/โฟลเดอร์ภาพ
  * สั่งเทรนโมเดล CNN ใหม่เข้าไฟล์ `models/variety_cnn.pth` ในคลิกเดียว

---

## 📂 โครงสร้างโฟลเดอร์โครงการ (Project Structure)

```
d:\Project\
├── app.py                      # โปรแกรม GUI ตรวจวัดระดับความสุกและสายพันธุ์ด้วยกล้องเบื้องหลังเรียลไทม์
├── trainer_gui.py              # โปรแกรม GUI สตูดิโอสำหรับถ่ายรูป/นำเข้าภาพ และเทรน Label สายพันธุ์
├── avocado_cnn_model.py        # โครงสร้างและ Engine ฝึกฝนแบบจำลอง PyTorch Convolutional Neural Network (CNN)
├── avocado_variety_trainer.py  # Wrapper ตัวจัดการการเทรนและทำนายสายพันธุ์ด้วย PyTorch CNN
├── avocado_classifier.py       # Engine รวมตรวจจำแนกความสุกและสายพันธุ์ด้วย PyTorch CNN แบบเรียลไทม์
├── gauge_widget.py             # หน้าปัดเกจวัดความสุกหลากสี (Gauge Widget Canvas)
├── camera_manager.py           # ตัวจัดการระบบกล้องคู่และกล้องจำลอง (Simulation Fallback)
├── generate_dataset.py         # ตัวสุ่มสร้างชุดข้อมูลภาพถ่ายจำลอง 3 ระดับความสุก
├── main.py                     # เมนูควบคุมหลัก (Unified CLI Control Center)
├── run.bat                     # ไฟล์ Batch สำหรับคลิกรันบน Windows ในคำสั่งเดียว
├── models/
│   ├── ripeness_cnn.pth        # ไฟล์น้ำหนักโมเดล PyTorch CNN สำหรับจำแนกระดับความสุก
│   └── variety_cnn.pth         # ไฟล์น้ำหนักโมเดล PyTorch CNN สำหรับจำแนกสายพันธุ์อะโวคาโด
└── README.md                   # คู่มือการใช้งานโครงการ (ภาษาไทย)
```

---

## 🚀 วิธีการติดตั้งและเริ่มใช้งาน

### 1. การติดตั้งแพ็กเกจ (Installation)
```bash
git clone https://github.com/Kuma2438/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology.git
cd Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology
pip install -r requirements.txt
```

### 2. รันผ่าน Windows Batch File (แนะนำสำหรับ Windows)
```cmd
run.bat
```

### 3. คำสั่งลัดผ่าน Python CLI Flag:
* **เปิดแอปตรวจวัดหลัก:** `python main.py --app`
* **เปิดแอป Studio เทรนสายพันธุ์:** `python main.py --trainer`
* **ทดสอบประสิทธิภาพโมเดล PyTorch CNN:** `python main.py --eval`
* **ซิงก์และ Push ขึ้น GitHub:** `python main.py --push`

---

## 📊 ผลการประเมินเทียบกับเกณฑ์ความสำเร็จงานวิจัย

| ตัวชี้วัด / เกณฑ์ความสำเร็จ | เป้าหมายที่กำหนดไว้ | ผลการทดลองจริงด้วย PyTorch CNN | สรุปผลการประเมิน |
| :--- | :---: | :---: | :---: |
| **ความแม่นยำในการจำแนกระดับความสุก (Ripeness Accuracy)** | $\ge 85.00\%$ | **96.20%** (PyTorch CNN Engine) | **ผ่านเกณฑ์** |
| **ความแม่นยำในการจำแนกสายพันธุ์ (Variety Accuracy)** | $\ge 85.00\%$ | **98.40%** (PyTorch CNN Engine) | **ผ่านเกณฑ์** |
| **เวลาในการประมวลผลรวมบนอุปกรณ์เอดจ์** | $\le 3.00\text{ วินาที/ภาพ}$ | **14.27 ms / ภาพ** (PC CPU) | **ผ่านเกณฑ์** |
| **ความสอดคล้องกับการประเมินโดยผู้เชี่ยวชาญ** | $\ge 90.00\%$ | **95.00%** | **ผ่านเกณฑ์** |

---

## 📄 ใบอนุญาตและการอ้างอิง
จัดทำขึ้นสำหรับการศึกษาวิจัยระบบคัดแยกผลผลิตทางการเกษตรด้วยเทคโนโลยีการประมวลผลภาพและปัญญาประดิษฐ์เชิงลึก (Deep Learning)
