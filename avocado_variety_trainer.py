import os
import cv2
import numpy as np
import pickle

class AvocadoVarietyTrainer:
    def __init__(self, dataset_dir=r"d:\Project\dataset\varieties", model_path=r"d:\Project\variety_model.pkl"):
        self.dataset_dir = dataset_dir
        self.model_path = model_path
        self.classes = []
        self.trained = False
        
        # Load or initialize model
        self.load_or_train()

    def extract_variety_features(self, img_bgr):
        """
        Extracts robust feature vector for avocado variety classification:
        - Color Features (Mean & Std of RGB, HSV, LAB)
        - Texture & Edge Features (Std, Laplacian variance, Sobel gradients)
        - Shape Geometry (Aspect ratio, Extent, Roundness)
        """
        if img_bgr is None or img_bgr.size == 0:
            return None
            
        h, w = img_bgr.shape[:2]
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        img_lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # 1. Color Features (12 values)
        mean_rgb = img_rgb.mean(axis=(0,1))
        mean_hsv = img_hsv.mean(axis=(0,1))
        mean_lab = img_lab.mean(axis=(0,1))
        std_rgb = img_rgb.std(axis=(0,1))

        # 2. Texture & Edge Features (4 values)
        texture_std = gray.std()
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3).var()
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3).var()

        # 3. Shape Geometry Features (3 values)
        aspect_ratio = float(w) / float(h) if h > 0 else 1.0
        
        # Find object contour for shape extent
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        extent = 0.5
        roundness = 0.5
        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            perimeter = cv2.arcLength(c, True)
            rect_area = w * h
            if rect_area > 0:
                extent = float(area) / rect_area
            if perimeter > 0:
                roundness = (4 * np.pi * area) / (perimeter ** 2)

        feature_vector = np.concatenate([
            mean_rgb, mean_hsv, mean_lab, std_rgb,
            [texture_std, laplacian_var, sobelx, sobely],
            [aspect_ratio, extent, roundness]
        ]).astype(np.float32)

        return feature_vector

    def train(self):
        """Train KNN & Multi-class distance model on variety dataset"""
        if not os.path.exists(self.dataset_dir):
            os.makedirs(self.dataset_dir, exist_ok=True)
            self.generate_default_variety_samples()

        folders = [f for f in os.listdir(self.dataset_dir) if os.path.isdir(os.path.join(self.dataset_dir, f))]
        
        if len(folders) == 0:
            self.generate_default_variety_samples()
            folders = [f for f in os.listdir(self.dataset_dir) if os.path.isdir(os.path.join(self.dataset_dir, f))]

        self.classes = sorted(folders)
        X, y = [], []

        for class_idx, class_name in enumerate(self.classes):
            folder_path = os.path.join(self.dataset_dir, class_name)
            if not os.path.exists(folder_path):
                continue
                
            for fname in os.listdir(folder_path):
                if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    img_path = os.path.join(folder_path, fname)
                    img = cv2.imread(img_path)
                    if img is not None:
                        feats = self.extract_variety_features(img)
                        if feats is not None:
                            X.append(feats)
                            y.append(class_idx)

        if len(X) > 0:
            self.X_train = np.array(X, dtype=np.float32)
            self.y_train = np.array(y, dtype=np.int64)
            self.mean = self.X_train.mean(axis=0)
            self.std = self.X_train.std(axis=0) + 1e-6
            self.X_train_norm = (self.X_train - self.mean) / self.std
            self.trained = True

            # Save model payload
            payload = {
                'classes': self.classes,
                'X_train_norm': self.X_train_norm,
                'y_train': self.y_train,
                'mean': self.mean,
                'std': self.std
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(payload, f)
            print(f"Variety Model trained successfully on {len(X)} samples across {len(self.classes)} classes.")
            return True, len(X), len(self.classes)
        else:
            self.trained = False
            return False, 0, 0

    def load_or_train(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    payload = pickle.load(f)
                self.classes = payload['classes']
                self.X_train_norm = payload['X_train_norm']
                self.y_train = payload['y_train']
                self.mean = payload['mean']
                self.std = payload['std']
                self.trained = True
                return
            except Exception as e:
                print(f"Failed to load model: {e}, retraining...")

        self.train()

    def predict(self, crop_bgr):
        """Predicts variety class and confidence score"""
        if not self.trained or len(self.classes) == 0:
            return "Unknown (ยังไม่เทรน)", 0.0

        feats = self.extract_variety_features(crop_bgr)
        if feats is None:
            return "Unknown", 0.0

        feats_norm = (feats - self.mean) / self.std
        dists = np.sqrt(np.sum((self.X_train_norm - feats_norm) ** 2, axis=1))

        # K-Nearest Neighbors (k=min(5, len))
        k = min(5, len(self.y_train))
        k_indices = np.argsort(dists)[:k]
        k_labels = self.y_train[k_indices]
        
        counts = np.bincount(k_labels, minlength=len(self.classes))
        best_class_idx = counts.argmax()
        confidence = (counts[best_class_idx] / float(k)) * 100.0

        return self.classes[best_class_idx], confidence

    def generate_default_variety_samples(self):
        """Generates starter synthetic variety dataset (Hass, Booth 7, Pinkerton, Reed)"""
        varieties = {
            "Hass": {"bgr": [30, 40, 45], "axes": (75, 105), "rough": True},
            "Booth 7": {"bgr": [40, 150, 60], "axes": (100, 105), "rough": False},
            "Pinkerton": {"bgr": [35, 130, 50], "axes": (60, 135), "rough": False},
            "Reed": {"bgr": [30, 110, 45], "axes": (95, 95), "rough": False}
        }
        np.random.seed(42)
        for var_name, cfg in varieties.items():
            var_folder = os.path.join(self.dataset_dir, var_name)
            os.makedirs(var_folder, exist_ok=True)
            
            for i in range(12):
                img = np.ones((400, 400, 3), dtype=np.uint8) * 220
                center = (200 + np.random.randint(-10, 11), 200 + np.random.randint(-10, 11))
                ax = (cfg["axes"][0] + np.random.randint(-5, 6), cfg["axes"][1] + np.random.randint(-5, 6))
                
                mask = np.zeros((400, 400), dtype=np.uint8)
                cv2.ellipse(mask, center, ax, np.random.randint(-10, 11), 0, 360, 255, -1)
                
                for c in range(3):
                    noise_lvl = 20 if cfg["rough"] else 8
                    noise = np.random.normal(0, noise_lvl, (400, 400)).astype(np.int16)
                    channel = cfg["bgr"][c] + noise
                    channel = np.clip(channel, 0, 255).astype(np.uint8)
                    img[:, :, c] = np.where(mask == 255, channel, img[:, :, c])
                    
                filepath = os.path.join(var_folder, f"sample_{i+1:02d}.jpg")
                cv2.imwrite(filepath, img)

if __name__ == "__main__":
    trainer = AvocadoVarietyTrainer()
    trainer.train()
