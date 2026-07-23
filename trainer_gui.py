import os
import sys
import cv2
import time
import glob
import shutil
import threading
import numpy as np
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from avocado_variety_trainer import AvocadoVarietyTrainer

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TrainerLabelerStudio(ctk.CTk):
    def __init__(self, dataset_dir=r"d:\Project\dataset\varieties"):
        super().__init__()

        self.title("🎓 โปรแกรมเทรนและกำหนด Label สายพันธุ์อะโวคาโด (Avocado Variety Trainer & Labeler Studio)")
        self.geometry("1180x740")
        self.minsize(980, 640)

        self.dataset_dir = dataset_dir
        os.makedirs(self.dataset_dir, exist_ok=True)

        self.trainer = AvocadoVarietyTrainer(dataset_dir=self.dataset_dir)
        
        self.is_running = True
        self.is_training = False
        self.selected_label = ""
        self.cap = None
        self.use_sim_cam = True

        # Non-blocking camera initialization in background thread
        threading.Thread(target=self.init_camera_async, daemon=True).start()

        self.build_ui()
        self.refresh_variety_list()
        self.update_webcam_loop()

    def init_camera_async(self):
        """Asynchronously initialize webcam to prevent GUI freeze on startup"""
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    self.cap = cap
                    self.use_sim_cam = False
                    return
                cap.release()
        except Exception:
            pass
        self.use_sim_cam = True

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, corner_radius=10, fg_color="#1e1e1e")
        header.pack(fill="x", padx=15, pady=(15, 5))

        title = ctk.CTkLabel(
            header,
            text="🎓 Avocado Variety Trainer & Labeler Studio (ระบบสร้าง Label และเทรนจำแนกสายพันธุ์)",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color="#3498db"
        )
        title.pack(side="left", padx=20, pady=12)

        subtitle = ctk.CTkLabel(
            header,
            text="Custom Dataset & Variety ML Training Engine",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        subtitle.pack(side="right", padx=20, pady=12)

        # Main Layout (Split Left: Camera/Import, Right: Label Manager & Train)
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # --- Left Panel: Camera & Capture ---
        left_panel = ctk.CTkFrame(main_frame, fg_color="#181818", corner_radius=10)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=5)

        cam_title = ctk.CTkLabel(
            left_panel,
            text="📷 กล้องถ่ายภาพตัวอย่างสำหรับเทรน (Capture Training Samples)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cam_title.pack(padx=15, pady=10, anchor="w")

        # Video container
        self.video_box = tk.Label(left_panel, bg="#000000")
        self.video_box.pack(fill="both", expand=True, padx=15, pady=5)

        # Action capture buttons
        cap_btn_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        cap_btn_frame.pack(fill="x", padx=15, pady=10)

        self.btn_capture = ctk.CTkButton(
            cap_btn_frame,
            text="📸 ถ่ายภาพเข้า Label ที่เลือก (Capture Photo)",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#27ae60",
            hover_color="#1e8449",
            command=self.capture_photo
        )
        self.btn_capture.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_import = ctk.CTkButton(
            cap_btn_frame,
            text="📁 นำเข้าไฟล์/โฟลเดอร์ภาพ (Import Images)",
            font=ctk.CTkFont(size=13),
            fg_color="#2980b9",
            hover_color="#1b4f72",
            command=self.import_images
        )
        self.btn_import.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # --- Right Panel: Label & Variety Manager ---
        right_panel = ctk.CTkFrame(main_frame, width=420, fg_color="#181818", corner_radius=10)
        right_panel.pack(side="right", fill="y", padx=(8, 0), pady=5)
        right_panel.pack_propagate(False)

        right_title = ctk.CTkLabel(
            right_panel,
            text="🏷️ จัดการ Label สายพันธุ์ (Variety Labels)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f39c12"
        )
        right_title.pack(padx=15, pady=(15, 5), anchor="w")

        # Add Label Entry
        entry_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        entry_frame.pack(fill="x", padx=15, pady=5)

        self.entry_label_name = ctk.CTkEntry(
            entry_frame,
            placeholder_text="พิมพ์ชื่อสายพันธุ์ใหม่ (เช่น Hass, Booth 7, Reed)",
            font=ctk.CTkFont(size=13)
        )
        self.entry_label_name.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_add = ctk.CTkButton(
            entry_frame,
            text="➕ เพิ่ม",
            width=65,
            fg_color="#f39c12",
            hover_color="#d68910",
            command=self.add_new_variety_label
        )
        btn_add.pack(side="right")

        # Label List Scrollable Container
        list_lbl = ctk.CTkLabel(
            right_panel,
            text="รายการสายพันธุ์ที่มีในระบบ (คลิกเลือก Label เพื่อถ่ายภาพสะสม):",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa"
        )
        list_lbl.pack(padx=15, pady=(10, 2), anchor="w")

        self.variety_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="#222222", corner_radius=8, height=200)
        self.variety_scroll.pack(fill="x", padx=15, pady=5)

        # Info Box / Status
        self.lbl_selected_status = ctk.CTkLabel(
            right_panel,
            text="📌 Label ที่เลือกอยู่: (ยังไม่ได้เลือก)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#2ecc71"
        )
        self.lbl_selected_status.pack(padx=15, pady=5, anchor="w")

        # Train Model Control Box
        train_box = ctk.CTkFrame(right_panel, fg_color="#252525", corner_radius=8)
        train_box.pack(fill="x", padx=15, pady=10)

        t_box_title = ctk.CTkLabel(
            train_box,
            text="🧠 ฝึกฝนแบบจำลอง (Model Trainer Engine)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3498db"
        )
        t_box_title.pack(padx=12, pady=(10, 4), anchor="w")

        self.lbl_train_stats = ctk.CTkLabel(
            train_box,
            text="สถานะโมเดล: กำลังโหลด...",
            font=ctk.CTkFont(size=12),
            text_color="#cccccc"
        )
        self.lbl_train_stats.pack(padx=12, pady=2, anchor="w")

        self.btn_start_train = ctk.CTkButton(
            train_box,
            text="⚡ เริ่มเทรนโมเดลสายพันธุ์ (Start Training)",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.start_training
        )
        self.btn_start_train.pack(fill="x", padx=12, pady=10)

    def refresh_variety_list(self):
        """Refreshes the scrollable list of variety labels"""
        for child in self.variety_scroll.winfo_children():
            child.destroy()

        folders = [f for f in os.listdir(self.dataset_dir) if os.path.isdir(os.path.join(self.dataset_dir, f))]
        
        if not folders:
            lbl_empty = ctk.CTkLabel(self.variety_scroll, text="ยังไม่มี Label สายพันธุ์ กรุณากรอกเพิ่มด้านบน", text_color="#777777")
            lbl_empty.pack(pady=15)
            self.selected_label = ""
            self.lbl_selected_status.configure(text="📌 Label ที่เลือกอยู่: (ไม่มี)", text_color="#e74c3c")
            return

        if not self.selected_label or self.selected_label not in folders:
            self.selected_label = folders[0]

        self.lbl_selected_status.configure(text=f"📌 Label ที่เลือกอยู่: [{self.selected_label}]", text_color="#2ecc71")

        for folder in sorted(folders):
            folder_path = os.path.join(self.dataset_dir, folder)
            img_count = len(glob.glob(os.path.join(folder_path, "*.*")))

            row_frame = ctk.CTkFrame(self.variety_scroll, fg_color="#1e1e1e" if folder != self.selected_label else "#2980b9", corner_radius=6)
            row_frame.pack(fill="x", padx=4, pady=3)

            is_sel = (folder == self.selected_label)
            btn_select = ctk.CTkButton(
                row_frame,
                text=f"🥑 {folder} ({img_count} ภาพ)",
                anchor="w",
                fg_color="transparent",
                hover_color="#34495e",
                font=ctk.CTkFont(size=13, weight="bold" if is_sel else "normal"),
                command=lambda f=folder: self.select_label(f)
            )
            btn_select.pack(side="left", fill="x", expand=True, padx=5, pady=4)

            btn_del = ctk.CTkButton(
                row_frame,
                text="❌",
                width=30,
                fg_color="#c0392b",
                hover_color="#922b21",
                command=lambda f=folder: self.delete_label(f)
            )
            btn_del.pack(side="right", padx=5, pady=4)

        # Update train stats
        total_imgs = sum([len(glob.glob(os.path.join(self.dataset_dir, f, "*.*"))) for f in folders])
        status_text = "กำลังเทรนโมเดล..." if self.is_training else ('พร้อมใช้งาน' if self.trainer.trained else 'ยังไม่ได้เทรน')
        self.lbl_train_stats.configure(
            text=f"มี {len(folders)} สายพันธุ์ | ทั้งหมด {total_imgs} ภาพตัวอย่าง\nสถานะโมเดล: {status_text}"
        )

    def select_label(self, label_name):
        self.selected_label = label_name
        self.refresh_variety_list()

    def add_new_variety_label(self):
        new_name = self.entry_label_name.get().strip()
        if not new_name:
            messagebox.showwarning("ข้อผิดพลาด", "กรุณากรอกชื่อสายพันธุ์ก่อนกดเพิ่ม")
            return
        
        folder_path = os.path.join(self.dataset_dir, new_name)
        os.makedirs(folder_path, exist_ok=True)
        self.entry_label_name.delete(0, 'end')
        self.selected_label = new_name
        self.refresh_variety_list()

    def delete_label(self, label_name):
        if messagebox.askyesno("ยืนยันลบ", f"คุณต้องการลบสายพันธุ์ '{label_name}' พร้อมรูปภาพทั้งหมดหรือไม่?"):
            folder_path = os.path.join(self.dataset_dir, label_name)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
            self.selected_label = ""
            self.refresh_variety_list()

    def capture_photo(self):
        if not self.selected_label:
            messagebox.showwarning("คำเตือน", "กรุณาเพิ่มหรือเลือก Label สายพันธุ์ก่อนถ่ายภาพ")
            return

        if hasattr(self, "current_frame") and self.current_frame is not None:
            folder_path = os.path.join(self.dataset_dir, self.selected_label)
            os.makedirs(folder_path, exist_ok=True)
            fname = f"{self.selected_label}_{int(time.time()*1000)}.jpg"
            fpath = os.path.join(folder_path, fname)
            cv2.imwrite(fpath, self.current_frame)
            self.refresh_variety_list()

    def import_images(self):
        if not self.selected_label:
            messagebox.showwarning("คำเตือน", "กรุณาเลือก Label สายพันธุ์เป้าหมายที่ต้องการนำเข้าก่อน")
            return

        files = filedialog.askopenfilenames(
            title="เลือกไฟล์รูปภาพอะโวคาโด",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if files:
            folder_path = os.path.join(self.dataset_dir, self.selected_label)
            os.makedirs(folder_path, exist_ok=True)
            for f in files:
                fname = f"{self.selected_label}_imp_{int(time.time()*1000)}_{os.path.basename(f)}"
                shutil.copy(f, os.path.join(folder_path, fname))
            self.refresh_variety_list()

    def start_training(self):
        """Asynchronously start model training in a background thread to prevent GUI freeze"""
        if self.is_training:
            return

        self.is_training = True
        self.btn_start_train.configure(text="⏳ กำลังเทรนโมเดล... (Training...)", state="disabled", fg_color="#7f8c8d")
        self.lbl_train_stats.configure(text="สถานะโมเดล: ⏳ กำลังสกัด Feature และเทรนโมเดล...")

        # Run training in background daemon thread
        threading.Thread(target=self._run_training_worker, daemon=True).start()

    def _run_training_worker(self):
        try:
            success, samples, classes = self.trainer.train()
        except Exception as e:
            success, samples, classes = False, 0, 0
            print(f"Training worker error: {e}")

        # Post result back to main GUI thread safely
        self.after(0, lambda: self._on_training_finished(success, samples, classes))

    def _on_training_finished(self, success, samples, classes):
        self.is_training = False
        self.btn_start_train.configure(text="⚡ เริ่มเทรนโมเดลสายพันธุ์ (Start Training)", state="normal", fg_color="#e74c3c")
        self.refresh_variety_list()

        if success:
            messagebox.showinfo(
                "สำเร็จ",
                f"🎉 เทรนโมเดลจำแนกสายพันธุ์สำเร็จเรียบร้อยแล้ว!\n\n- จำนวนสายพันธุ์: {classes} สายพันธุ์\n- ตัวอย่างภาพทั้งหมด: {samples} ภาพ\n- บันทึกไฟล์โมเดลที่: variety_model.pkl"
            )
        else:
            messagebox.showerror("ผิดพลาด", "ไม่สามารถเทรนโมเดลได้ กรุณาเพิ่มสายพันธุ์อย่างน้อย 1 สายพันธุ์และมีรูปภาพอย่างน้อย 2 ภาพ")

    def update_webcam_loop(self):
        if not self.is_running:
            return

        frame = None
        if not self.use_sim_cam and self.cap and self.cap.isOpened():
            try:
                ret, img = self.cap.read()
                if ret:
                    frame = img
            except Exception:
                pass

        if frame is None:
            frame = self.get_simulated_frame()

        self.current_frame = frame.copy()

        # Draw ROI guide box
        h, w, _ = frame.shape
        cv2.rectangle(frame, (int(w*0.25), int(h*0.15)), (int(w*0.75), int(h*0.85)), (0, 255, 255), 2)
        cv2.putText(frame, "Place Avocado in Box", (int(w*0.28), int(h*0.12)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

        if self.selected_label:
            cv2.putText(frame, f"Label: {self.selected_label}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        # Convert to Tkinter Image
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb).resize((620, 460), Image.Resampling.BILINEAR)
        tk_img = ImageTk.PhotoImage(image=img_pil)
        self.video_box.configure(image=tk_img)
        self.video_box.image = tk_img

        self.after(33, self.update_webcam_loop)

    def get_simulated_frame(self):
        img = np.ones((480, 640, 3), dtype=np.uint8) * 200
        cv2.ellipse(img, (320, 240), (100, 140), 0, 0, 360, (30, 120, 40), -1)
        cv2.putText(img, "Training Studio Live Feed", (180, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        return img

    def on_closing(self):
        self.is_running = False
        if self.cap and self.cap.isOpened():
            try:
                self.cap.release()
            except Exception:
                pass
        self.destroy()

if __name__ == "__main__":
    app = TrainerLabelerStudio()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
