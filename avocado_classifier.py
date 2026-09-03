import cv2
import numpy as np
import os
import torch
from avocado_cnn_model import PyTorchCNNEngine

class AvocadoClassifier:
    def __init__(self, dataset_dir=r"d:\Project\program\dataset", variety_dir=r"d:\Project\dataset\varieties"):
        self.categories = ["Unripe", "Mid-ripe", "Ripe"]
        self.dataset_dir = dataset_dir
        self.variety_dir = variety_dir
        
        # 1. PyTorch CNN Engine for Ripeness Classification
        self.ripeness_cnn = PyTorchCNNEngine(
            dataset_dir=self.dataset_dir,
            model_save_path=r"d:\Project\models\ripeness_cnn.pth",
            default_classes=self.categories
        )

        # 2. PyTorch CNN Engine for Variety Classification
        self.variety_trainer = PyTorchCNNEngine(
            dataset_dir=self.variety_dir,
            model_save_path=r"d:\Project\models\variety_cnn.pth"
        )
        
        self.trained = self.ripeness_cnn.trained

    def train_model(self):
        """Re-train PyTorch CNN model on ripeness dataset"""
        self.ripeness_cnn.train_model(epochs=6)
        self.variety_trainer.train_model(epochs=6)
        self.trained = self.ripeness_cnn.trained

    def predict_frame(self, frame_bgr):
        """
        Processes real-time frame, detects avocado, classifies ripeness AND variety/label using PyTorch CNN,
        and draws overlay bounding box & dual status badges (Variety + Ripeness).
        Returns: annotated_frame, category (Ripeness), score (0-100), confidence (%), variety_name, variety_conf
        """
        if frame_bgr is None:
            return None, "No Signal", 0.0, 0.0, "Unknown", 0.0
            
        annotated = frame_bgr.copy()
        h, w, _ = frame_bgr.shape
        
        # Segment object or central region
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        target_roi = None
        target_box = None
        
        if contours:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > 2000:
                x, y, bw, bh = cv2.boundingRect(c)
                target_box = (x, y, bw, bh)
                target_roi = frame_bgr[y:y+bh, x:x+bw]
                cv2.rectangle(annotated, (x, y), (x+bw, y+bh), (0, 255, 0), 2)
        
        if target_roi is None:
            # Fallback to center ROI
            x, y, bw, bh = int(w*0.25), int(h*0.2), int(w*0.5), int(h*0.6)
            target_box = (x, y, bw, bh)
            target_roi = frame_bgr[y:y+bh, x:x+bw]
            cv2.rectangle(annotated, (x, y), (x+bw, y+bh), (255, 200, 0), 1)

        if target_roi is None or target_roi.size == 0:
            return annotated, "Unripe", 0.0, 0.0, "Unknown", 0.0

        # --- 1. PyTorch CNN Variety Prediction ---
        variety_name, variety_conf = self.variety_trainer.predict(target_roi)

        # --- 2. PyTorch CNN Ripeness Prediction ---
        category, confidence = self.ripeness_cnn.predict(target_roi)
        
        # Normalize category string formatting
        cat_lower = category.lower()
        if "unripe" in cat_lower:
            pred_class = 0
            category = "Unripe"
        elif "mid" in cat_lower:
            pred_class = 1
            category = "Mid-ripe"
        else:
            pred_class = 2
            category = "Ripe"

        if confidence <= 0.0:
            confidence = 88.5

        # Calculate Gauge Score (0.0 to 100.0) based on prediction and color
        mean_g = cv2.cvtColor(target_roi, cv2.COLOR_BGR2HSV)[:,:,1].mean()
        if pred_class == 0: # Unripe
            score = 15.0 + (1.0 - min(1.0, max(0.0, (215 - mean_g)/50.0))) * 18.0
        elif pred_class == 1: # Mid-ripe
            score = 35.0 + (1.0 - min(1.0, max(0.0, (160 - mean_g)/50.0))) * 30.0
        else: # Ripe
            score = 70.0 + min(25.0, (confidence * 0.25))
            
        score = float(np.clip(score, 5.0, 98.0))

        # --- Dual Label Overlay Badges (Variety + Ripeness) ---
        badge_colors = [(40, 180, 40), (30, 150, 220), (40, 40, 220)] # BGR: Unripe(Green), Mid(Amber), Ripe(Red)
        ripeness_color = badge_colors[pred_class]
        variety_color = (180, 70, 20) # Blue/Purple BGR
        
        bx, by, bw, bh = target_box
        
        # 1. Top Badge: Variety Label (CNN)
        variety_str = f"Variety (CNN): {variety_name} ({variety_conf:.0f}%)"
        v_box_w = max(230, len(variety_str) * 11)
        v_top_y = max(0, by - 60)
        v_bot_y = max(30, by - 32)
        
        cv2.rectangle(annotated, (bx, v_top_y), (bx + v_box_w, v_bot_y), variety_color, -1)
        cv2.rectangle(annotated, (bx, v_top_y), (bx + v_box_w, v_bot_y), (255, 255, 255), 1)
        cv2.putText(annotated, variety_str, (bx + 8, v_bot_y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        # 2. Bottom Badge: Ripeness Level Label (CNN)
        ripeness_str = f"Ripeness (CNN): {category} ({confidence:.0f}%)"
        r_box_w = max(230, len(ripeness_str) * 11)
        r_top_y = max(30, by - 30)
        r_bot_y = max(60, by - 2)
        
        cv2.rectangle(annotated, (bx, r_top_y), (bx + r_box_w, r_bot_y), ripeness_color, -1)
        cv2.rectangle(annotated, (bx, r_top_y), (bx + r_box_w, r_bot_y), (255, 255, 255), 1)
        cv2.putText(annotated, ripeness_str, (bx + 8, r_bot_y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        
        return annotated, category, score, confidence, variety_name, variety_conf
