import cv2
import numpy as np
import os
import sys
import glob
import time

class DualCameraManager:
    def __init__(self, dataset_dir=None):
        if dataset_dir is None:
            dataset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
            
        self.cam1_id = 0
        self.cam2_id = 1
        
        self.cap1 = None
        self.cap2 = None
        self.picam2_obj = None
        
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
            fallback_img = np.ones((480, 640, 3), dtype=np.uint8) * 200
            cv2.ellipse(fallback_img, (320, 240), (90, 130), 0, 0, 360, (40, 160, 50), -1)
            cv2.putText(fallback_img, "Simulated Camera Feed", (160, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            self.sim_images.append(fallback_img)

    def init_raspberry_pi_camera(self):
        """Try initializing Raspberry Pi 5 Picamera2 for OV5647 5MP Camera"""
        try:
            from picamera2 import Picamera2
            picam2 = Picamera2()
            config = picam2.create_preview_configuration(main={"size": (1280, 720)})
            picam2.configure(config)
            picam2.start()
            self.picam2_obj = picam2
            print("Successfully initialized Raspberry Pi 5 Picamera2 (OV5647 Camera)")
            return True
        except Exception as e:
            print(f"Picamera2 init note/fallback: {e}")
            return False

    def open_camera_backend(self, cam_id):
        """Cross-platform Camera Opener (DirectShow for Windows, V4L2/OpenCV for Linux)"""
        cap = None
        if sys.platform.startswith('win'):
            cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
        elif sys.platform.startswith('linux'):
            # GStreamer or V4L2 pipeline for Linux/RPi
            gst_pipeline = f"v4l2src device=/dev/video{cam_id} ! video/x-raw, width=1280, height=720, framerate=30/1 ! videoconvert ! appsink"
            cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
            if cap is None or not cap.isOpened():
                cap = cv2.VideoCapture(cam_id, cv2.CAP_V4L2)
            if cap is None or not cap.isOpened():
                cap = cv2.VideoCapture(cam_id)
            if cap and cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        else:
            cap = cv2.VideoCapture(cam_id)
        return cap

    def init_cameras(self):
        """Initialize Cameras, fallback to Picamera2 or Simulation if unavailable"""
        if sys.platform.startswith('linux'):
            # Try Picamera2 first on Raspberry Pi 5
            rpi_ok = self.init_raspberry_pi_camera()
            if rpi_ok:
                self.use_sim_cam1 = False
                self.use_sim_cam2 = True
                return

        # Fallback to OpenCV VideoCapture
        self.cap1 = self.open_camera_backend(self.cam1_id)
        if self.cap1 is None or not self.cap1.isOpened() or not self.cap1.read()[0]:
            self.use_sim_cam1 = True
            if self.cap1:
                self.cap1.release()

        self.cap2 = self.open_camera_backend(self.cam2_id)
        if self.cap2 is None or not self.cap2.isOpened() or not self.cap2.read()[0]:
            self.use_sim_cam2 = True
            if self.cap2:
                self.cap2.release()

    def get_simulated_frame(self, offset=0):
        """Returns animated synthetic/dataset camera frame"""
        now = time.time()
        if now - self.last_sim_change > 4.0:
            self.sim_index = (self.sim_index + 1) % len(self.sim_images)
            self.last_sim_change = now
            
        idx = (self.sim_index + offset) % len(self.sim_images)
        frame = self.sim_images[idx].copy()
        
        cam_num = 1 if offset == 0 else 2
        mode_str = "SIMULATED CAMERA" if (cam_num == 1 and self.use_sim_cam1) or (cam_num == 2 and self.use_sim_cam2) else f"PHYSICAL WEBCAM #{cam_num}"
        cv2.putText(frame, f"CAM {cam_num}: {mode_str}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
        return frame

    def read_frames(self):
        """Reads frame from Picamera2, Camera 1, and Camera 2"""
        # Read from Raspberry Pi 5 Picamera2 if active
        if self.picam2_obj is not None:
            try:
                img_array = self.picam2_obj.capture_array()
                frame1 = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                frame2 = self.get_simulated_frame(1)
                return frame1, frame2
            except Exception as e:
                print(f"Picamera2 capture error: {e}")

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
        if self.picam2_obj is not None:
            try:
                self.picam2_obj.stop()
            except Exception:
                pass
        if self.cap1 and self.cap1.isOpened():
            self.cap1.release()
        if self.cap2 and self.cap2.isOpened():
            self.cap2.release()
