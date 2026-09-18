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

        self.title("🥑 ระบบตรวจวัดระดับความสุกและจำแนกสายพันธุ์อะโวคาโด (Avocado Inspector Dashboard)")
        self.geometry("1080x720")
        self.minsize(960, 640)

        # Dataset & Model Initialization
        self.dataset_dir = r"d:\Project\dataset"
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
        # Single Unified Outer Container Frame (รวมอยู่ในช่องเดียวกันทั้งหมด)
        unified_card = ctk.CTkFrame(self, fg_color="#181818", corner_radius=16, border_width=1, border_color="#2c3e50")
        unified_card.pack(fill="both", expand=True, padx=20, pady=20)

        # --- 1. Header Section Inside Card ---
        header_box = ctk.CTkFrame(unified_card, fg_color="#222222", corner_radius=12)
        header_box.pack(fill="x", padx=20, pady=(20, 15))

        title_label = ctk.CTkLabel(
            header_box, 
            text="🥑 ระบบตรวจวัดระดับความสุกและจำแนกสายพันธุ์อะโวคาโด (Avocado Inspector Engine)",
            font=ctk.CTkFont(family="Helvetica", size=19, weight="bold"),
            text_color="#2ecc71"
        )
        title_label.pack(side="left", padx=20, pady=12)

        self.lbl_cam_status = ctk.CTkLabel(
            header_box,
            text="● กล้องทำงานเบื้องหลัง (Live Active)",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            text_color="#2ecc71"
        )
        self.lbl_cam_status.pack(side="right", padx=20, pady=12)

        # --- 2. Main Dashboard Content Grid Inside Card ---
        content_box = ctk.CTkFrame(unified_card, fg_color="transparent")
        content_box.pack(fill="both", expand=True, padx=20, pady=5)

        # Left Column: Large Gauge Widget
        gauge_box = ctk.CTkFrame(content_box, fg_color="#202020", corner_radius=12, border_width=1, border_color="#333333")
        gauge_box.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)

        g_title = ctk.CTkLabel(
            gauge_box,
            text="🎯 เกจวัดระดับความสุก (Ripeness Gauge)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#2ecc71"
        )
        g_title.pack(padx=15, pady=(15, 5))

        # Canvas Gauge Widget
        self.gauge = GaugeWidget(gauge_box, width=400, height=250, bg="#202020")
        self.gauge.pack(padx=15, pady=5)

        # Right Column: Unified Metrics & Status Cards
        metrics_box = ctk.CTkFrame(content_box, fg_color="#202020", corner_radius=12, border_width=1, border_color="#333333")
        metrics_box.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=5)

        m_title = ctk.CTkLabel(
            metrics_box,
            text="📊 ผลการวิเคราะห์และทำนายภาพ (CNN Live Prediction)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f39c12"
        )
        m_title.pack(padx=20, pady=(15, 10), anchor="w")

        # Status 1: Main Ripeness Level Banner
        self.ripeness_card = ctk.CTkFrame(metrics_box, fg_color="#282828", corner_radius=10)
        self.ripeness_card.pack(fill="x", padx=20, pady=6)

        self.lbl_main_status = ctk.CTkLabel(
            self.ripeness_card,
            text="🥑 ระดับความสุก: กำลังประมวลผล...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        self.lbl_main_status.pack(anchor="w", padx=16, pady=12)

        # Status 2: Variety Label Banner
        self.variety_card = ctk.CTkFrame(metrics_box, fg_color="#282828", corner_radius=10)
        self.variety_card.pack(fill="x", padx=20, pady=6)

        self.lbl_variety = ctk.CTkLabel(
            self.variety_card,
            text="🏷️ สายพันธุ์ (Variety): ---",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3498db"
        )
        self.lbl_variety.pack(anchor="w", padx=16, pady=12)

        # Status 3: Performance & Confidence Banner
        stats_card = ctk.CTkFrame(metrics_box, fg_color="#282828", corner_radius=10)
        stats_card.pack(fill="x", padx=20, pady=6)

        self.lbl_conf = ctk.CTkLabel(
            stats_card,
            text="ความเชื่อมั่น (Confidence): 0.0%",
            font=ctk.CTkFont(size=13),
            text_color="#aaaaaa"
        )
        self.lbl_conf.pack(anchor="w", padx=16, pady=(10, 3))

        self.lbl_latency = ctk.CTkLabel(
            stats_card,
            text="เวลาประมวลผล (Latency): 0.0 ms",
            font=ctk.CTkFont(size=13),
            text_color="#aaaaaa"
        )
        self.lbl_latency.pack(anchor="w", padx=16, pady=(3, 10))

        # --- 3. Action Control Buttons Bar Inside Card ---
        btn_bar = ctk.CTkFrame(unified_card, fg_color="transparent")
        btn_bar.pack(fill="x", padx=20, pady=(10, 15))

        btn_trainer = ctk.CTkButton(
            btn_bar,
            text="🎓 เทรนและจัดการสายพันธุ์ (Trainer Studio)",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42,
            fg_color="#8e44ad",
            hover_color="#6c3483",
            command=self.open_trainer_studio
        )
        btn_trainer.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_snapshot = ctk.CTkButton(
            btn_bar,
            text="📸 บันทึกภาพเฟรมปัจจุบัน (Snapshot Frame)",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42,
            fg_color="#27ae60",
            hover_color="#219150",
            command=self.on_snapshot
        )
        btn_snapshot.pack(side="right", fill="x", expand=True, padx=(8, 0))

        # Footer Status Label
        self.lbl_sys_info = ctk.CTkLabel(
            unified_card,
            text="● พร้อมประมวลผลข้อมูล (PyTorch CNN Engine Active)",
            font=ctk.CTkFont(size=11),
            text_color="#2ecc71"
        )
        self.lbl_sys_info.pack(pady=(0, 12))

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

        # Update UI Badges & Cards Inside Consolidated Dashboard
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
