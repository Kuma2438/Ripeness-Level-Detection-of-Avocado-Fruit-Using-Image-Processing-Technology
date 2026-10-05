"""Main Avocado Ripeness & Variety Inspector Desktop Dashboard."""

from pathlib import Path
import time
import tkinter as tk
from tkinter import messagebox
from typing import Optional
import cv2
import customtkinter as ctk
import numpy as np
from PIL import Image, ImageTk

from avocado.camera.manager import DualCameraManager
from avocado.config import AppConfig, get_project_root, load_config
from avocado.core.classifier import AvocadoClassifier
from avocado.ui.trainer_gui import TrainerLabelerStudio
from avocado.ui.widgets.gauge import GaugeWidget

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AvocadoApp(ctk.CTk):
    """Main desktop application window for dual-camera avocado ripeness & variety inspection."""

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        super().__init__()

        self.config = config or load_config()

        self.title("🥑 Avocado Ripeness & Variety Inspection Dashboard")
        self.geometry("1180x760")
        self.minsize(980, 640)

        self.classifier = AvocadoClassifier(config=self.config)
        self.cam_manager = DualCameraManager(config=self.config)

        self.is_running = True
        self.trainer_win: Optional[TrainerLabelerStudio] = None
        self.current_ann_frame: Optional[np.ndarray] = None

        self.build_ui()
        self.update_loop()

    def build_ui(self) -> None:
        unified_card = ctk.CTkFrame(self, fg_color="#181818", corner_radius=16, border_width=1, border_color="#2c3e50")
        unified_card.pack(fill="both", expand=True, padx=16, pady=16)

        # Header
        header_box = ctk.CTkFrame(unified_card, fg_color="#222222", corner_radius=12)
        header_box.pack(fill="x", padx=16, pady=(16, 10))

        title_label = ctk.CTkLabel(
            header_box,
            text="🥑 Avocado Ripeness & Variety Inspector (Raspberry Pi 5 & Desktop)",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color="#2ecc71",
        )
        title_label.pack(side="left", padx=16, pady=10)

        self.lbl_cam_status = ctk.CTkLabel(
            header_box,
            text="● Dual USB Cameras Active",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            text_color="#2ecc71",
        )
        self.lbl_cam_status.pack(side="right", padx=16, pady=10)

        # Content Split: Left (Cameras & Gauge), Right (Prediction Results & Controls)
        content_box = ctk.CTkFrame(unified_card, fg_color="transparent")
        content_box.pack(fill="both", expand=True, padx=16, pady=5)

        # Left Column: Video Preview & Gauge
        left_box = ctk.CTkFrame(content_box, fg_color="#202020", corner_radius=12, border_width=1, border_color="#333333")
        left_box.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=5)

        # Video previews container
        cam_container = ctk.CTkFrame(left_box, fg_color="transparent")
        cam_container.pack(fill="both", expand=True, padx=10, pady=5)

        self.lbl_cam1_view = tk.Label(cam_container, bg="#111111")
        self.lbl_cam1_view.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        self.lbl_cam2_view = tk.Label(cam_container, bg="#111111")
        self.lbl_cam2_view.pack(side="right", fill="both", expand=True, padx=4, pady=4)

        # Gauge Widget
        self.gauge = GaugeWidget(left_box, width=380, height=210, bg="#202020")
        self.gauge.pack(padx=10, pady=(0, 10))

        # Right Column: Metrics & Results
        metrics_box = ctk.CTkFrame(content_box, width=420, fg_color="#202020", corner_radius=12, border_width=1, border_color="#333333")
        metrics_box.pack(side="right", fill="y", padx=(8, 0), pady=5)
        metrics_box.pack_propagate(False)

        m_title = ctk.CTkLabel(
            metrics_box,
            text="📊 CNN Live Inspection Results",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f39c12",
        )
        m_title.pack(padx=16, pady=(15, 8), anchor="w")

        # Ripeness Status Card
        self.ripeness_card = ctk.CTkFrame(metrics_box, fg_color="#282828", corner_radius=10)
        self.ripeness_card.pack(fill="x", padx=16, pady=6)

        self.lbl_main_status = ctk.CTkLabel(
            self.ripeness_card,
            text="🥑 ระดับความสุก: กำลังประมวลผล...",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#ffffff",
        )
        self.lbl_main_status.pack(anchor="w", padx=14, pady=10)

        # Variety Status Card
        self.variety_card = ctk.CTkFrame(metrics_box, fg_color="#282828", corner_radius=10)
        self.variety_card.pack(fill="x", padx=16, pady=6)

        self.lbl_variety = ctk.CTkLabel(
            self.variety_card,
            text="🏷️ สายพันธุ์ (Variety): ---",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#3498db",
        )
        self.lbl_variety.pack(anchor="w", padx=14, pady=10)

        # Metrics Card
        stats_card = ctk.CTkFrame(metrics_box, fg_color="#282828", corner_radius=10)
        stats_card.pack(fill="x", padx=16, pady=6)

        self.lbl_conf = ctk.CTkLabel(
            stats_card,
            text="ความเชื่อมั่น (Confidence): 0.0%",
            font=ctk.CTkFont(size=13),
            text_color="#aaaaaa",
        )
        self.lbl_conf.pack(anchor="w", padx=14, pady=(8, 2))

        self.lbl_latency = ctk.CTkLabel(
            stats_card,
            text="เวลาประมวลผล (Latency): 0.0 ms",
            font=ctk.CTkFont(size=13),
            text_color="#aaaaaa",
        )
        self.lbl_latency.pack(anchor="w", padx=14, pady=(2, 8))

        # Control Buttons
        btn_trainer = ctk.CTkButton(
            metrics_box,
            text="🎓 Trainer & Labeler Studio",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            fg_color="#8e44ad",
            hover_color="#6c3483",
            command=self.open_trainer_studio,
        )
        btn_trainer.pack(fill="x", padx=16, pady=(15, 6))

        btn_snapshot = ctk.CTkButton(
            metrics_box,
            text="📸 Snapshot Frames",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            fg_color="#27ae60",
            hover_color="#219150",
            command=self.on_snapshot,
        )
        btn_snapshot.pack(fill="x", padx=16, pady=6)

        self.lbl_sys_info = ctk.CTkLabel(
            metrics_box,
            text="● PyTorch CNN Engine Active",
            font=ctk.CTkFont(size=11),
            text_color="#2ecc71",
        )
        self.lbl_sys_info.pack(side="bottom", pady=12)

    def open_trainer_studio(self) -> None:
        if self.trainer_win is None or not self.trainer_win.winfo_exists():
            self.trainer_win = TrainerLabelerStudio(parent=self, config=self.config)
            self.trainer_win.protocol("WM_DELETE_WINDOW", self.on_trainer_closed)
        else:
            self.trainer_win.focus()

    def on_trainer_closed(self) -> None:
        if self.trainer_win:
            self.trainer_win.on_closing()
            self.trainer_win = None
        self.classifier.variety_trainer.load_or_train()
        self.lbl_sys_info.configure(text="● โหลดโมเดลสายพันธุ์ใหม่เรียบร้อยแล้ว!", text_color="#f1c40f")

    def on_snapshot(self) -> None:
        if self.current_ann_frame is not None:
            snap_dir = self.config.project_root / "snapshots"
            snap_dir.mkdir(parents=True, exist_ok=True)
            fname = f"snapshot_{int(time.time())}.jpg"
            fpath = snap_dir / fname
            cv2.imwrite(str(fpath), self.current_ann_frame)
            messagebox.showinfo("บันทึกสำเร็จ", f"บันทึกรูปภาพเรียบร้อยที่:\n{fpath}")

    def update_loop(self) -> None:
        if not self.is_running:
            return

        start_t = time.time()
        frame1, frame2 = self.cam_manager.read_frames()

        res1 = self.classifier.predict_frame(frame1)
        res2 = self.classifier.predict_frame(frame2)

        self.current_ann_frame = res1.annotated_frame

        latency_ms = (time.time() - start_t) * 1000.0
        avg_score = (res1.score + res2.score) / 2.0
        avg_conf = (res1.confidence + res2.confidence) / 2.0

        self.gauge.set_score(avg_score)

        status_th = {"Unripe": "ดิบ (Unripe)", "Mid-ripe": "กึ่งสุก (Mid-ripe)", "Ripe": "สุก (Ripe)"}.get(
            res1.category, res1.category
        )
        status_colors = {"Unripe": "#2ecc71", "Mid-ripe": "#f39c12", "Ripe": "#e74c3c"}

        self.lbl_main_status.configure(
            text=f"🥑 ระดับความสุก: {status_th}",
            text_color=status_colors.get(res1.category, "#ffffff"),
        )
        self.lbl_variety.configure(
            text=f"🏷️ สายพันธุ์: {res1.variety_name} ({res1.variety_confidence:.0f}%)",
            text_color="#3498db",
        )
        self.lbl_conf.configure(text=f"ความเชื่อมั่น (Confidence): {avg_conf:.1f}%")
        self.lbl_latency.configure(text=f"เวลาประมวลผล (Latency): {latency_ms:.1f} ms")

        # Update preview frames
        img1_rgb = cv2.cvtColor(cv2.resize(res1.annotated_frame, (320, 240)), cv2.COLOR_BGR2RGB)
        tk_img1 = ImageTk.PhotoImage(image=Image.fromarray(img1_rgb))
        self.lbl_cam1_view.configure(image=tk_img1)
        self.lbl_cam1_view.image = tk_img1

        img2_rgb = cv2.cvtColor(cv2.resize(res2.annotated_frame, (320, 240)), cv2.COLOR_BGR2RGB)
        tk_img2 = ImageTk.PhotoImage(image=Image.fromarray(img2_rgb))
        self.lbl_cam2_view.configure(image=tk_img2)
        self.lbl_cam2_view.image = tk_img2

        self.after(30, self.update_loop)

    def on_closing(self) -> None:
        self.is_running = False
        if self.trainer_win:
            try:
                self.trainer_win.on_closing()
            except Exception:
                pass
        self.cam_manager.release()
        self.destroy()
