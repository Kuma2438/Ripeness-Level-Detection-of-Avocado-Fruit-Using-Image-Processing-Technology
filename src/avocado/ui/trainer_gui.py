"""Trainer & Labeler Studio GUI."""

from pathlib import Path
import shutil
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional
import cv2
import customtkinter as ctk
import numpy as np
from PIL import Image, ImageTk

from avocado.config import AppConfig, get_project_root, load_config
from avocado.core.trainer import AvocadoTrainer


class TrainerLabelerStudio(ctk.CTkToplevel):
    """GUI window for creating custom variety labels, capturing training samples, and training CNN."""

    def __init__(self, parent: Optional[ctk.CTk] = None, config: Optional[AppConfig] = None) -> None:
        super().__init__(parent)

        self.config = config or load_config()
        self.dataset_dir = Path(self.config.dataset.varieties_dir)
        self.dataset_dir.mkdir(parents=True, exist_ok=True)

        self.title("🎓 Avocado Variety Trainer & Labeler Studio")
        self.geometry("1180x740")
        self.minsize(980, 640)

        self.trainer = AvocadoTrainer(
            dataset_dir=self.dataset_dir,
            model_save_path=self.config.models.variety_model_path,
            device=self.config.models.device,
        )

        self.is_running = True
        self.is_training = False
        self.selected_label = ""
        self.cap: Optional[cv2.VideoCapture] = None
        self.use_sim_cam = True
        self.current_frame: Optional[np.ndarray] = None

        threading.Thread(target=self._init_camera_async, daemon=True).start()

        self.build_ui()
        self.refresh_variety_list()
        self.update_webcam_loop()

    def _init_camera_async(self) -> None:
        try:
            cap = cv2.VideoCapture(self.config.camera.cam1_id)
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

    def build_ui(self) -> None:
        header = ctk.CTkFrame(self, corner_radius=10, fg_color="#1e1e1e")
        header.pack(fill="x", padx=15, pady=(15, 5))

        title = ctk.CTkLabel(
            header,
            text="🎓 Avocado Variety Trainer & Labeler Studio",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color="#3498db",
        )
        title.pack(side="left", padx=20, pady=12)

        subtitle = ctk.CTkLabel(
            header,
            text="Custom Dataset & Variety ML Training Engine",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
        )
        subtitle.pack(side="right", padx=20, pady=12)

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Left Panel: Camera & Capture
        left_panel = ctk.CTkFrame(main_frame, fg_color="#181818", corner_radius=10)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=5)

        cam_title = ctk.CTkLabel(
            left_panel,
            text="📷 กล้องถ่ายภาพตัวอย่างสำหรับเทรน (Capture Training Samples)",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        cam_title.pack(padx=15, pady=10, anchor="w")

        self.video_box = tk.Label(left_panel, bg="#000000")
        self.video_box.pack(fill="both", expand=True, padx=15, pady=5)

        cap_btn_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        cap_btn_frame.pack(fill="x", padx=15, pady=10)

        self.btn_capture = ctk.CTkButton(
            cap_btn_frame,
            text="📸 ถ่ายภาพเข้า Label ที่เลือก (Capture)",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#27ae60",
            hover_color="#1e8449",
            command=self.capture_photo,
        )
        self.btn_capture.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_import = ctk.CTkButton(
            cap_btn_frame,
            text="📁 นำเข้าไฟล์/โฟลเดอร์ภาพ (Import)",
            font=ctk.CTkFont(size=13),
            fg_color="#2980b9",
            hover_color="#1b4f72",
            command=self.import_images,
        )
        self.btn_import.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # Right Panel: Label & Variety Manager
        right_panel = ctk.CTkFrame(main_frame, width=420, fg_color="#181818", corner_radius=10)
        right_panel.pack(side="right", fill="y", padx=(8, 0), pady=5)
        right_panel.pack_propagate(False)

        right_title = ctk.CTkLabel(
            right_panel,
            text="🏷️ จัดการ Label สายพันธุ์ (Variety Labels)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f39c12",
        )
        right_title.pack(padx=15, pady=(15, 5), anchor="w")

        entry_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        entry_frame.pack(fill="x", padx=15, pady=5)

        self.entry_label_name = ctk.CTkEntry(
            entry_frame,
            placeholder_text="พิมพ์ชื่อสายพันธุ์ (เช่น Hass, Pinkerton, Booth 7)",
            font=ctk.CTkFont(size=13),
        )
        self.entry_label_name.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_add = ctk.CTkButton(
            entry_frame,
            text="➕ เพิ่ม",
            width=65,
            fg_color="#f39c12",
            hover_color="#d68910",
            command=self.add_new_variety_label,
        )
        btn_add.pack(side="right")

        list_lbl = ctk.CTkLabel(
            right_panel,
            text="รายการสายพันธุ์ (คลิกเพื่อเลือกบันทึกภาพ):",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa",
        )
        list_lbl.pack(padx=15, pady=(10, 2), anchor="w")

        self.variety_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="#222222", corner_radius=8, height=200)
        self.variety_scroll.pack(fill="x", padx=15, pady=5)

        self.lbl_selected_status = ctk.CTkLabel(
            right_panel,
            text="📌 Label ที่เลือก: (ยังไม่ได้เลือก)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#2ecc71",
        )
        self.lbl_selected_status.pack(padx=15, pady=5, anchor="w")

        train_box = ctk.CTkFrame(right_panel, fg_color="#252525", corner_radius=8)
        train_box.pack(fill="x", padx=15, pady=10)

        t_box_title = ctk.CTkLabel(
            train_box,
            text="🧠 ฝึกฝนแบบจำลอง (Model Trainer Engine)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3498db",
        )
        t_box_title.pack(padx=12, pady=(10, 4), anchor="w")

        self.lbl_train_stats = ctk.CTkLabel(
            train_box,
            text="สถานะโมเดล: กำลังโหลด...",
            font=ctk.CTkFont(size=12),
            text_color="#cccccc",
        )
        self.lbl_train_stats.pack(padx=12, pady=2, anchor="w")

        self.btn_start_train = ctk.CTkButton(
            train_box,
            text="⚡ เริ่มเทรนโมเดลสายพันธุ์ (Start Training)",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.start_training,
        )
        self.btn_start_train.pack(fill="x", padx=12, pady=10)

    def refresh_variety_list(self) -> None:
        """Refreshes the scrollable variety directory list."""
        for child in self.variety_scroll.winfo_children():
            child.destroy()

        folders = [f.name for f in self.dataset_dir.iterdir() if f.is_dir()]

        if not folders:
            lbl_empty = ctk.CTkLabel(self.variety_scroll, text="ยังไม่มี Label สายพันธุ์ กรุณากรอกเพิ่มด้านบน", text_color="#777777")
            lbl_empty.pack(pady=15)
            self.selected_label = ""
            self.lbl_selected_status.configure(text="📌 Label ที่เลือก: (ไม่มี)", text_color="#e74c3c")
            return

        if not self.selected_label or self.selected_label not in folders:
            self.selected_label = folders[0]

        self.lbl_selected_status.configure(text=f"📌 Label ที่เลือก: [{self.selected_label}]", text_color="#2ecc71")

        for folder in sorted(folders):
            folder_path = self.dataset_dir / folder
            img_count = len(list(folder_path.glob("*.*")))

            row_frame = ctk.CTkFrame(self.variety_scroll, fg_color="#1e1e1e" if folder != self.selected_label else "#2980b9", corner_radius=6)
            row_frame.pack(fill="x", padx=4, pady=3)

            is_sel = folder == self.selected_label
            btn_select = ctk.CTkButton(
                row_frame,
                text=f"🥑 {folder} ({img_count} ภาพ)",
                anchor="w",
                fg_color="transparent",
                hover_color="#34495e",
                font=ctk.CTkFont(size=13, weight="bold" if is_sel else "normal"),
                command=lambda f=folder: self.select_label(f),
            )
            btn_select.pack(side="left", fill="x", expand=True, padx=5, pady=4)

            btn_del = ctk.CTkButton(
                row_frame,
                text="❌",
                width=30,
                fg_color="#c0392b",
                hover_color="#922b21",
                command=lambda f=folder: self.delete_label(f),
            )
            btn_del.pack(side="right", padx=5, pady=4)

        total_imgs = sum(len(list((self.dataset_dir / f).glob("*.*"))) for f in folders)
        status_text = "กำลังเทรนโมเดล..." if self.is_training else ("พร้อมใช้งาน" if self.trainer.trained else "ยังไม่ได้เทรน")
        self.lbl_train_stats.configure(
            text=f"มี {len(folders)} สายพันธุ์ | ทั้งหมด {total_imgs} ภาพตัวอย่าง\nสถานะโมเดล: {status_text}"
        )

    def select_label(self, label_name: str) -> None:
        self.selected_label = label_name
        self.refresh_variety_list()

    def add_new_variety_label(self) -> None:
        new_name = self.entry_label_name.get().strip()
        if not new_name:
            messagebox.showwarning("ข้อผิดพลาด", "กรุณากรอกชื่อสายพันธุ์ก่อนกดเพิ่ม")
            return

        folder_path = self.dataset_dir / new_name
        folder_path.mkdir(parents=True, exist_ok=True)
        self.entry_label_name.delete(0, "end")
        self.selected_label = new_name
        self.refresh_variety_list()

    def delete_label(self, label_name: str) -> None:
        if messagebox.askyesno("ยืนยันลบ", f"คุณต้องการลบสายพันธุ์ '{label_name}' พร้อมรูปภาพทั้งหมดหรือไม่?"):
            folder_path = self.dataset_dir / label_name
            if folder_path.is_dir():
                shutil.rmtree(folder_path)
            self.selected_label = ""
            self.refresh_variety_list()

    def capture_photo(self) -> None:
        if not self.selected_label:
            messagebox.showwarning("คำเตือน", "กรุณาเพิ่มหรือเลือก Label สายพันธุ์ก่อนถ่ายภาพ")
            return

        if self.current_frame is not None:
            folder_path = self.dataset_dir / self.selected_label
            folder_path.mkdir(parents=True, exist_ok=True)
            fname = f"{self.selected_label}_{int(time.time()*1000)}.jpg"
            fpath = folder_path / fname
            cv2.imwrite(str(fpath), self.current_frame)
            self.refresh_variety_list()

    def import_images(self) -> None:
        if not self.selected_label:
            messagebox.showwarning("คำเตือน", "กรุณาเลือก Label สายพันธุ์เป้าหมายก่อน")
            return

        files = filedialog.askopenfilenames(
            title="เลือกไฟล์รูปภาพอะโวคาโด",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")],
        )
        if files:
            folder_path = self.dataset_dir / self.selected_label
            folder_path.mkdir(parents=True, exist_ok=True)
            for f in files:
                fname = f"{self.selected_label}_imp_{int(time.time()*1000)}_{Path(f).name}"
                shutil.copy(f, str(folder_path / fname))
            self.refresh_variety_list()

    def start_training(self) -> None:
        if self.is_training:
            return

        self.is_training = True
        self.btn_start_train.configure(text="⏳ กำลังเทรนโมเดล... (Training...)", state="disabled", fg_color="#7f8c8d")
        self.lbl_train_stats.configure(text="สถานะโมเดล: ⏳ กำลังสกัด Feature และเทรนโมเดล...")

        threading.Thread(target=self._run_training_worker, daemon=True).start()

    def _run_training_worker(self) -> None:
        try:
            success = self.trainer.train_model(
                epochs=self.config.training.epochs,
                batch_size=self.config.training.batch_size,
                lr=self.config.training.learning_rate,
            )
        except Exception as e:
            success = False
            print(f"Training worker error: {e}")

        self.after(0, lambda: self._on_training_finished(success))

    def _on_training_finished(self, success: bool) -> None:
        self.is_training = False
        self.btn_start_train.configure(text="⚡ เริ่มเทรนโมเดลสายพันธุ์ (Start Training)", state="normal", fg_color="#e74c3c")
        self.refresh_variety_list()

        if success:
            messagebox.showinfo(
                "สำเร็จ",
                f"🎉 เทรนโมเดลจำแนกสายพันธุ์สำเร็จ!\nบันทึกไฟล์โมเดลที่:\n{self.config.models.variety_model_path}",
            )
        else:
            messagebox.showerror(
                "ผิดพลาด",
                "ไม่สามารถเทรนโมเดลได้ กรุณาเพิ่มสายพันธุ์และมีรูปภาพอย่างน้อย 2 ภาพ",
            )

    def update_webcam_loop(self) -> None:
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
            frame = self._get_simulated_frame()

        self.current_frame = frame.copy()

        h, w, _ = frame.shape
        cv2.rectangle(frame, (int(w * 0.25), int(h * 0.15)), (int(w * 0.75), int(h * 0.85)), (0, 255, 255), 2)
        cv2.putText(frame, "Place Avocado in Box", (int(w * 0.28), int(h * 0.12)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

        if self.selected_label:
            cv2.putText(frame, f"Label: {self.selected_label}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb).resize((620, 460), Image.Resampling.BILINEAR)
        tk_img = ImageTk.PhotoImage(image=img_pil)
        self.video_box.configure(image=tk_img)
        self.video_box.image = tk_img

        self.after(33, self.update_webcam_loop)

    def _get_simulated_frame(self) -> np.ndarray:
        img = np.ones((480, 640, 3), dtype=np.uint8) * 200
        cv2.ellipse(img, (320, 240), (100, 140), 0, 0, 360, (30, 120, 40), -1)
        cv2.putText(img, "Training Studio Live Feed", (180, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        return img

    def on_closing(self) -> None:
        self.is_running = False
        if self.cap and self.cap.isOpened():
            try:
                self.cap.release()
            except Exception:
                pass
        self.destroy()
