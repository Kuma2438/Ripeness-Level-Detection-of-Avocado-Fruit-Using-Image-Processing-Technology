"""Dual and Single USB Camera Manager for Raspberry Pi 5 and Desktop platforms."""

import glob
from pathlib import Path
import sys
import time
from typing import List, Optional, Tuple
import cv2
import numpy as np

from avocado.config import AppConfig, CameraConfig, load_config


class DualCameraManager:
    """Manages dual USB webcams with auto-detection, V4L2/DSHOW backends, and simulation fallback."""

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        cam1_id: Optional[int] = None,
        cam2_id: Optional[int] = None,
    ) -> None:
        self.config = config or load_config()
        self.cam1_id = cam1_id if cam1_id is not None else self.config.camera.cam1_id
        self.cam2_id = cam2_id if cam2_id is not None else self.config.camera.cam2_id

        self.width = self.config.camera.width
        self.height = self.config.camera.height
        self.fps = self.config.camera.fps

        self.cap1: Optional[cv2.VideoCapture] = None
        self.cap2: Optional[cv2.VideoCapture] = None
        self.picam2_obj = None

        self.use_sim_cam1 = False
        self.use_sim_cam2 = False

        self.sim_images: List[np.ndarray] = []
        self.sim_index = 0
        self.last_sim_change = time.time()

        self.load_simulation_dataset()
        self.init_cameras()

    def load_simulation_dataset(self) -> None:
        """Loads dataset sample images for simulation fallback."""
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

    def _open_device(self, cam_id: int) -> Optional[cv2.VideoCapture]:
        """Cross-platform USB camera opener (DirectShow for Windows, V4L2 for Linux/Pi 5)."""
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
        """Initializes primary and secondary USB cameras."""
        # 1. Initialize Primary Camera
        if self.cam1_id is not None:
            self.cap1 = self._open_device(self.cam1_id)
            self.use_sim_cam1 = self.cap1 is None
        else:
            self.use_sim_cam1 = True

        # 2. Initialize Secondary Camera
        if self.cam2_id is not None:
            self.cap2 = self._open_device(self.cam2_id)
            self.use_sim_cam2 = self.cap2 is None
        else:
            self.use_sim_cam2 = True

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
        is_sim = (cam_num == 1 and self.use_sim_cam1) or (cam_num == 2 and self.use_sim_cam2)
        mode_str = "SIMULATED FEED" if is_sim else f"USB CAM #{cam_num}"

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

    def read_frames(self) -> Tuple[np.ndarray, np.ndarray]:
        """Reads frame pair from Camera 1 and Camera 2."""
        # Frame 1
        if not self.use_sim_cam1 and self.cap1 and self.cap1.isOpened():
            ret1, frame1 = self.cap1.read()
            if not ret1 or frame1 is None:
                frame1 = self.get_simulated_frame(0)
        else:
            frame1 = self.get_simulated_frame(0)

        # Frame 2
        if not self.use_sim_cam2 and self.cap2 and self.cap2.isOpened():
            ret2, frame2 = self.cap2.read()
            if not ret2 or frame2 is None:
                frame2 = self.get_simulated_frame(1)
        else:
            frame2 = self.get_simulated_frame(1)

        return frame1, frame2

    def release(self) -> None:
        """Releases video capture hardware handles."""
        if self.cap1 and self.cap1.isOpened():
            self.cap1.release()
            self.cap1 = None
        if self.cap2 and self.cap2.isOpened():
            self.cap2.release()
            self.cap2 = None
