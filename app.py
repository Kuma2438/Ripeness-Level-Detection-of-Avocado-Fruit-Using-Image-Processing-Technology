import os
import sys
import time
import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk

from avocado_classifier import AvocadoClassifier
from gauge_widget import GaugeWidget
from camera_manager import DualCameraManager
from generate_dataset import generate_sample_dataset
from trainer_gui import TrainerLabelerStudio

# CustomTkinter Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AvocadoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🥑 ระบบตรวจวัดระดับความสุกและสายพันธุ์อะโวคาโด (Dual Camera Avocado Inspector)")
        self.geometry("1320x780")
        self.minsize(1080, 700)

        # Dataset initialization
        self.dataset_dir = r"d:\Project\program\dataset"
        self.variety_dir = r"d:\Project\dataset\varieties"
        
        if not os.path.exists(self.dataset_dir):
            generate_sample_dataset(self.dataset_dir)

        # ML Engine & Dual Camera Manager
        self.classifier = AvocadoClassifier(dataset_dir=self.dataset_dir, variety_dir=self.variety_dir)
        self.cam_manager = DualCameraManager(self.dataset_dir)
        
        self.view_mode = "split" # "split", "cam1", "cam2"
        self.is_running = True
        self.trainer_win = None

        self.build_ui()
        self.update_loop()

    def build_ui(self):
        # 1. Header Frame
        header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1e1e1e")
        header_frame.pack(fill="x", padx=15, pady=(15, 5))

        title_label = ctk.CTkLabel(
            header_frame, 
            text="🥑 ระบบตรวจวัดระดับความสุกและจำแนกสายพันธุ์อะโวคาโด (Real-Time Avocado Inspector)",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color="#2ecc71"
        )
        title_label.pack(side="left", padx=20, pady=12)

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Edge-AI Multi-Feature System (Raspberry Pi 4 / PC)",
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color="#888888"
        )
        subtitle_label.pack(side="right", padx=20, pady=12)

        # 2. Main Content Frame (Split Left: Dual Video, Right: Gauge & Analytics)
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=15, pady=5)

        # --- Left Panel: Video Display ---
        left_panel = ctk.CTkFrame(main_content, fg_color="#181818", corner_radius=10)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=5)

        video_header = ctk.CTkFrame(left_panel, fg_color="transparent")
        video_header.pack(fill="x", padx=15, pady=8)

        v_title = ctk.CTkLabel(
            video_header,
            text="📹 หน้าจอแสดงผลเรียลไทม์จากกล้อง (Live Dual Video Feeds)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        v_title.pack(side="left")

        # Camera Mode Switcher
        self.btn_mode = ctk.CTkSegmentedButton(
            video_header,
            values=["Split View (2 กล้อง)", "Cam 1 (Top)", "Cam 2 (Side)"],
            command=self.change_view_mode,
            selected_color="#27ae60"
        )
        self.btn_mode.set("Split View (2 กล้อง)")
        self.btn_mode.pack(side="right")

        # Video Containers Frame
        self.video_container = ctk.CTkFrame(left_panel, fg_color="#000000", corner_radius=8)
        self.video_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.cam1_label = tk.Label(self.video_container, bg="#000000")
        self.cam2_label = tk.Label(self.video_container, bg="#000000")
        
        self.cam1_label.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        self.cam2_label.pack(side="right", fill="both", expand=True, padx=2, pady=2)

        # --- Right Panel: Gauge & Metrics ---
        right_panel = ctk.CTkFrame(main_content, width=390, fg_color="#181818", corner_radius=10)
        right_panel.pack(side="right", fill="y", padx=(8, 0), pady=5)
        right_panel.pack_propagate(False)

        gauge_title = ctk.CTkLabel(
            right_panel,
            text="🎯 เกจวัดระดับความสุก (Ripeness Gauge)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#2ecc71"
        )
        gauge_title.pack(padx=15, pady=(12, 2))

        # Canvas Gauge Widget
        self.gauge = GaugeWidget(right_panel, width=340, height=210, bg="#181818")
        self.gauge.pack(padx=10, pady=2)

        # Status Cards Frame
        cards_frame = ctk.CTkFrame(right_panel, fg_color="#222222", corner_radius=8)
        cards_frame.pack(fill="x", padx=15, pady=8)

        # Metric 0: Variety Label
        self.lbl_variety = ctk.CTkLabel(
            cards_frame,
            text="🏷️ สายพันธุ์ (Variety): ---",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#3498db"
        )
        self.lbl_variety.pack(anchor="w", padx=15, pady=(8, 3))

        # Metric 1: Ripeness Status
        self.lbl_status = ctk.CTkLabel(
            cards_frame,
            text="🥑 ระดับความสุก: ---",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#ffffff"
        )
        self.lbl_status.pack(anchor="w", padx=15, pady=3)

        # Metric 2: Confidence
        self.lbl_conf = ctk.CTkLabel(
            cards_frame,
            text="ความเชื่อมั่น (Confidence): 0.0%",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa"
        )
        self.lbl_conf.pack(anchor="w", padx=15, pady=2)

        # Metric 3: Processing Latency
        self.lbl_latency = ctk.CTkLabel(
            cards_frame,
            text="เวลาประมวลผล (Latency): 0.0 ms",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa"
        )
        self.lbl_latency.pack(anchor="w", padx=15, pady=(2, 8))

        # Action Buttons
        btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=5)

        btn_trainer = ctk.CTkButton(
            btn_frame,
            text="🎓 เทรนและจัดการสายพันธุ์ (Train & Label Studio)",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8e44ad",
            hover_color="#6c3483",
            command=self.open_trainer_studio
        )
        btn_trainer.pack(fill="x", pady=4)

        btn_gen_ds = ctk.CTkButton(
            btn_frame,
            text="⚡ สุ่ม Dataset ความสุกจำลอง",
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=self.on_generate_dataset
        )
        btn_gen_ds.pack(fill="x", pady=4)

        btn_snap = ctk.CTkButton(
            btn_frame,
            text="📷 บันทึกภาพผลการตรวจ (Snapshot)",
            fg_color="#27ae60",
            hover_color="#219150",
            command=self.on_snapshot
        )
        btn_snap.pack(fill="x", pady=4)

        # System Status Footer Inside Right Panel
        self.lbl_sys_info = ctk.CTkLabel(
            right_panel,
            text="● ระบบพร้อมทำงาน (Edge-AI Active)",
            font=ctk.CTkFont(size=11),
            text_color="#2ecc71"
        )
        self.lbl_sys_info.pack(side="bottom", pady=10)

    def change_view_mode(self, value):
        if "Split" in value:
            self.view_mode = "split"
            self.cam1_label.pack(side="left", fill="both", expand=True, padx=2, pady=2)
            self.cam2_label.pack(side="right", fill="both", expand=True, padx=2, pady=2)
        elif "Cam 1" in value:
            self.view_mode = "cam1"
            self.cam2_label.pack_forget()
            self.cam1_label.pack(fill="both", expand=True, padx=2, pady=2)
        else:
            self.view_mode = "cam2"
            self.cam1_label.pack_forget()
            self.cam2_label.pack(fill="both", expand=True, padx=2, pady=2)

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

    def on_generate_dataset(self):
        generate_sample_dataset(self.dataset_dir)
        self.classifier.train_model()
        self.lbl_sys_info.configure(text="● สุ่ม Dataset จำลองเรียบร้อยแล้ว!", text_color="#f1c40f")

    def on_snapshot(self):
        # Save snapshot image
        if hasattr(self, "current_ann1") and self.current_ann1 is not None:
            os.makedirs(r"d:\Project\snapshots", exist_ok=True)
            fname = f"snapshot_{int(time.time())}.jpg"
            fpath = os.path.join(r"d:\Project\snapshots", fname)
            cv2.imwrite(fpath, self.current_ann1)
            self.lbl_sys_info.configure(text=f"● บันทึกภาพสำเร็จ: {fname}", text_color="#2ecc71")

    def update_loop(self):
        if not self.is_running:
            return

        start_t = time.time()
        
        # Read Dual Camera Frames
        frame1, frame2 = self.cam_manager.read_frames()

        # Classify Avocado Ripeness AND Variety on Cam 1 & Cam 2
        ann1, cat1, score1, conf1, var1, var_conf1 = self.classifier.predict_frame(frame1)
        ann2, cat2, score2, conf2, var2, var_conf2 = self.classifier.predict_frame(frame2)

        self.current_ann1 = ann1

        latency_ms = (time.time() - start_t) * 1000.0

        # Average Gauge score from both cameras
        avg_score = (score1 + score2) / 2.0
        avg_conf = (conf1 + conf2) / 2.0

        # Update Gauge & Metric UI
        self.gauge.set_score(avg_score)
        
        status_th = {"Unripe": "ดิบ (Unripe)", "Mid-ripe": "กึ่งสุก (Mid-ripe)", "Ripe": "สุก (Ripe)"}.get(cat1, cat1)
        status_colors = {"Unripe": "#2ecc71", "Mid-ripe": "#f39c12", "Ripe": "#e74c3c"}
        
        self.lbl_variety.configure(text=f"🏷️ สายพันธุ์: {var1} ({var_conf1:.0f}%)", text_color="#3498db")
        self.lbl_status.configure(text=f"🥑 ระดับความสุก: {status_th}", text_color=status_colors.get(cat1, "#ffffff"))
        self.lbl_conf.configure(text=f"ความเชื่อมั่น (Confidence): {avg_conf:.1f}%")
        self.lbl_latency.configure(text=f"เวลาประมวลผล (Latency): {latency_ms:.1f} ms")

        # Convert OpenCV BGR to Tkinter Image
        if self.view_mode in ["split", "cam1"]:
            img1 = Image.fromarray(cv2.cvtColor(ann1, cv2.COLOR_BGR2RGB))
            img1 = img1.resize((520, 390), Image.Resampling.BILINEAR)
            tk_img1 = ImageTk.PhotoImage(image=img1)
            self.cam1_label.configure(image=tk_img1)
            self.cam1_label.image = tk_img1

        if self.view_mode in ["split", "cam2"]:
            img2 = Image.fromarray(cv2.cvtColor(ann2, cv2.COLOR_BGR2RGB))
            img2 = img2.resize((520, 390), Image.Resampling.BILINEAR)
            tk_img2 = ImageTk.PhotoImage(image=img2)
            self.cam2_label.configure(image=tk_img2)
            self.cam2_label.image = tk_img2

        # Refresh loop every ~30ms (approx 30 FPS)
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
    app = AvocadoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
