"""Main Avocado Ripeness & Variety Inspector Desktop Dashboard (Touchscreen & On-Demand Mode)."""

from enum import Enum
from pathlib import Path
import threading
import time
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Tuple
import cv2
import customtkinter as ctk
import numpy as np
from PIL import Image, ImageTk

from avocado.camera.manager import DualCameraManager
from avocado.config import AppConfig, load_config
from avocado.core.classifier import AvocadoClassifier, ClassificationResult
from avocado.ui.trainer_gui import TrainerLabelerStudio
from avocado.ui.widgets.gauge import GaugeWidget

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AppState(Enum):
    STANDBY = "STANDBY"        # Live preview stream, guide box overlay, no heavy AI load
    ANALYZING = "ANALYZING"    # Frozen frame captured, CNN models computing
    RESULT = "RESULT"          # Displaying frozen analyzed frame, badges, gauge score


class AvocadoApp(ctk.CTk):
    """Desktop dashboard with standby preview, on-demand Capture & Analyze, and Touchscreen Kiosk support."""

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        super().__init__()

        self.config = config or load_config()

        self.title("🥑 Avocado Ripeness & Variety Inspector")
        self.geometry("1180x780")
        self.minsize(800, 480)

        self.classifier = AvocadoClassifier(config=self.config)
        self.cam_manager = DualCameraManager(config=self.config)

        self.inspection_state = AppState.STANDBY
        self.is_running = True
        self.is_fullscreen = False
        self.trainer_win: Optional[TrainerLabelerStudio] = None

        # Frames cache
        self.current_live_frame1: Optional[np.ndarray] = None
        self.current_live_frame2: Optional[np.ndarray] = None
        self.captured_frame1: Optional[np.ndarray] = None
        self.captured_frame2: Optional[np.ndarray] = None

        # Classification results cache
        self.result1: Optional[ClassificationResult] = None
        self.result2: Optional[ClassificationResult] = None

        self.build_ui()
        self.bind_shortcuts()
        self.update_video_loop()

    def bind_shortcuts(self) -> None:
        """Binds Spacebar, Enter, and F11 keys for rapid on-demand capture / reset / fullscreen."""
        self.bind("<space>", lambda event: self.handle_primary_action())
        self.bind("<Return>", lambda event: self.handle_primary_action())
        self.bind("<F11>", lambda event: self.toggle_fullscreen())
        self.bind("<Escape>", lambda event: self.exit_fullscreen())

    def toggle_fullscreen(self) -> None:
        """Toggles fullscreen Kiosk mode for Raspberry Pi touchscreens."""
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)
        if hasattr(self, "btn_fullscreen"):
            self.btn_fullscreen.configure(text="🗗 ย่อหน้าต่าง" if self.is_fullscreen else "⛶ เต็มจอ")

    def exit_fullscreen(self) -> None:
        if self.is_fullscreen:
            self.toggle_fullscreen()

    def build_ui(self) -> None:
        unified_card = ctk.CTkFrame(self, fg_color="#181818", corner_radius=16, border_width=1, border_color="#2c3e50")
        unified_card.pack(fill="both", expand=True, padx=12, pady=12)

        # Header
        header_box = ctk.CTkFrame(unified_card, fg_color="#222222", corner_radius=12)
        header_box.pack(fill="x", padx=14, pady=(14, 6))

        title_label = ctk.CTkLabel(
            header_box,
            text="🥑 Avocado Ripeness & Variety Inspector",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color="#2ecc71",
        )
        title_label.pack(side="left", padx=16, pady=8)

        # Header Right Controls: Fullscreen button + Mode Status
        hdr_right = ctk.CTkFrame(header_box, fg_color="transparent")
        hdr_right.pack(side="right", padx=10, pady=6)

        self.btn_fullscreen = ctk.CTkButton(
            hdr_right,
            text="⛶ เต็มจอ",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=self.toggle_fullscreen,
        )
        self.btn_fullscreen.pack(side="right", padx=(8, 0))

        self.lbl_system_mode = ctk.CTkLabel(
            hdr_right,
            text="● STANDBY (แตะเพื่อถ่าย)",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            text_color="#f1c40f",
        )
        self.lbl_system_mode.pack(side="right", padx=6)

        # Main Layout
        content_box = ctk.CTkFrame(unified_card, fg_color="transparent")
        content_box.pack(fill="both", expand=True, padx=12, pady=4)

        # Left Column: Dual Camera Previews & Ripeness Gauge
        left_box = ctk.CTkFrame(content_box, fg_color="#202020", corner_radius=12, border_width=1, border_color="#333333")
        left_box.pack(side="left", fill="both", expand=True, padx=(0, 6), pady=4)

        cam_container = ctk.CTkFrame(left_box, fg_color="transparent")
        cam_container.pack(fill="both", expand=True, padx=8, pady=4)

        # Camera views with tap-to-capture event binding
        self.lbl_cam1_view = tk.Label(cam_container, bg="#111111", cursor="hand2")
        self.lbl_cam1_view.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        self.lbl_cam1_view.bind("<Button-1>", lambda event: self.handle_primary_action())

        self.lbl_cam2_view = tk.Label(cam_container, bg="#111111", cursor="hand2")
        self.lbl_cam2_view.pack(side="right", fill="both", expand=True, padx=4, pady=4)
        self.lbl_cam2_view.bind("<Button-1>", lambda event: self.handle_primary_action())

        # Gauge Widget (also clickable for touch)
        self.gauge = GaugeWidget(left_box, width=380, height=210, bg="#202020")
        self.gauge.pack(padx=8, pady=(0, 8))
        self.gauge.bind("<Button-1>", lambda event: self.handle_primary_action())

        # Right Column: Inspection Metrics & Touch-Optimized Primary Button
        right_box = ctk.CTkFrame(content_box, width=430, fg_color="#202020", corner_radius=12, border_width=1, border_color="#333333")
        right_box.pack(side="right", fill="y", padx=(6, 0), pady=4)
        right_box.pack_propagate(False)

        # Primary Trigger Action Box (Extra-Large Touch Target)
        trigger_box = ctk.CTkFrame(right_box, fg_color="#282828", corner_radius=12)
        trigger_box.pack(fill="x", padx=14, pady=(12, 6))

        self.btn_action = ctk.CTkButton(
            trigger_box,
            text="📸 แตะเพื่อตรวจวัดความสุก\n(Tap / Click / Spacebar)",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=68,
            corner_radius=10,
            fg_color="#27ae60",
            hover_color="#1e8449",
            command=self.handle_primary_action,
        )
        self.btn_action.pack(fill="x", padx=8, pady=8)

        # Results & Metrics Title
        m_title = ctk.CTkLabel(
            right_box,
            text="📊 ผลการวิเคราะห์ (Inspection Results)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#f39c12",
        )
        m_title.pack(padx=14, pady=(6, 2), anchor="w")

        # Status 1: Ripeness Banner
        self.ripeness_card = ctk.CTkFrame(right_box, fg_color="#282828", corner_radius=10)
        self.ripeness_card.pack(fill="x", padx=14, pady=4)

        self.lbl_main_status = ctk.CTkLabel(
            self.ripeness_card,
            text="🥑 ระดับความสุก: รอการตรวจวัด...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#aaaaaa",
        )
        self.lbl_main_status.pack(anchor="w", padx=12, pady=8)

        # Status 2: Variety Banner
        self.variety_card = ctk.CTkFrame(right_box, fg_color="#282828", corner_radius=10)
        self.variety_card.pack(fill="x", padx=14, pady=4)

        self.lbl_variety = ctk.CTkLabel(
            self.variety_card,
            text="🏷️ สายพันธุ์: ---",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#3498db",
        )
        self.lbl_variety.pack(anchor="w", padx=12, pady=8)

        # Status 3: Confidence & Latency
        stats_card = ctk.CTkFrame(right_box, fg_color="#282828", corner_radius=10)
        stats_card.pack(fill="x", padx=14, pady=4)

        self.lbl_conf = ctk.CTkLabel(
            stats_card,
            text="ความเชื่อมั่น (Confidence): ---",
            font=ctk.CTkFont(size=13),
            text_color="#aaaaaa",
        )
        self.lbl_conf.pack(anchor="w", padx=12, pady=(6, 2))

        self.lbl_latency = ctk.CTkLabel(
            stats_card,
            text="เวลาประมวลผล (Inference): ---",
            font=ctk.CTkFont(size=13),
            text_color="#aaaaaa",
        )
        self.lbl_latency.pack(anchor="w", padx=12, pady=(2, 6))

        # Auxiliary Control Buttons (Comfortable Touch Target)
        btn_aux_frame = ctk.CTkFrame(right_box, fg_color="transparent")
        btn_aux_frame.pack(fill="x", padx=14, pady=(8, 4))

        btn_trainer = ctk.CTkButton(
            btn_aux_frame,
            text="🎓 Trainer Studio",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=42,
            fg_color="#8e44ad",
            hover_color="#6c3483",
            command=self.open_trainer_studio,
        )
        btn_trainer.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_snapshot = ctk.CTkButton(
            btn_aux_frame,
            text="📸 บันทึกภาพ",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=42,
            fg_color="#2980b9",
            hover_color="#1b4f72",
            command=self.on_snapshot,
            state="disabled",
        )
        self.btn_snapshot.pack(side="right", fill="x", expand=True, padx=(4, 0))

        # Footer Status
        self.lbl_sys_info = ctk.CTkLabel(
            right_box,
            text="● แตะที่ปุ่มหรือแตะที่หน้าจอกล้องเพื่อเริ่มตรวจวัด",
            font=ctk.CTkFont(size=11),
            text_color="#aaaaaa",
        )
        self.lbl_sys_info.pack(side="bottom", pady=8)

    def handle_primary_action(self) -> None:
        """Handles toggle between Capture & Analyze and Reset / Next Fruit."""
        if self.inspection_state == AppState.STANDBY:
            self.trigger_capture_and_analyze()
        elif self.inspection_state == AppState.RESULT:
            self.reset_to_standby()

    def trigger_capture_and_analyze(self) -> None:
        """Captures synchronized frame pair and runs CNN inference in background worker."""
        if self.inspection_state == AppState.ANALYZING:
            return

        if self.current_live_frame1 is None or self.current_live_frame2 is None:
            return

        self.inspection_state = AppState.ANALYZING
        self.captured_frame1 = self.current_live_frame1.copy()
        self.captured_frame2 = self.current_live_frame2.copy()

        self.btn_action.configure(
            text="⏳ กำลังวิเคราะห์ภาพ... (Analyzing)",
            state="disabled",
            fg_color="#7f8c8d",
        )
        self.lbl_system_mode.configure(text="● ANALYZING...", text_color="#e67e22")
        self.lbl_sys_info.configure(text="● กำลังตรวจวัดระดับความสุกและจำแนกสายพันธุ์...")

        threading.Thread(target=self._run_analysis_worker, daemon=True).start()

    def _run_analysis_worker(self) -> None:
        t0 = time.time()
        res1 = self.classifier.predict_frame(self.captured_frame1)
        res2 = self.classifier.predict_frame(self.captured_frame2)
        latency_ms = (time.time() - t0) * 1000.0

        self.after(0, lambda: self._on_analysis_complete(res1, res2, latency_ms))

    def _on_analysis_complete(
        self, res1: ClassificationResult, res2: ClassificationResult, latency_ms: float
    ) -> None:
        self.result1 = res1
        self.result2 = res2
        self.inspection_state = AppState.RESULT

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
        self.lbl_latency.configure(text=f"เวลาประมวลผล (Inference): {latency_ms:.1f} ms")

        self.lbl_system_mode.configure(text="● RESULT (แตะเพื่อตรวจผลถัดไป)", text_color="#2ecc71")
        self.btn_action.configure(
            text="🔄 แตะเพื่อตรวจผลถัดไป\n(Reset / Next Fruit)",
            state="normal",
            fg_color="#e67e22",
            hover_color="#d35400",
        )
        self.btn_snapshot.configure(state="normal")
        self.lbl_sys_info.configure(text="● ตรวจวัดเสร็จสิ้น แตะปุ่มเพื่อเริ่มตรวจผลถัดไป")

        self._render_preview_frame(self.lbl_cam1_view, res1.annotated_frame)
        self._render_preview_frame(self.lbl_cam2_view, res2.annotated_frame)

    def reset_to_standby(self) -> None:
        """Resets application back to live standby preview mode."""
        self.inspection_state = AppState.STANDBY
        self.result1 = None
        self.result2 = None
        self.captured_frame1 = None
        self.captured_frame2 = None

        self.gauge.set_score(0.0)
        self.lbl_main_status.configure(text="🥑 ระดับความสุก: รอการตรวจวัด...", text_color="#aaaaaa")
        self.lbl_variety.configure(text="🏷️ สายพันธุ์: ---", text_color="#3498db")
        self.lbl_conf.configure(text="ความเชื่อมั่น (Confidence): ---")
        self.lbl_latency.configure(text="เวลาประมวลผล (Inference): ---")

        self.lbl_system_mode.configure(text="● STANDBY (แตะเพื่อถ่าย)", text_color="#f1c40f")
        self.btn_action.configure(
            text="📸 แตะเพื่อตรวจวัดความสุก\n(Tap / Click / Spacebar)",
            state="normal",
            fg_color="#27ae60",
            hover_color="#1e8449",
        )
        self.btn_snapshot.configure(state="disabled")
        self.lbl_sys_info.configure(text="● แตะที่ปุ่มหรือแตะที่หน้าจอกล้องเพื่อเริ่มตรวจวัด")

    def _render_preview_frame(self, target_label: tk.Label, frame: np.ndarray) -> None:
        """Helper to render BGR numpy image onto Tkinter Label."""
        rgb = cv2.cvtColor(cv2.resize(frame, (320, 240)), cv2.COLOR_BGR2RGB)
        tk_img = ImageTk.PhotoImage(image=Image.fromarray(rgb))
        target_label.configure(image=tk_img)
        target_label.image = tk_img

    def update_video_loop(self) -> None:
        """Continuous camera streaming loop (only streams video in STANDBY with zero inference)."""
        if not self.is_running:
            return

        frame1, frame2 = self.cam_manager.read_frames()
        self.current_live_frame1 = frame1
        self.current_live_frame2 = frame2

        if self.inspection_state == AppState.STANDBY:
            h, w, _ = frame1.shape
            f1_view = frame1.copy()
            f2_view = frame2.copy()

            guide_box = (int(w * 0.25), int(h * 0.15), int(w * 0.5), int(h * 0.7))
            gx, gy, gw, gh = guide_box
            cv2.rectangle(f1_view, (gx, gy), (gx + gw, gy + gh), (0, 255, 255), 2)
            cv2.putText(f1_view, "CAM 1 (Tap to scan)", (gx + 10, gy + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

            cv2.rectangle(f2_view, (gx, gy), (gx + gw, gy + gh), (0, 255, 255), 2)
            cv2.putText(f2_view, "CAM 2 (Tap to scan)", (gx + 10, gy + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

            self._render_preview_frame(self.lbl_cam1_view, f1_view)
            self._render_preview_frame(self.lbl_cam2_view, f2_view)

        self.after(33, self.update_video_loop)

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
        if self.result1 is not None and self.result2 is not None:
            snap_dir = self.config.project_root / "snapshots"
            snap_dir.mkdir(parents=True, exist_ok=True)
            ts = int(time.time())
            fpath1 = snap_dir / f"scan_cam1_{ts}.jpg"
            fpath2 = snap_dir / f"scan_cam2_{ts}.jpg"
            cv2.imwrite(str(fpath1), self.result1.annotated_frame)
            cv2.imwrite(str(fpath2), self.result2.annotated_frame)
            messagebox.showinfo("บันทึกสำเร็จ", f"บันทึกรูปภาพการตรวจวัดเรียบร้อยที่:\n{snap_dir}")

    def on_closing(self) -> None:
        self.is_running = False
        if self.trainer_win:
            try:
                self.trainer_win.on_closing()
            except Exception:
                pass
        self.cam_manager.release()
        self.destroy()
