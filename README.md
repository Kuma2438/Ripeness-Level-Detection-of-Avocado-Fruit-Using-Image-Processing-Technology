# 🥑 Avocado Ripeness Inspector Application (โปรแกรมวัดระดับความสุกอะโวคาโด)

โปรแกรมวัดระดับความสุกของผลอะโวคาโดแบบเรียลไทม์ด้วยระบบประมวลผลภาพ (Color & Texture Image Processing) ร่วมกับ Machine Learning / Edge AI รองรับกล้อง 2 ตัว (Dual Camera) พร้อม Gauge Widget แสดงระดับความสุก

---

## 🌟 คุณสมบัติเด่นของโปรแกรม (Features)

1. **รองรับกล้อง 2 ตัว (Dual Camera Feeds):**
   * แสดงผลวิดีโอจากกล้อง 2 ตัวพร้อมกัน (เช่น มุมมองด้านบน Top View และด้านข้าง Side View)
   * สามารถเลือกสลับโหมดการดูได้: **Split View (2 กล้อง)** / **Cam 1 Only** / **Cam 2 Only**
   * หากไม่ได้เสียบกล้อง หรือเปิดกล้องไม่ได้ ระบบจะ **Fallback ไปใช้กล้องจำลอง (Simulated Camera Feed)** โดยอัตโนมัติ เพื่อให้ทดสอบแอปได้โดยไม่มีการ Crash
2. **เกจวัดระดับความสุก (Gauge Widget Meter):**
   * แสดงเกจแบบหน้าปัดเรือนไมล์หลากสี (เขียว = Unripe, เหลือง/ส้ม = Mid-ripe, แดง/ดำ = Ripe)
   * เข็มวัดเคลื่อนที่แบบแอนิเมชันนุ่มนวล (Smooth Animation) ชี้บอกคะแนนความสุก (0% – 100%)
3. **การประมวลผลเรียลไทม์ (Real-Time Object & Ripeness Detection):**
   * ตรวจจับตำแหน่งผลอะโวคาโดบนหน้าจอพร้อมวาด Bounding Box
   * สกัดคุณลักษณะด้านสี ($RGB, HSV$) และพื้นผิว ($GLCM$)
   * จำแนกระดับความสุก 3 ระดับ: **Unripe (ดิบ)**, **Mid-ripe (กึ่งสุก)**, **Ripe (สุก)** พร้อมค่าความเชื่อมั่น ($Confidence\ \%$) และเวลาประมวลผล ($Latency\ ms$)
4. **ชุดข้อมูลจำลอง (Sample Dataset Generator):**
   * สคริปต์สร้างชุดข้อมูลภาพถ่ายอะโวคาโดจำลอง 3 ระดับความสุกในตัว สะดวกสำหรับการทดลองเทรนโมเดลและทดสอบระบบ

---

## 📁 โครงสร้างไฟล์ในโฟลเดอร์ `program/`

```
d:\Project\program\
├── app.py                      # แอปพลิเคชัน GUI หลัก (CustomTkinter)
├── avocado_classifier.py       # Engine สกัดคุณลักษณะและจำแนกระดับความสุก
├── gauge_widget.py             # Gauge Widget แสดงเกจวัดบน Canvas
├── camera_manager.py           # ตัวจัดการกล้องคู่ (Dual Camera & Simulation Fallback)
├── generate_dataset.py         # ตัวสร้าง Sample Dataset จำลอง 3 ระดับความสุก
├── requirements.txt            # รายการแพ็กเกจที่ต้องใช้
└── dataset/                    # โฟลเดอร์เก็บภาพ Sample Dataset (สร้างให้อัตโนมัติ)
```

---

## 🚀 วิธีการรันโปรแกรม

เปิด Terminal / Command Prompt แล้วพิมพ์คำสั่ง:

```bash
cd d:\Project\program
python app.py
```
