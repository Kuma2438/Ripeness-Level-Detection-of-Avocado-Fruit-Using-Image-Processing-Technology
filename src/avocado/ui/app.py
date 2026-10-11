"""Main Avocado Ripeness & Variety Inspector Desktop Dashboard with 85.42mm x 55.60mm (480x320 Landscape) Hardware Support."""

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
    STANDBY = "STANDBY"        # Live preview stream, guide box overlay, zero heavy AI load
    ANALYZING = "ANALYZING"    # Frozen frame captured, CNN models computing
    RESULT = "RESULT"          # Displaying frozen analyzed frame, badges, gauge score


class AvocadoApp(ctk.CTk):
    """Desktop & Kiosk dashboard supporting standard desktop displays and compact 85.42mm x 55.60mm (480x320 Landscape) hardware screens."""

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        super().__init__()

        self.config = config or load_config()

        self.title("🥑 Avocado Ripeness & Variety Inspector")

        # Determine display mode: compact landscape (480x320) vs desktop (1180x780)
        mode = getattr(self.config.display, "mode", "auto").lower()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        self.is_compact = (
            mode in ["compact", "compact_landscape", "touchscreen", "hardware"]
            or (mode == "auto" and (screen_w <= 640 or screen_h <= 480))
        )

        if self.is_compact:
            self.geometry("480x320")
            self.minsize(440, 280)
            self.preview_size = (220, 160)
        else:
            self.geometry("1180x780")
            self.minsize(800, 480)
            self.preview_size = (320, 240)

        self.classifier = AvocadoClassifier(config=self.config)
        self.cam_manager = DualCameraManager(config=self.config)

        self.inspection_state = AppState.STANDBY
        self.is_running = True
        self.is_fullscreen = getattr(self.config.display, "fullscreen", False)
        self.active_cam_idx = 1  # For compact mode switching between CAM1 and CAM2
        self.trainer_win: Optional[TrainerLabelerStudio] = None

        # Frames cache (native RGB)
        self.current_live_frame1: Optional[np.ndarray] = None
        self.current_live_frame2: Optional[np.ndarray] = None
        self.captured_frame1: Optional[np.ndarray] = None
        self.captured_frame2: Optional[np.ndarray] = None

        # Classification results cache
        self.result1: Optional[ClassificationResult] = None
        self.result2: Optional[ClassificationResult] = None

        if self.is_fullscreen:
            self.attributes("-fullscreen", True)

        self.build_ui()
        self.bind_shortcuts()
        self.update_video_loop()

    def bind_shortcuts(self) -> None:
        """Binds Spacebar, Enter, Tab, and F11 keys for rapid on-demand capture / reset / camera toggle."""
        self.bind("<space>", lambda event: self.handle_primary_action())
        self.bind("<Return>", lambda event: self.handle_primary_action())
        self.bind("<Tab>", lambda event: self.toggle_active_cam())
        self.bind("<F11>", lambda event: self.toggle_fullscreen())
        self.bind("<Escape>", lambda event: self.exit_fullscreen())

    def toggle_fullscreen(self) -> None:
        """Toggles fullscreen Kiosk mode for hardware touchscreens."""
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)
        if hasattr(self, "btn_fullscreen"):
            self.btn_fullscreen.configure(text="🗗" if self.is_fullscreen else "⛶")

    def exit_fullscreen(self) -> None:
        if self.is_fullscreen:
            self.toggle_fullscreen()

    def toggle_active_cam(self) -> None:
        """Toggles preview between Camera 1 and Camera 2 in compact landscape mode."""
        self.active_cam_idx = 2 if self.active_cam_idx == 1 else 1
        if hasattr(self, "btn_cam_toggle"):
            self.btn_cam_toggle.configure(text=f"📷 CAM {self.active_cam_idx}")

    def build_ui(self) -> None:
        if self.is_compact:
            self._build_compact_ui()
        else:
            self._build_desktop_ui()

    def _build_compact_ui(self) -> None:
        """Compact 480x320 Landscape layout optimized for 85.42 mm x 55.60 mm hardware displays."""
        unified_card = ctk.CTkFrame(self, fg_color="#181818", corner_radius=10, border_width=1, border_color="#2c3e50")
        unified_card.pack(fill="both", expand=True, padx=4, pady=4)

        # Top Bar: Height 28px
        header_box = ctk.CTkFrame(unified_card, fg_color="#202020", height=28, corner_radius=6)
        header_box.pack(fill="x", padx=6, pady=(4, 2))
        header_box.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_box,
            text="🥑 Avocado Inspector",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            text_color="#2ecc71",
        )
        title_label.pack(side="left", padx=8, pady=2)

        self.btn_fullscreen = ctk.CTkButton(
            header_box,
            text="⛶",
            width=28,
            height=22,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#34495e",
            command=self.toggle_fullscreen,
        )
        self.btn_fullscreen.pack(side="right", padx=(4, 6), pady=2)

        self.btn_cam_toggle = ctk.CTkButton(
            header_box,
            text="📷 CAM 1",
            width=70,
            height=22,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#2980b9",
            hover_color="#1b4f72",
            command=self.toggle_active_cam,
        )
        self.btn_cam_toggle.pack(side="right", padx=4, pady=2)

        self.lbl_system_mode = ctk.CTkLabel(
            header_box,
            text="● STANDBY",
            font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
            text_color="#f1c40f",
        )
        self.lbl_system_mode.pack(side="right", padx=6, pady=2)

        # Content Area: Split Left (Camera) & Right (Gauge + Status)
        content_box = ctk.CTkFrame(unified_card, fg_color="transparent")
        content_box.pack(fill="both", expand=True, padx=6, pady=2)

        # Left Column: Video Preview
        left_box = ctk.CTkFrame(content_box, width=230, fg_color="#141414", corner_radius=8)
        left_box.pack(side="left", fill="both", expand=True, padx=(0, 4), pady=2)
        left_box.pack_propagate(False)

        self.lbl_cam1_view = tk.Label(left_box, bg="#0d0d0d", cursor="hand2")
        self.lbl_cam1_view.pack(fill="both", expand=True, padx=2, pady=2)
        self.lbl_cam1_view.bind("<Button-1>", lambda event: self.handle_primary_action())

        # Placeholder label for camera 2 in compact mode
        self.lbl_cam2_view = self.lbl_cam1_view

        # Right Column: Status & Gauge
        right_box = ctk.CTkFrame(content_box, width=220, fg_color="#1e1e1e", corner_radius=8)
        right_box.pack(side="right", fill="both", expand=True, padx=(4, 0), pady=2)
        right_box.pack_propagate(False)

        self.lbl_main_status = ctk.CTkLabel(
            right_box,
            text="🥑 ความสุก: รอตรวจวัด...",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#aaaaaa",
        )
        self.lbl_main_status.pack(anchor="w", padx=8, pady=(4, 0))

        self.lbl_variety = ctk.CTkLabel(
            right_box,
            text="🏷️ สายพันธุ์: ---",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#3498db",
        )
        self.lbl_variety.pack(anchor="w", padx=8, pady=(0, 2))

        # Compact Gauge Widget
        self.gauge = GaugeWidget(right_box, width=200, height=125, bg="#1e1e1e")
        self.gauge.pack(padx=4, pady=0)
        self.gauge.bind("<Button-1>", lambda event: self.handle_primary_action())

        # Bottom Bar: Large Touch Trigger Action Button (Height 46px)
        self.btn_action = ctk.CTkButton(
            unified_card,
            text="📸 แตะเพื่อตรวจวัด (Tap to Scan)",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=46,
            corner_radius=8,
            fg_color="#27ae60",
            hover_color="#1e8449",
            command=self.handle_primary_action,
        )
        self.btn_action.pack(fill="x", padx=6, pady=(2, 4))

        # Helper metrics stored as hidden/accessible attributes
        self.lbl_conf = ctk.CTkLabel(unified_card, text="")
        self.lbl_latency = ctk.CTkLabel(unified_card, text="")
        self.lbl_sys_info = ctk.CTkLabel(unified_card, text="")
        self.btn_snapshot = ctk.CTkButton(unified_card, text="", state="disabled")

    def _build_desktop_ui(self) -> None:
        """Full 1180x780 Desktop layout with Dual Camera Previews."""
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

        self.lbl_cam1_view = tk.Label(cam_container, bg="#111111", cursor="hand2")
        self.lbl_cam1_view.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        self.lbl_cam1_view.bind("<Button-1>", lambda event: self.handle_primary_action())

        self.lbl_cam2_view = tk.Label(cam_container, bg="#111111", cursor="hand2")
        self.lbl_cam2_view.pack(side="right", fill="both", expand=True, padx=4, pady=4)
        self.lbl_cam2_view.bind("<Button-1>", lambda event: self.handle_primary_action())

        self.gauge = GaugeWidget(left_box, width=380, height=210, bg="#202020")
        self.gauge.pack(padx=8, pady=(0, 8))
        self.gauge.bind("<Button-1>", lambda event: self.handle_primary_action())

        # Right Column: Metrics & Trigger Action Box
        right_box = ctk.CTkFrame(content_box, width=430, fg_color="#202020", corner_radius=12, border_width=1, border_color="#333333")
        right_box.pack(side="right", fill="y", padx=(6, 0), pady=4)
        right_box.pack_propagate(False)

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

        m_title = ctk.CTkLabel(
            right_box,
            text="📊 ผลการวิเคราะห์ (Inspection Results)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#f39c12",
        )
        m_title.pack(padx=14, pady=(6, 2), anchor="w")

        self.ripeness_card = ctk.CTkFrame(right_box, fg_color="#282828", corner_radius=10)
        self.ripeness_card.pack(fill="x", padx=14, pady=4)

        self.lbl_main_status = ctk.CTkLabel(
            self.ripeness_card,
            text="🥑 ระดับความสุก: รอการตรวจวัด...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#aaaaaa",
        )
        self.lbl_main_status.pack(anchor="w", padx=12, pady=8)

        self.variety_card = ctk.CTkFrame(right_box, fg_color="#282828", corner_radius=10)
        self.variety_card.pack(fill="x", padx=14, pady=4)

        self.lbl_variety = ctk.CTkLabel(
            self.variety_card,
            text="🏷️ สายพันธุ์: ---",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#3498db",
        )
        self.lbl_variety.pack(anchor="w", padx=12, pady=8)

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

        btn_text = "⏳ กำลังวิเคราะห์ภาพ..." if not self.is_compact else "⏳ กำลังวิเคราะห์..."
        self.btn_action.configure(
            text=btn_text,
            state="disabled",
            fg_color="#7f8c8d",
        )
        self.lbl_system_mode.configure(text="● ANALYZING...", text_color="#e67e22")

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

        # Case 1: Empty Scan Box on Both Views
        if res1.status == "NO_AVOCADO" and res2.status == "NO_AVOCADO":
            self.gauge.set_inactive("--%", "NO AVOCADO (ไม่พบอะโวคาโด)", "#888888")
            status_text = "❌ ไม่พบอะโวคาโด (No Avocado)" if self.is_compact else "❌ ไม่พบอะโวคาโด (No Avocado Detected)"
            self.lbl_main_status.configure(text=f"🥑 ระดับความสุก: {status_text}", text_color="#aaaaaa")
            self.lbl_variety.configure(text="🏷️ สายพันธุ์: ---", text_color="#888888")
            self.lbl_conf.configure(text="ความเชื่อมั่น (Confidence): ---")

        # Case 2: Foreign Object (Not Avocado) on Either View with No Valid Detection
        elif (res1.status == "NOT_AVOCADO" or res2.status == "NOT_AVOCADO") and not (
            res1.status == "DETECTED" or res2.status == "DETECTED"
        ):
            self.gauge.set_inactive("--%", "NOT AN AVOCADO (ไม่ใช่อะโวคาโด)", "#e67e22")
            status_text = "⚠️ ไม่ใช่อะโวคาโด (Not Avocado)" if self.is_compact else "⚠️ ไม่ใช่อะโวคาโด (Not an Avocado Detected)"
            self.lbl_main_status.configure(text=f"🥑 ระดับความสุก: {status_text}", text_color="#e67e22")
            self.lbl_variety.configure(text="🏷️ สายพันธุ์: ---", text_color="#888888")
            self.lbl_conf.configure(text="ความเชื่อมั่น (Confidence): ---")

        # Case 3: Valid Avocado Detected on One or Both Cameras
        else:
            valid_scores = [r.score for r in [res1, res2] if r.status == "DETECTED" and r.score is not None]
            valid_confs = [r.confidence for r in [res1, res2] if r.status == "DETECTED"]
            primary_res = res1 if res1.status == "DETECTED" else res2

            avg_score = float(np.mean(valid_scores)) if valid_scores else 50.0
            avg_conf = float(np.mean(valid_confs)) if valid_confs else 85.0

            self.gauge.set_score(avg_score)

            status_th = {
                "Unripe": "ดิบ (Unripe)",
                "Mid-ripe": "กึ่งสุก (Mid-ripe)",
                "Ripe": "สุก (Ripe)",
            }.get(primary_res.category, primary_res.category)
            status_colors = {"Unripe": "#2ecc71", "Mid-ripe": "#f39c12", "Ripe": "#e74c3c"}

            self.lbl_main_status.configure(
                text=f"🥑 ระดับความสุก: {status_th}",
                text_color=status_colors.get(primary_res.category, "#ffffff"),
            )
            self.lbl_variety.configure(
                text=f"🏷️ สายพันธุ์: {primary_res.variety_name} ({primary_res.variety_confidence:.0f}%)",
                text_color="#3498db",
            )
            self.lbl_conf.configure(text=f"ความเชื่อมั่น (Confidence): {avg_conf:.1f}%")

        self.lbl_latency.configure(text=f"เวลาประมวลผล (Inference): {latency_ms:.1f} ms")
        self.lbl_system_mode.configure(text="● RESULT", text_color="#2ecc71")

        next_btn_text = "🔄 แตะเพื่อตรวจผลถัดไป" if self.is_compact else "🔄 แตะเพื่อตรวจผลถัดไป\n(Reset / Next Fruit)"
        self.btn_action.configure(
            text=next_btn_text,
            state="normal",
            fg_color="#e67e22",
            hover_color="#d35400",
        )
        self.btn_snapshot.configure(state="normal")

        # Render analyzed frame
        if self.is_compact:
            target_res = res1 if self.active_cam_idx == 1 else res2
            self._render_preview_frame(self.lbl_cam1_view, target_res.annotated_frame)
        else:
            self._render_preview_frame(self.lbl_cam1_view, res1.annotated_frame)
            self._render_preview_frame(self.lbl_cam2_view, res2.annotated_frame)

    def reset_to_standby(self) -> None:
        """Resets application back to live standby preview mode."""
        self.inspection_state = AppState.STANDBY
        self.result1 = None
        self.result2 = None
        self.captured_frame1 = None
        self.captured_frame2 = None

        self.gauge.set_score(None)
        self.lbl_main_status.configure(text="🥑 ระดับความสุก: รอการตรวจวัด...", text_color="#aaaaaa")
        self.lbl_variety.configure(text="🏷️ สายพันธุ์: ---", text_color="#3498db")
        self.lbl_conf.configure(text="ความเชื่อมั่น (Confidence): ---")
        self.lbl_latency.configure(text="เวลาประมวลผล (Inference): ---")

        self.lbl_system_mode.configure(text="● STANDBY", text_color="#f1c40f")

        scan_text = "📸 แตะเพื่อตรวจวัด (Tap to Scan)" if self.is_compact else "📸 แตะเพื่อตรวจวัดความสุก\n(Tap / Click / Spacebar)"
        self.btn_action.configure(
            text=scan_text,
            state="normal",
            fg_color="#27ae60",
            hover_color="#1e8449",
        )
        self.btn_snapshot.configure(state="disabled")

    def _render_preview_frame(self, target_label: tk.Label, frame_rgb: np.ndarray) -> None:
        """Helper to render native RGB numpy image directly onto Tkinter Label."""
        resized = cv2.resize(frame_rgb, self.preview_size)
        tk_img = ImageTk.PhotoImage(image=Image.fromarray(resized))
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
            gx, gy, gw, gh = int(w * 0.25), int(h * 0.15), int(w * 0.5), int(h * 0.7)

            if self.is_compact:
                active_frame = frame1 if self.active_cam_idx == 1 else frame2
                f_view = active_frame.copy()
                # Guide box in native RGB yellow (255, 255, 0)
                cv2.rectangle(f_view, (gx, gy), (gx + gw, gy + gh), (255, 255, 0), 2)
                cv2.putText(
                    f_view,
                    f"CAM {self.active_cam_idx} (Tap to scan)",
                    (gx + 8, gy + 22),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.50,
                    (255, 255, 0),
                    2,
                )
                self._render_preview_frame(self.lbl_cam1_view, f_view)
            else:
                f1_view = frame1.copy()
                f2_view = frame2.copy()
                cv2.rectangle(f1_view, (gx, gy), (gx + gw, gy + gh), (255, 255, 0), 2)
                cv2.putText(f1_view, "CAM 1 (Tap to scan)", (gx + 10, gy + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)

                cv2.rectangle(f2_view, (gx, gy), (gx + gw, gy + gh), (255, 255, 0), 2)
                cv2.putText(f2_view, "CAM 2 (Tap to scan)", (gx + 10, gy + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)

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
            # Save snapshots converting RGB back to BGR for cv2.imwrite
            cv2.imwrite(str(fpath1), cv2.cvtColor(self.result1.annotated_frame, cv2.COLOR_RGB2BGR))
            cv2.imwrite(str(fpath2), cv2.cvtColor(self.result2.annotated_frame, cv2.COLOR_RGB2BGR))
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
