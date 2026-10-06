"""Resilient Dual Camera Manager supporting Raspberry Pi 5 CSI (OV5647/IMX), USB Webcams, and Simulation."""

from pathlib import Path
import sys
import threading
import time
from typing import Any, List, Optional, Tuple
import cv2
import numpy as np

from avocado.config import AppConfig, load_config


class DualCameraManager:
    """Manages dual camera pairs: Raspberry Pi 5 MIPI CSI (Dual OV5647 / IMX series), USB Webcams, or Simulated feeds."""

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        cam1_id: Optional[int] = None,
        cam2_id: Optional[int] = None,
    ) -> None:
        self.config = config or load_config()
        self.driver_mode = self.config.camera.driver.lower()

        self.cam1_id = cam1_id if cam1_id is not None else self.config.camera.cam1_id
        self.cam2_id = cam2_id if cam2_id is not None else self.config.camera.cam2_id

        self.width = self.config.camera.width
        self.height = self.config.camera.height
        self.fps = self.config.camera.fps

        # Hardware handles
        self.picam1_obj: Any = None
        self.picam2_obj: Any = None
        self.cap1: Optional[cv2.VideoCapture] = None
        self.cap2: Optional[cv2.VideoCapture] = None

        # Camera status flags
        self.cam1_type: str = "none"  # "picamera2", "usb", or "sim"
        self.cam2_type: str = "none"

        self.sim_images: List[np.ndarray] = []
        self.sim_index = 0
        self.last_sim_change = time.time()

        # Threaded background frame buffer
        self._running = True
        self._lock = threading.Lock()
        self._latest_frame1: Optional[np.ndarray] = None
        self._latest_frame2: Optional[np.ndarray] = None

        self.load_simulation_dataset()
        self.init_cameras()

        self._thread = threading.Thread(target=self._capture_worker, daemon=True, name="DualCameraWorker")
        self._thread.start()

    def load_simulation_dataset(self) -> None:
        """Loads sample images for simulation fallback."""
        dataset_dir = self.config.dataset.root_dir
        if dataset_dir.is_dir():
            for cat in self.config.dataset.categories:
                folder = dataset_dir / cat
                if folder.is_dir():
                    for f in folder.glob("*.jpg"):
                        img = cv2.imread(str(f))
                        if img is not None:
                            self.sim_images.append(img)

        if not self.sim_images:
            fallback = np.ones((self.height, self.width, 3), dtype=np.uint8) * 210
            cv2.ellipse(
                fallback,
                (self.width // 2, self.height // 2),
                (self.width // 7, self.height // 4),
                0,
                0,
                360,
                (40, 160, 50),
                -1,
            )
            cv2.putText(
                fallback,
                "Simulated Camera Feed",
                (self.width // 6, self.height - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 0),
                2,
            )
            self.sim_images.append(fallback)

    def _try_init_picamera2(self, camera_num: int) -> Optional[Any]:
        """Initializes a Raspberry Pi 5 MIPI CSI Camera instance (OV5647 / IMX sensor)."""
        if not sys.platform.startswith("linux"):
            return None

        try:
            from picamera2 import Picamera2
            picam = Picamera2(camera_num)
            config = picam.create_preview_configuration(main={"size": (self.width, self.height), "format": "RGB888"})
            picam.configure(config)
            picam.start()
            # Test grab
            _ = picam.capture_array()
            return picam
        except Exception:
            return None

    def _open_usb_device(self, cam_id: int) -> Optional[cv2.VideoCapture]:
        """Opens USB Video Capture device via DirectShow (Windows) or V4L2/OpenCV (Linux)."""
        cap = None
        if sys.platform.startswith("win"):
            cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
        elif sys.platform.startswith("linux"):
            cap = cv2.VideoCapture(cam_id, cv2.CAP_V4L2)
            if cap is None or not cap.isOpened():
                cap = cv2.VideoCapture(cam_id)
        else:
            cap = cv2.VideoCapture(cam_id)

        if cap and cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            cap.set(cv2.CAP_PROP_FPS, self.fps)
            ret, frame = cap.read()
            if ret and frame is not None and frame.size > 0:
                return cap
            cap.release()
        return None

    def init_cameras(self) -> None:
        """Initializes primary and secondary cameras with priority: Picamera2 CSI (OV5647) -> USB Video -> Simulation."""
        # Check if driver is forced to simulation
        if self.driver_mode == "sim":
            self.cam1_type = "sim"
            self.cam2_type = "sim"
            return

        # 1. Try Raspberry Pi 5 Picamera2 CSI (OV5647 / IMX) if on Linux and driver is auto/picamera2
        if self.driver_mode in ["auto", "picamera2"] and sys.platform.startswith("linux"):
            if self.cam1_id is not None:
                self.picam1_obj = self._try_init_picamera2(self.cam1_id)
                if self.picam1_obj:
                    self.cam1_type = "picamera2"

            if self.cam2_id is not None:
                self.picam2_obj = self._try_init_picamera2(self.cam2_id)
                if self.picam2_obj:
                    self.cam2_type = "picamera2"

        # 2. If Camera 1 not active on CSI, probe USB Video / DirectShow
        if self.cam1_type == "none" and self.driver_mode != "picamera2":
            if self.cam1_id is not None:
                self.cap1 = self._open_usb_device(self.cam1_id)
                if self.cap1:
                    self.cam1_type = "usb"

        # 3. If Camera 2 not active on CSI, probe USB Video / DirectShow
        if self.cam2_type == "none" and self.driver_mode != "picamera2":
            if self.cam2_id is not None:
                self.cap2 = self._open_usb_device(self.cam2_id)
                if self.cap2:
                    self.cam2_type = "usb"

        # 4. Fallback missing cameras to simulation
        if self.cam1_type == "none":
            self.cam1_type = "sim"
        if self.cam2_type == "none":
            self.cam2_type = "sim"

    def get_simulated_frame(self, offset: int = 0) -> np.ndarray:
        """Generates synthetic animated frame for test/fallback."""
        now = time.time()
        if now - self.last_sim_change > 4.0:
            self.sim_index = (self.sim_index + 1) % len(self.sim_images)
            self.last_sim_change = now

        idx = (self.sim_index + offset) % len(self.sim_images)
        frame = self.sim_images[idx].copy()
        if frame.shape[:2] != (self.height, self.width):
            frame = cv2.resize(frame, (self.width, self.height))

        cam_num = 1 if offset == 0 else 2
        mode_str = "SIMULATED FEED"
        cv2.putText(
            frame,
            f"CAM {cam_num}: {mode_str}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2,
        )
        return frame

    def _grab_single_frame(self, cam_num: int) -> Optional[np.ndarray]:
        """Captures a raw frame from specified camera hardware (1 or 2)."""
        cam_type = self.cam1_type if cam_num == 1 else self.cam2_type
        picam_obj = self.picam1_obj if cam_num == 1 else self.picam2_obj
        cap_obj = self.cap1 if cam_num == 1 else self.cap2

        if cam_type == "picamera2" and picam_obj is not None:
            try:
                rgb_arr = picam_obj.capture_array()
                return cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2BGR)
            except Exception:
                return None

        if cam_type == "usb" and cap_obj and cap_obj.isOpened():
            try:
                ret, img = cap_obj.read()
                if ret and img is not None and img.size > 0:
                    return img
            except Exception:
                return None

        return None

    def _capture_worker(self) -> None:
        """Continuous background thread grabbing frames to ensure non-blocking UI preview."""
        target_interval = 1.0 / max(1, self.fps)
        while self._running:
            start_t = time.time()

            f1 = self._grab_single_frame(1)
            if f1 is None:
                f1 = self.get_simulated_frame(0)

            f2 = self._grab_single_frame(2)
            if f2 is None:
                f2 = self.get_simulated_frame(1)

            with self._lock:
                self._latest_frame1 = f1
                self._latest_frame2 = f2

            elapsed = time.time() - start_t
            sleep_time = target_interval - elapsed
            if sleep_time > 0.001:
                time.sleep(sleep_time)

    def read_frames(self) -> Tuple[np.ndarray, np.ndarray]:
        """Returns the latest synchronized frame pair from memory buffer with zero I/O wait."""
        with self._lock:
            f1 = self._latest_frame1
            f2 = self._latest_frame2

        if f1 is None:
            f1 = self.get_simulated_frame(0)
        if f2 is None:
            f2 = self.get_simulated_frame(1)

        return f1, f2

    def release(self) -> None:
        """Safely stops background thread and releases hardware handles."""
        self._running = False
        if hasattr(self, "_thread") and self._thread.is_alive():
            self._thread.join(timeout=0.5)

        if self.picam1_obj is not None:
            try:
                self.picam1_obj.stop()
            except Exception:
                pass
            self.picam1_obj = None

        if self.picam2_obj is not None:
            try:
                self.picam2_obj.stop()
            except Exception:
                pass
            self.picam2_obj = None

        if self.cap1 and self.cap1.isOpened():
            self.cap1.release()
            self.cap1 = None

        if self.cap2 and self.cap2.isOpened():
            self.cap2.release()
            self.cap2 = None
