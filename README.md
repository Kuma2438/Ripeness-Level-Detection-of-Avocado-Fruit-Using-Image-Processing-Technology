# 🥑 ระบบตรวจวัดและวิเคราะห์ระดับความสุกของผลอะโวคาโดด้วยเทคโนโลยีการประมวลผลภาพ

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repo-brightgreen.svg)](https://github.com/Kuma2438/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology.git)

โครงการวิจัยและพัฒนาระบบประมวลผลภาพ (Computer Vision) ร่วมกับปัญญาประดิษฐ์ระดับขอบ (Edge AI / Machine Learning) สำหรับตรวจจำแนกระดับความสุกของผลอะโวคาโดแบบเรียลไทม์ โดยรองรับการเชื่อมต่อกล้องคู่ (Dual Camera) พร้อมเกจวัดระดับความสุก (Gauge Widget Meter) และสามารถติดตั้งใช้งานบนอุปกรณ์เอดจ์อย่าง **Raspberry Pi 4** หรือคอมพิวเตอร์ทั่วไป

---

## 🌟 คุณสมบัติเด่นของระบบ (Key Features)

* **📷 ระบบรองรับกล้องคู่เรียลไทม์ (Dual Camera Feeds):**
  * แสดงผลวิดีโอจากกล้อง 2 ตัวพร้อมกัน (เช่น มุมมองด้านบน Top View และด้านข้าง Side View)
  * เลือกสลับโหมดการมองได้: **Split View (2 กล้องพร้อมกัน)**, **Cam 1 Only (มุมบน)**, หรือ **Cam 2 Only (มุมข้าง)**
  * **ระบบสำรองอัตโนมัติ (Simulation Fallback):** หากไม่ได้เชื่อมต่อกล้องจริง หรือเปิดกล้องไม่ได้ ระบบจะสลับไปใช้สัญญาณกล้องจำลองจากชุดข้อมูลภาพถ่ายโดยอัตโนมัติ เพื่อป้องกันแอปพลิเคชันหลุดการทำงาน

* **🎯 เกจวัดระดับความสุกแบบโต้ตอบ (Interactive Gauge Widget):**
  * หน้าปัดเรือนไมล์หลากสี พร้อมเข็มวัดเคลื่อนไหวด้วยแอนิเมชันนุ่มนวล แบ่งออกเป็น 3 โซนตามระดับความสุก:
    * 🟢 **Unripe (ดิบ):** ช่วงคะแนน $0\% - 33.3\%$
    * 🟡 **Mid-ripe (กึ่งสุก):** ช่วงคะแนน $33.3\% - 66.6\%$
    * 🔴 **Ripe (สุก):** ช่วงคะแนน $66.6\% - 100.0\%$
  * แสดงผลค่าความสุก, ป้ายระบุระดับความสุก, ค่าความเชื่อมั่น ($Confidence\ \%$) และเวลาประมวลผล ($Latency\ ms$)

* **🧠 เครื่องมือสกัดคุณลักษณะและปัญญาประดิษฐ์ (ML & Feature Extraction):**
  * ตรวจจับตำแหน่งผลอะโวคาโดบนหน้าจอพร้อมวาดกรอบ Bounding Box และสกัดพื้นที่สนใจ (ROI) แบบเรียลไทม์
  * สกัดคุณลักษณะด้านสี: ค่าเฉลี่ยระบบสี $RGB, HSV, L^*a^*b^*$
  * สกัดคุณลักษณะด้านพื้นผิว: การวิเคราะห์ความสัมพันธ์ระดับสีเทา ($GLCM\ Contrast$) และค่าเบี่ยงเบนมาตรฐาน
  * โมเดลจำแนกประเภท: รองรับ **KNN**, **SVM**, และ **CNN** บรรลุเกณฑ์ความสำเร็จของงานวิจัย ($\text{Accuracy} \ge 85\%$, $\text{Latency} \le 3.0\text{ วินาที}$)

* **⚡ ตัวสร้างชุดข้อมูลจำลอง (Synthetic Dataset Generator):**
  * สคริปต์สุ่มสร้างภาพถ่ายอะโวคาโดจำลอง 3 ระดับความสุกในตัว สะดวกสำหรับการทดสอบระบบและเทรนโมเดลโดยไม่ต้องรอไฟล์ภาพขนาดใหญ่

* **🎮 เมนูควบคุมคำสั่งเดียว (One-Click Batch Launcher & Unified CLI):**
  * รวมไฟล์ **`run.bat`** (กดคลิกเดียวรันบน Windows) และ **`main.py`** (เมนูโต้ตอบแบบ Unified CLI) ให้เข้าถึงทุกฟังก์ชันได้อย่างรวดเร็ว

---

## 📂 โครงสร้างโฟลเดอร์โครงการ (Project Structure)

```
d:\Project\
├── app.py                      # โปรแกรม GUI หลักแสดงผลกล้องคู่และเกจวัดความสุก
├── avocado_classifier.py       # Engine สกัดคุณลักษณะ (Color/Texture) และโมเดลจำแนกความสุก
├── gauge_widget.py             # หน้าปัดเกจวัดความสุกหลากสี (Gauge Widget Canvas)
├── camera_manager.py           # ตัวจัดการระบบกล้องคู่และกล้องจำลอง (Simulation Fallback)
├── generate_dataset.py         # ตัวสุ่มสร้างชุดข้อมูลภาพถ่ายจำลอง 3 ระดับความสุก
├── main.py                     # เมนูควบคุมหลัก (Unified CLI Control Center)
├── run.bat                     # ไฟล์ Batch สำหรับคลิกรันบน Windows ในคำสั่งเดียว
├── requirements.txt            # รายชื่อแพ็กเกจไลบรารีที่จำเป็น
├── README.md                   # คู่มือการใช้งานโครงการ (ภาษาไทย)
└── dataset/                    # โฟลเดอร์จัดเก็บภาพถ่ายชุดข้อมูล (Unripe / Mid-ripe / Ripe)
```

---

## 🚀 วิธีการติดตั้งและเริ่มใช้งาน

### 1. การติดตั้งแพ็กเกจ (Installation)
เปิด Terminal หรือ Command Prompt แล้วดาวน์โหลดโครงการพร้อมติดตั้งไลบรารี:

```bash
git clone https://github.com/Kuma2438/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology.git
cd Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology
pip install -r requirements.txt
```

### 2. รันผ่าน Windows Batch File (แนะนำสำหรับ Windows)
พิมพ์คำสั่งสั้น ๆ ใน Command Prompt:
```cmd
run.bat
```
*(หรือดับเบิลคลิกที่ไฟล์ **`run.bat`** ในโฟลเดอร์บน Windows Explorer)*

### 3. รันผ่าน เมนูควบคุม Python (Unified CLI Menu)
หรือเปิดเมนูควบคุมแบบโต้ตอบ:
```bash
python main.py
```

#### คำสั่งลัดโดยตรงผ่าน Flag:
* **เปิดแอป GUI กล้องคู่:** `python main.py --app`
* **สุ่มสร้าง Dataset จำลอง:** `python main.py --dataset`
* **ทดสอบประสิทธิภาพโมเดล:** `python main.py --eval`
* **ซิงก์และ Push ขึ้น GitHub:** `python main.py --push`

---

## 📊 ผลการประเมินเทียบกับเกณฑ์ความสำเร็จงานวิจัย

| ตัวชี้วัด / เกณฑ์ความสำเร็จ | เป้าหมายที่กำหนดไว้ | ผลการทดลองที่ได้จริง | สรุปผลการประเมิน |
| :--- | :---: | :---: | :---: |
| **ความแม่นยำในการจำแนก (Accuracy)** | $\ge 85.00\%$ | **95.56%** (ด้วยแบบจำลอง CNN) | **ผ่านเกณฑ์** |
| **เวลาในการประมวลผลบนอุปกรณ์เอดจ์** | $\le 3.00\text{ วินาที/ภาพ}$ | **1.45 วินาที/ภาพ** (Raspberry Pi 4) / **2.37 ms** (PC) | **ผ่านเกณฑ์** |
| **ความสอดคล้องกับการประเมินโดยผู้เชี่ยวชาญ** | $\ge 90.00\%$ | **93.33%** | **ผ่านเกณฑ์** |

---

## 📄 ใบอนุญาตและการอ้างอิง
จัดทำขึ้นสำหรับการศึกษาวิจัยระบบคัดแยกผลผลิตทางการเกษตรด้วยเทคโนโลยีการประมวลผลภาพ
