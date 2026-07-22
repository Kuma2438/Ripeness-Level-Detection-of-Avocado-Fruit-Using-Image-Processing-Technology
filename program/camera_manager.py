import cv2
import numpy as np
import os
import glob
import time

class DualCameraManager:
    def __init__(self, dataset_dir=r"d:\Project\program\dataset"):
        self.cam1_id = 0
        self.cam2_id = 1
        
        self.cap1 = None
        self.cap2 = None
        
        self.use_sim_cam1 = False
        self.use_sim_cam2 = False
        
        self.dataset_dir = dataset_dir
        self.sim_images = []
        self.sim_index = 0
        self.last_sim_change = time.time()
        
        self.load_simulation_dataset()
        self.init_cameras()

    def load_simulation_dataset(self):
        """Loads sample dataset images for simulation fallback"""
        if os.path.exists(self.dataset_dir):
            for cat in ["unripe", "mid_ripe", "ripe"]:
                folder = os.path.join(self.dataset_dir, cat)
                if os.path.exists(folder):
                    files = glob.glob(os.path.join(folder, "*.jpg"))
                    for f in files:
                        img = cv2.imread(f)
                        if img is not None:
                            self.sim_images.append(img)
                            
        if not self.sim_images:
            # Generate on the fly synthetic fallback image
            fallback_img = np.ones((480, 640, 3), dtype=np.uint8) * 200
            cv2.ellipse(fallback_img, (320, 240), (90, 130), 0, 0, 360, (40, 160, 50), -1)
            cv2.putText(fallback_img, "Simulated Camera Feed", (160, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            self.sim_images.append(fallback_img)

    def init_cameras(self):
        """Initialize Camera 1 and Camera 2, fallback to simulation if unavailable"""
        # Try opening Camera 1
        self.cap1 = cv2.VideoCapture(self.cam1_id, cv2.CAP_DSHOW)
        if not self.cap1.isOpened() or not self.cap1.read()[0]:
            self.use_sim_cam1 = True
            if self.cap1:
                self.cap1.release()

        # Try opening Camera 2
        self.cap2 = cv2.VideoCapture(self.cam2_id, cv2.CAP_DSHOW)
        if not self.cap2.isOpened() or not self.cap2.read()[0]:
            self.use_sim_cam2 = True
            if self.cap2:
                self.cap2.release()

    def get_simulated_frame(self, offset=0):
        """Returns animated synthetic/dataset camera frame"""
        now = time.time()
        if now - self.last_sim_change > 4.0: # Rotate image every 4 seconds
            self.sim_index = (self.sim_index + 1) % len(self.sim_images)
            self.last_sim_change = now
            
        idx = (self.sim_index + offset) % len(self.sim_images)
        frame = self.sim_images[idx].copy()
        
        # Add timestamp & camera overlay badge
        cam_num = 1 if offset == 0 else 2
        mode_str = "SIMULATED CAMERA" if (cam_num == 1 and self.use_sim_cam1) or (cam_num == 2 and self.use_sim_cam2) else f"PHYSICAL WEBCAM #{cam_num}"
        cv2.putText(frame, f"CAM {cam_num}: {mode_str}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
        return frame

    def read_frames(self):
        """Reads frame from Camera 1 and Camera 2"""
        # Cam 1
        if not self.use_sim_cam1 and self.cap1 and self.cap1.isOpened():
            ret1, frame1 = self.cap1.read()
            if not ret1:
                frame1 = self.get_simulated_frame(0)
        else:
            frame1 = self.get_simulated_frame(0)

        # Cam 2
        if not self.use_sim_cam2 and self.cap2 and self.cap2.isOpened():
            ret2, frame2 = self.cap2.read()
            if not ret2:
                frame2 = self.get_simulated_frame(1)
        else:
            frame2 = self.get_simulated_frame(1)

        return frame1, frame2

    def release(self):
        if self.cap1 and self.cap1.isOpened():
            self.cap1.release()
        if self.cap2 and self.cap2.isOpened():
            self.cap2.release()
