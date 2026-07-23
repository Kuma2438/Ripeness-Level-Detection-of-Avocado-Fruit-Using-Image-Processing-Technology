import os
import sys
import time
import cv2
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox

from avocado_classifier import AvocadoClassifier
from gauge_widget import GaugeWidget
from generate_dataset import generate_sample_dataset
from trainer_gui import TrainerLabelerStudio

# CustomTkinter Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AvocadoImageInspectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🥑 ระบบวิเคราะห์ภาพถ่าย อะโวคาโด (Avocado Variety & Ripeness Image Inspector)")
        self.geometry("1240x760")
        self.minsize(1024, 680)

        # Dataset & Model Initialization
        self.dataset_dir = r"d:\Project\program\dataset"
        self.variety_dir = r"d:\Project\dataset\varieties"
        
        if not os.path.exists(self.dataset_dir):
            generate_sample_dataset(self.dataset_dir)

        # ML Engine
        self.classifier = AvocadoClassifier(dataset_dir=self.dataset_dir, variety_dir=self.variety_dir)
        
        self.current_img_path = None
        self.current_raw_img = None
        self.current_ann_img = None
        self.trainer_win = None

        self.build_ui()
        
        # Load initial sample image if available
        self.load_default_sample()

    def build_ui(self):
        # 1. Header Frame
        header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1e1e1e")
        header_frame.pack(fill="x", padx=15, pady=(15, 5))

        title_label = ctk.CTkLabel(
            header_frame, 
            text="🥑 ระบบวิเคราะห์ภาพถ่าย อะโวคาโด (Avocado Variety & Ripeness Image Inspector)",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color="#2ecc71"
        )
        title_label.pack(side="left", padx=20, pady=12)

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Static Image Inspection Engine",
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color="#888888"
        )
        subtitle_label.pack(side="right", padx=20, pady=12)

        # 2. Main Content Frame (Split Left: Image Display & Select, Right: Gauge & Analytics)
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=15, pady=5)

        # --- Left Panel: Image Display & File Chooser ---
        left_panel = ctk.CTkFrame(main_content, fg_color="#181818", corner_radius=10)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=5)

        img_header = ctk.CTkFrame(left_panel, fg_color="transparent")
        img_header.pack(fill="x", padx=15, pady=8)

        v_title = ctk.CTkLabel(
            img_header,
            text="🖼️ ภาพถ่ายอะโวคาโดที่นำมาวิเคราะห์ (Analyzed Image Preview)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        v_title.pack(side="left")

        self.btn_browse = ctk.CTkButton(
            img_header,
            text="📁 เลือกรูปภาพ... (Browse Image)",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2980b9",
            hover_color="#1b4f72",
            command=self.on_browse_image
        )
        self.btn_browse.pack(side="right")

        # Image Container Box
        self.image_container = ctk.CTkFrame(left_panel, fg_color="#000000", corner_radius=8)
        self.image_container.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.img_label = tk.Label(self.image_container, bg="#000000", text="กรุณากดเลือกไฟล์รูปภาพอะโวคาโด", fg="#888888")
        self.img_label.pack(fill="both", expand=True, padx=5, pady=5)

        # Quick Sample Selector Bar
        sample_bar = ctk.CTkFrame(left_panel, fg_color="transparent")
        sample_bar.pack(fill="x", padx=15, pady=(0, 12))

        lbl_quick = ctk.CTkLabel(sample_bar, text="ตัวอย่างสุ่มทดสอบ:", font=ctk.CTkFont(size=12), text_color="#aaaaaa")
        lbl_quick.pack(side="left", padx=(0, 10))

        btn_sample_unripe = ctk.CTkButton(sample_bar, text="🥑 ดิบ (Unripe)", width=100, fg_color="#27ae60", command=lambda: self.load_category_sample("unripe"))
        btn_sample_unripe.pack(side="left", padx=4)

        btn_sample_mid = ctk.CTkButton(sample_bar, text="🥑 กึ่งสุก (Mid)", width=100, fg_color="#f39c12", command=lambda: self.load_category_sample("mid_ripe"))
        btn_sample_mid.pack(side="left", padx=4)

        btn_sample_ripe = ctk.CTkButton(sample_bar, text="🥑 สุก (Ripe)", width=100, fg_color="#e74c3c", command=lambda: self.load_category_sample("ripe"))
        btn_sample_ripe.pack(side="left", padx=4)

        # --- Right Panel: Gauge & Metrics ---
        right_panel = ctk.CTkFrame(main_content, width=410, fg_color="#181818", corner_radius=10)
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

        # Metric 1: Variety Label
        self.lbl_variety = ctk.CTkLabel(
            cards_frame,
            text="🏷️ สายพันธุ์ (Variety): ---",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#3498db"
        )
        self.lbl_variety.pack(anchor="w", padx=15, pady=(10, 4))

        # Metric 2: Ripeness Status
        self.lbl_status = ctk.CTkLabel(
            cards_frame,
            text="🥑 ระดับความสุก: ---",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#ffffff"
        )
        self.lbl_status.pack(anchor="w", padx=15, pady=4)

        # Metric 3: Confidence & Latency
        self.lbl_conf = ctk.CTkLabel(
            cards_frame,
            text="ความเชื่อมั่น (Confidence): 0.0%",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa"
        )
        self.lbl_conf.pack(anchor="w", padx=15, pady=2)

        self.lbl_latency = ctk.CTkLabel(
            cards_frame,
            text="เวลาประมวลผล (Latency): 0.0 ms",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa"
        )
        self.lbl_latency.pack(anchor="w", padx=15, pady=(2, 10))

        # Action Buttons
        btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=5)

        btn_trainer = ctk.CTkButton(
            btn_frame,
            text="🎓 เทรนและจัดการสายพันธุ์ (Trainer Studio)",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8e44ad",
            hover_color="#6c3483",
            command=self.open_trainer_studio
        )
        btn_trainer.pack(fill="x", pady=4)

        btn_save_report = ctk.CTkButton(
            btn_frame,
            text="📷 บันทึกภาพผลการวิเคราะห์ (Save Result)",
            fg_color="#27ae60",
            hover_color="#219150",
            command=self.on_save_result
        )
        btn_save_report.pack(fill="x", pady=4)

        # System Status Footer
        self.lbl_sys_info = ctk.CTkLabel(
            right_panel,
            text="● พร้อมวิเคราะห์รูปภาพ",
            font=ctk.CTkFont(size=11),
            text_color="#2ecc71"
        )
        self.lbl_sys_info.pack(side="bottom", pady=10)

    def load_default_sample(self):
        """Loads default sample image on startup if available"""
        sample_path = os.path.join(self.dataset_dir, "mid_ripe", "mid_ripe_01.jpg")
        if os.path.exists(sample_path):
            self.analyze_image_file(sample_path)

    def load_category_sample(self, category):
        folder = os.path.join(self.dataset_dir, category)
        if os.path.exists(folder):
            files = [f for f in os.listdir(folder) if f.endswith('.jpg') or f.endswith('.png')]
            if files:
                fpath = os.path.join(folder, files[0])
                self.analyze_image_file(fpath)

    def on_browse_image(self):
        fpath = filedialog.askopenfilename(
            title="เลือกไฟล์รูปภาพอะโวคาโด",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if fpath:
            self.analyze_image_file(fpath)

    def analyze_image_file(self, fpath):
        if not os.path.exists(fpath):
            return

        start_t = time.time()
        img = cv2.imread(fpath)
        if img is None:
            messagebox.showerror("ผิดพลาด", "ไม่สามารถอ่านไฟล์รูปภาพนี้ได้")
            return

        self.current_img_path = fpath
        self.current_raw_img = img.copy()

        # Classify Avocado Ripeness AND Variety
        ann_img, category, score, confidence, variety_name, variety_conf = self.classifier.predict_frame(img)
        self.current_ann_img = ann_img

        latency_ms = (time.time() - start_t) * 1000.0

        # Update Gauge Widget Needle
        self.gauge.set_score(score)

        # Update Status Cards
        status_th = {"Unripe": "ดิบ (Unripe)", "Mid-ripe": "กึ่งสุก (Mid-ripe)", "Ripe": "สุก (Ripe)"}.get(category, category)
        status_colors = {"Unripe": "#2ecc71", "Mid-ripe": "#f39c12", "Ripe": "#e74c3c"}

        self.lbl_variety.configure(text=f"🏷️ สายพันธุ์: {variety_name} ({variety_conf:.0f}%)", text_color="#3498db")
        self.lbl_status.configure(text=f"🥑 ระดับความสุก: {status_th}", text_color=status_colors.get(category, "#ffffff"))
        self.lbl_conf.configure(text=f"ความเชื่อมั่น (Confidence): {confidence:.1f}%")
        self.lbl_latency.configure(text=f"เวลาประมวลผล (Latency): {latency_ms:.1f} ms")
        self.lbl_sys_info.configure(text=f"● วิเคราะห์ภาพ: {os.path.basename(fpath)}", text_color="#2ecc71")

        # Render Annotated OpenCV BGR image onto Tkinter Label Box
        img_rgb = cv2.cvtColor(ann_img, cv2.COLOR_BGR2RGB)
        h, w = img_rgb.shape[:2]

        # Calculate fit aspect ratio
        max_w, max_h = 680, 520
        scale = min(max_w / float(w), max_h / float(h))
        new_w, new_h = int(w * scale), int(h * scale)

        pil_img = Image.fromarray(img_rgb).resize((new_w, new_h), Image.Resampling.BILINEAR)
        tk_img = ImageTk.PhotoImage(image=pil_img)
        self.img_label.configure(image=tk_img, text="")
        self.img_label.image = tk_img

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
        if self.current_img_path:
            self.analyze_image_file(self.current_img_path)

    def on_save_result(self):
        if self.current_ann_img is not None:
            os.makedirs(r"d:\Project\snapshots", exist_ok=True)
            fname = f"analysis_result_{int(time.time())}.jpg"
            fpath = os.path.join(r"d:\Project\snapshots", fname)
            cv2.imwrite(fpath, self.current_ann_img)
            messagebox.showinfo("บันทึกสำเร็จ", f"บันทึกรูปภาพผลการวิเคราะห์เรียบร้อยแล้วที่:\n{fpath}")

if __name__ == "__main__":
    app = AvocadoImageInspectorApp()
    app.mainloop()
