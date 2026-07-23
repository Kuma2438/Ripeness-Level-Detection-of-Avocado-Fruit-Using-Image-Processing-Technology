import cv2
import numpy as np
import os
from avocado_variety_trainer import AvocadoVarietyTrainer

class AvocadoClassifier:
    def __init__(self, dataset_dir=r"d:\Project\program\dataset", variety_dir=r"d:\Project\dataset\varieties"):
        self.categories = ["Unripe", "Mid-ripe", "Ripe"]
        self.dataset_dir = dataset_dir
        self.trained = False
        
        # Variety Classifier Engine
        self.variety_trainer = AvocadoVarietyTrainer(dataset_dir=variety_dir)
        
        # Train baseline ripeness classifier if dataset exists
        self.train_model()

    def train_model(self):
        """Train classifier using sample dataset if available"""
        if not os.path.exists(self.dataset_dir):
            return
        
        X, y = [], []
        cat_map = {"unripe": 0, "mid_ripe": 1, "ripe": 2}
        
        for cat_name, cat_idx in cat_map.items():
            folder = os.path.join(self.dataset_dir, cat_name)
            if not os.path.exists(folder):
                continue
            for fname in os.listdir(folder):
                if fname.endswith(".jpg") or fname.endswith(".png"):
                    fpath = os.path.join(folder, fname)
                    img = cv2.imread(fpath)
                    if img is not None:
                        feats = self.extract_features(img)
                        if feats is not None:
                            X.append(feats)
                            y.append(cat_idx)
        
        if len(X) > 0:
            self.X_train = np.array(X, dtype=np.float32)
            self.y_train = np.array(y, dtype=np.int64)
            self.mean = self.X_train.mean(axis=0)
            self.std = self.X_train.std(axis=0) + 1e-6
            self.X_train_norm = (self.X_train - self.mean) / self.std
            self.trained = True

        # Also reload/train variety model
        self.variety_trainer.load_or_train()

    def extract_features(self, img_bgr):
        """Extract color and texture features from image/ROI"""
        if img_bgr is None or img_bgr.size == 0:
            return None
        
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        mean_r = img_rgb[:,:,0].mean()
        mean_g = img_rgb[:,:,1].mean()
        mean_b = img_rgb[:,:,2].mean()
        mean_h = img_hsv[:,:,0].mean()
        mean_s = img_hsv[:,:,1].mean()
        mean_v = img_hsv[:,:,2].mean()
        texture_sd = gray.std()
        
        return [mean_r, mean_g, mean_b, mean_h, mean_s, mean_v, texture_sd]

    def predict_frame(self, frame_bgr):
        """
        Processes real-time frame, detects avocado, classifies ripeness AND variety/label,
        and draws overlay bounding box & status badges.
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

        feats = self.extract_features(target_roi)
        
        if feats is None:
            return annotated, "Unripe", 0.0, 0.0, "Unknown", 0.0

        # Predict Variety / Cultivar Label
        variety_name, variety_conf = self.variety_trainer.predict(target_roi)

        # Classification logic via KNN / Color Space Rule
        mean_g = feats[1]
        texture_sd = feats[6]

        if self.trained:
            feats_norm = (np.array(feats, dtype=np.float32) - self.mean) / self.std
            dists = np.sqrt(np.sum((self.X_train_norm - feats_norm)**2, axis=1))
            k_idx = np.argsort(dists)[:5]
            k_labels = self.y_train[k_idx]
            counts = np.bincount(k_labels, minlength=3)
            pred_class = counts.argmax()
            confidence = (counts[pred_class] / 5.0) * 100.0
        else:
            # Color space heuristic fallback
            if mean_g > 160:
                pred_class = 0 # Unripe
                confidence = 92.0
            elif mean_g > 110:
                pred_class = 1 # Mid-ripe
                confidence = 88.0
            else:
                pred_class = 2 # Ripe
                confidence = 95.0

        category = self.categories[pred_class]
        
        # Calculate Gauge Score (0.0 to 100.0)
        if pred_class == 0: # Unripe
            score = 15.0 + (1.0 - min(1.0, max(0.0, (215 - mean_g)/50.0))) * 18.0
        elif pred_class == 1: # Mid-ripe
            score = 35.0 + (1.0 - min(1.0, max(0.0, (160 - mean_g)/50.0))) * 30.0
        else: # Ripe
            score = 68.0 + min(30.0, max(0.0, (texture_sd - 50.0)*0.5))
            
        score = float(np.clip(score, 5.0, 98.0))

        # Overlay Status Badges
        badge_colors = [(40, 200, 40), (40, 180, 220), (50, 50, 200)] # BGR
        color = badge_colors[pred_class]
        
        bx, by, bw, bh = target_box
        
        # Variety Badge (Top)
        variety_str = f"Variety: {variety_name}"
        cv2.rectangle(annotated, (bx, max(0, by - 55)), (bx + max(200, len(variety_str)*11), max(25, by - 30)), (140, 50, 20), -1)
        cv2.putText(annotated, variety_str, (bx + 8, max(18, by - 36)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        # Ripeness Badge (Bottom)
        label_str = f"{category} ({confidence:.0f}%)"
        cv2.rectangle(annotated, (bx, max(0, by - 28)), (bx + 180, max(28, by)), color, -1)
        cv2.putText(annotated, label_str, (bx + 8, max(20, by - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        
        return annotated, category, score, confidence, variety_name, variety_conf
