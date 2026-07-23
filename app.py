import os
import sys
import time
import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

from avocado_classifier import AvocadoClassifier
from gauge_widget import GaugeWidget
from camera_manager import DualCameraManager
from generate_dataset import generate_sample_dataset
from trainer_gui import TrainerLabelerStudio

# CustomTkinter Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BackgroundCameraAvocadoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🥑 ระบบตรวจวัดระดับความสุกและสายพันธุ์อะโวคาโด (Background Camera Inspector)")
        self.geometry("1100x720")
        self.minsize(920, 600)

        # Dataset & Model Initialization
        self.dataset_dir = r"d:\Project\program\dataset"
        self.variety_dir = r"d:\Project\dataset\varieties"
        
        if not os.path.exists(self.dataset_dir):
            generate_sample_dataset(self.dataset_dir)

        # ML Engine & Background Dual Camera Manager
        self.classifier = AvocadoClassifier(dataset_dir=self.dataset_dir, variety_dir=self.variety_dir)
        self.cam_manager = DualCameraManager(self.dataset_dir)
        
        self.is_running = True
        self.trainer_win = None
        self.current_ann_frame = None

        self.build_ui()
        self.update_loop()

    def build_ui(self):
        # 1. Header Frame
        header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1e1e1e")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header_frame, 
            text="🥑 ระบบตรวจวัดระดับความสุกและจำแนกสายพันธุ์อะโวคาโด (Real-Time Background Engine)",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color="#2ecc71"
        )
        title_label.pack(side="left", padx=20, pady=14)

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="● Live Camera Active (Hidden Feed)",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            text_color="#2ecc71"
        )
        subtitle_label.pack(side="right", padx=20, pady=14)

        # 2. Main Content Frame (Split Center Left: Big Gauge Meter, Right: Live Cards & Control)
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=5)

        # --- Left Panel: Large Gauge Meter & Status Badge ---
        left_panel = ctk.CTkFrame(main_content, fg_color="#181818", corner_radius=12)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)

        g_header = ctk.CTkLabel(
            left_panel,
            text="🎯 เกจวัดระดับความสุก (Ripeness Gauge Meter)",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2ecc71"
        )
        g_header.pack(padx=20, pady=(20, 10))

        # Canvas Gauge Widget (Large)
        self.gauge = GaugeWidget(left_panel, width=420, height=260, bg="#181818")
        self.gauge.pack(padx=20, pady=10)

        # Main Ripeness Status Badge Banner
        self.badge_status = ctk.CTkFrame(left_panel, fg_color="#222222", corner_radius=10)
        self.badge_status.pack(fill="x", padx=30, pady=15)

        self.lbl_main_status = ctk.CTkLabel(
            self.badge_status,
            text="🥑 ระดับความสุก: กำลังประมวลผล...",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ffffff"
        )
        self.lbl_main_status.pack(pady=14)

        # --- Right Panel: Variety Card, Confidence & Actions ---
        right_panel = ctk.CTkFrame(main_content, width=440, fg_color="#181818", corner_radius=12)
        right_panel.pack(side="right", fill="y", padx=(10, 0), pady=5)
        right_panel.pack_propagate(False)

        cards_title = ctk.CTkLabel(
            right_panel,
            text="📊 ผลการเปรียบเทียบกับ Dataset (Live Prediction)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f39c12"
        )
        cards_title.pack(padx=20, pady=(20, 10), anchor="w")

        # Status Cards Container
        cards_box = ctk.CTkFrame(right_panel, fg_color="#222222", corner_radius=10)
        cards_box.pack(fill="x", padx=20, pady=5)

        # Metric 1: Variety Card
        self.lbl_variety = ctk.CTkLabel(
            cards_box,
            text="🏷️ สายพันธุ์ (Variety): ---",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3498db"
        )
        self.lbl_variety.pack(anchor="w", padx=18, pady=(15, 6))

        # Metric 2: Confidence % Card
        self.lbl_conf = ctk.CTkLabel(
            cards_box,
            text="ความเชื่อมั่น (Confidence): 0.0%",
            font=ctk.CTkFont(size=14),
            text_color="#aaaaaa"
        )
        self.lbl_conf.pack(anchor="w", padx=18, pady=4)

        # Metric 3: Inference Latency
        self.lbl_latency = ctk.CTkLabel(
            cards_box,
            text="เวลาประมวลผล (Latency): 0.0 ms",
            font=ctk.CTkFont(size=14),
            text_color="#aaaaaa"
        )
        self.lbl_latency.pack(anchor="w", padx=18, pady=(4, 15))

        # Camera Status Indicator Box
        cam_info_box = ctk.CTkFrame(right_panel, fg_color="#1c2833", corner_radius=8)
        cam_info_box.pack(fill="x", padx=20, pady=15)

        self.lbl_cam_active = ctk.CTkLabel(
            cam_info_box,
            text="📹 กล้องยังคงทำงานอยู่เบื้องหลังแบบเรียลไทม์\n(ดึงภาพจากกล้องมาเปรียบเทียบกับ Dataset อัตโนมัติ)",
            font=ctk.CTkFont(size=12),
            text_color="#3498db"
        )
        self.lbl_cam_active.pack(padx=12, pady=10)

        # Action Buttons
        btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        btn_trainer = ctk.CTkButton(
            btn_frame,
            text="🎓 เทรนและจัดการสายพันธุ์ (Trainer Studio)",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8e44ad",
            hover_color="#6c3483",
            command=self.open_trainer_studio
        )
        btn_trainer.pack(fill="x", pady=6)

        btn_snapshot = ctk.CTkButton(
            btn_frame,
            text="📸 บันทึกภาพเฟรมปัจจุบัน (Snapshot Frame)",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#27ae60",
            hover_color="#219150",
            command=self.on_snapshot
        )
        btn_snapshot.pack(fill="x", pady=6)

        # System Status Footer
        self.lbl_sys_info = ctk.CTkLabel(
            right_panel,
            text="● Live Engine Ready",
            font=ctk.CTkFont(size=11),
            text_color="#2ecc71"
        )
        self.lbl_sys_info.pack(side="bottom", pady=15)

    def open_trainer_studio(self):
        if self.trainer_win is None or not self.trainer_win.winfo_exists():
            self.trainer_win = TrainerLabelerStudio(dataset_dir=self.variety_dir)
            self.trainer_win.protocol("WM_DELETE_WINDOW", self.on_trainer_closed)
        else:
            self.trainer_win.focus()

    def on_trainer_closed(self):
        if self.trainer_win:
            self.trainer_win.on_closing()
            self.trainer_win = None
        # Reload Variety Classifier Engine
        self.classifier.variety_trainer.load_or_train()
        self.lbl_sys_info.configure(text="● โหลดโมเดลสายพันธุ์ใหม่เรียบร้อยแล้ว!", text_color="#f1c40f")

    def on_snapshot(self):
        if self.current_ann_frame is not None:
            os.makedirs(r"d:\Project\snapshots", exist_ok=True)
            fname = f"camera_snapshot_{int(time.time())}.jpg"
            fpath = os.path.join(r"d:\Project\snapshots", fname)
            cv2.imwrite(fpath, self.current_ann_frame)
            messagebox.showinfo("บันทึกสำเร็จ", f"บันทึกรูปภาพจากกล้องเบื้องหลังเรียบร้อยแล้วที่:\n{fpath}")

    def update_loop(self):
        if not self.is_running:
            return

        start_t = time.time()
        
        # Read frames from live background camera
        frame1, frame2 = self.cam_manager.read_frames()

        # Classify Avocado Ripeness AND Variety on live background frames
        ann1, cat1, score1, conf1, var1, var_conf1 = self.classifier.predict_frame(frame1)
        ann2, cat2, score2, conf2, var2, var_conf2 = self.classifier.predict_frame(frame2)

        self.current_ann_frame = ann1

        latency_ms = (time.time() - start_t) * 1000.0

        # Average Gauge score from background camera feeds
        avg_score = (score1 + score2) / 2.0
        avg_conf = (conf1 + conf2) / 2.0

        # Update Ripeness Gauge Needle
        self.gauge.set_score(avg_score)
        
        status_th = {"Unripe": "ดิบ (Unripe)", "Mid-ripe": "กึ่งสุก (Mid-ripe)", "Ripe": "สุก (Ripe)"}.get(cat1, cat1)
        status_colors = {"Unripe": "#2ecc71", "Mid-ripe": "#f39c12", "Ripe": "#e74c3c"}

        # Update UI Badges & Cards (No Camera Feed Displayed!)
        self.lbl_main_status.configure(text=f"🥑 ระดับความสุก: {status_th}", text_color=status_colors.get(cat1, "#ffffff"))
        self.lbl_variety.configure(text=f"🏷️ สายพันธุ์: {var1} ({var_conf1:.0f}%)", text_color="#3498db")
        self.lbl_conf.configure(text=f"ความเชื่อมั่น (Confidence): {avg_conf:.1f}%")
        self.lbl_latency.configure(text=f"เวลาประมวลผล (Latency): {latency_ms:.1f} ms")

        # Refresh loop every ~30ms (approx 30 FPS background analysis)
        self.after(30, self.update_loop)

    def on_closing(self):
        self.is_running = False
        if self.trainer_win:
            try:
                self.trainer_win.on_closing()
            except Exception:
                pass
        self.cam_manager.release()
        self.destroy()

if __name__ == "__main__":
    app = BackgroundCameraAvocadoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
