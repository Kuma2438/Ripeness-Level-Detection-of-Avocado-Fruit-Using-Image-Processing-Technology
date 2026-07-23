# 🥑 ระบบตรวจวัดระดับความสุกและจำแนกสายพันธุ์อะโวคาโดด้วยเทคโนโลยีการประมวลผลภาพ

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repo-brightgreen.svg)](https://github.com/Kuma2438/Ripeness-Level-Detection-of-Avocado-Fruit-Using-Image-Processing-Technology.git)

โครงการวิจัยและพัฒนาระบบประมวลผลภาพ (Computer Vision) ร่วมกับปัญญาประดิษฐ์ระดับขอบ (Edge AI / Machine Learning) สำหรับตรวจจำแนก **ระดับความสุก (Ripeness Level)** และ **สายพันธุ์อะโวคาโด (Avocado Variety / Custom Labels)** แบบเรียลไทม์ โดยรองรับการเชื่อมต่อกล้องคู่ (Dual Camera) พร้อมเกจวัดระดับความสุก (Gauge Widget Meter) และ **โปรแกรม Trainer Studio สำหรับสร้าง Label และเทรนสายพันธุ์ใหม่ได้ด้วยตนเอง**

---

## 🌟 คุณสมบัติเด่นของระบบ (Key Features)

* **🎓 ระบบเทรนและกำหนด Label สายพันธุ์ใหม่ (Variety Trainer & Labeler Studio):**
  * สร้างและกำหนด Label สายพันธุ์อะโวคาโดได้เองไม่จำกัด (เช่น **Hass**, **Booth 7**, **Pinkerton**, **Reed** หรือสายพันธุ์ตามที่ผู้ใช้กำหนด)
  * ถ่ายภาพตัวอย่างสะสมเข้า Label จากกล้องได้ทันทีแบบเรียลไทม์ หรือนำเข้าไฟล์ภาพ/โฟลเดอร์ภาพ
  * กดปุ่มเทรนโมเดลจำแนกสายพันธุ์ (Machine Learning Engine) ในคลิกเดียว
  * บันทึกน้ำหนักและพารามิเตอร์โมเดลเข้าไฟล์ `variety_model.pkl` อัตโนมัติ

* **📷 ระบบตรวจจับกล้องคู่เรียลไทม์ (Dual Camera Feeds):**
  * แสดงผลวิดีโอจากกล้อง 2 ตัวพร้อมกัน (มุมมองด้านบน Top View และด้านข้าง Side View)
  * แสดงผลป้ายระบุสายพันธุ์ (**Variety Badge**) และระดับความสุก (**Ripeness Badge**) บนกรอบ Bounding Box พร้อมกัน
  * **ระบบสำรองอัตโนมัติ (Simulation Fallback):** สลับไปใช้กล้องจำลองอัตโนมัติหากไม่ได้ต่อกล้องจริง

* **🎯 เกจวัดระดับความสุกแบบโต้ตอบ (Interactive Gauge Widget):**
  * หน้าปัดเรือนไมล์หลากสี 3 โซน (🟢 **Unripe ดิบ**, 🟡 **Mid-ripe กึ่งสุก**, 🔴 **Ripe สุก**)
  * เข็มวัดเคลื่อนไหวด้วยแอนิเมชันนุ่มนวล พร้อมแสดงค่าความเชื่อมั่น ($Confidence\ \%$) และเวลาประมวลผล ($Latency\ ms$)

* **🧠 เครื่องมือสกัดคุณลักษณะหลากมิติ (Multi-Feature Extraction):**
  * สกัดคุณลักษณะด้านสี: ค่าเฉลี่ยระบบสี $RGB, HSV, L^*a^*b^*$
  * สกัดคุณลักษณะด้านพื้นผิว: การวิเคราะห์ความสัมพันธ์ระดับสีเทา ($GLCM\ Contrast$) และค่าเบี่ยงเบนมาตรฐาน
  * สกัดคุณลักษณะด้านรูปทรง: อัตราส่วนความกว้างต่อความสูง (Aspect Ratio), ความกลม (Roundness), และ Extent

---

## 📂 โครงสร้างโฟลเดอร์โครงการ (Project Structure)

```
d:\Project\
├── app.py                      # โปรแกรม GUI หลักแสดงผลกล้องคู่ เกจวัดความสุก และสายพันธุ์
├── trainer_gui.py              # โปรแกรม GUI สตูดิโอสำหรับถ่ายรูป/นำเข้าภาพ และเทรน Label สายพันธุ์
├── avocado_variety_trainer.py  # Engine ฝึกฝนโมเดลจำแนกสายพันธุ์อะโวคาโด (Variety Classifier)
├── avocado_classifier.py       # Engine รวมสำหรับตรวจจำแนกความสุกและสายพันธุ์แบบเรียลไทม์
├── gauge_widget.py             # หน้าปัดเกจวัดความสุกหลากสี (Gauge Widget Canvas)
├── camera_manager.py           # ตัวจัดการระบบกล้องคู่และกล้องจำลอง (Simulation Fallback)
├── generate_dataset.py         # ตัวสุ่มสร้างชุดข้อมูลภาพถ่ายจำลอง 3 ระดับความสุก
├── main.py                     # เมนูควบคุมหลัก (Unified CLI Control Center)
├── run.bat                     # ไฟล์ Batch สำหรับคลิกรันบน Windows ในคำสั่งเดียว
├── variety_model.pkl           # ไฟล์โมเดลสายพันธุ์อะโวคาโดที่ผ่านการเทรนแล้ว
├── dataset/
│   ├── varieties/              # โฟลเดอร์จัดเก็บภาพตัวอย่างสายพันธุ์ (Hass, Booth 7, Pinkerton, Reed...)
│   └── (unripe/mid_ripe/ripe)  # โฟลเดอร์จัดเก็บภาพชุดข้อมูลระดับความสุก
└── README.md                   # คู่มือการใช้งานโครงการ (ภาษาไทย)
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

### 3. วิธีการเทรนและกำหนด Label สายพันธุ์ใหม่ (Variety Training & Labeling)
1. เปิดเมนูควบคุม `run.bat` แล้วเลือกข้อ **`[2] Open Variety Trainer & Labeler Studio`** (หรือรัน `python trainer_gui.py`)
2. พิมพ์ชื่อสายพันธุ์ใหม่ในช่อง (เช่น `Hass`, `Booth 7`, `Pinkerton`, `Reed`) แล้วกด **"➕ เพิ่ม"**
3. เลือก Label สายพันธุ์ที่ต้องการ จากนั้นกด **"📸 ถ่ายภาพเข้า Label"** หรือ **"📁 นำเข้าไฟล์ภาพ"** เพื่อสะสมตัวอย่างภาพ
4. กดปุ่ม **"⚡ เริ่มเทรนโมเดลสายพันธุ์ (Start Training)"** ระบบจะสร้างไฟล์ `variety_model.pkl`
5. เมื่อเปิดแอปพลิเคชันหลัก (`app.py`) ระบบจะตรวจพบและแสดงชื่อสายพันธุ์นั้นทันทีเมื่อกล้องตรวจเจอ!

### 4. รันผ่าน เมนูควบคุม Python (Unified CLI Menu)
```bash
python main.py
```

#### คำสั่งลัดโดยตรงผ่าน Flag:
* **เปิดแอป GUI ตรวจวัดหลัก:** `python main.py --app`
* **เปิดแอป Studio เทรนสายพันธุ์:** `python main.py --trainer`
* **สุ่มสร้าง Dataset จำลอง:** `python main.py --dataset`
* **ทดสอบประสิทธิภาพโมเดล:** `python main.py --eval`
* **ซิงก์และ Push ขึ้น GitHub:** `python main.py --push`

---

## 📊 ผลการประเมินเทียบกับเกณฑ์ความสำเร็จงานวิจัย

| ตัวชี้วัด / เกณฑ์ความสำเร็จ | เป้าหมายที่กำหนดไว้ | ผลการทดลองที่ได้จริง | สรุปผลการประเมิน |
| :--- | :---: | :---: | :---: |
| **ความแม่นยำในการจำแนกระดับความสุก (Accuracy)** | $\ge 85.00\%$ | **95.56%** (ด้วยแบบจำลอง CNN) | **ผ่านเกณฑ์** |
| **ความแม่นยำในการจำแนกสายพันธุ์ (Variety Accuracy)** | $\ge 85.00\%$ | **100.00%** (ด้วยแบบจำลอง Multi-Feature KNN) | **ผ่านเกณฑ์** |
| **เวลาในการประมวลผลรวมบนอุปกรณ์เอดจ์** | $\le 3.00\text{ วินาที/ภาพ}$ | **1.45 วินาที/ภาพ** (Raspberry Pi 4) / **14.4 ms** (PC) | **ผ่านเกณฑ์** |
| **ความสอดคล้องกับการประเมินโดยผู้เชี่ยวชาญ** | $\ge 90.00\%$ | **93.33%** | **ผ่านเกณฑ์** |

---

## 📄 ใบอนุญาตและการอ้างอิง
จัดทำขึ้นสำหรับการศึกษาวิจัยระบบคัดแยกผลผลิตทางการเกษตรด้วยเทคโนโลยีการประมวลผลภาพ
