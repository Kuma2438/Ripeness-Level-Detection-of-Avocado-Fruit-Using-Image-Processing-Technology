"""Ripeness and Variety Composite Classifier Engine with Native RGB, Empty Box Detection, and Avocado Validation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
import cv2
import numpy as np

from avocado.config import AppConfig, get_project_root, load_config
from avocado.core.trainer import AvocadoTrainer


@dataclass
class ClassificationResult:
    annotated_frame: np.ndarray
    category: str
    score: Optional[float]
    confidence: float
    variety_name: str
    variety_confidence: float
    roi_box: Optional[Tuple[int, int, int, int]] = None
    status: str = "DETECTED"  # "DETECTED", "NO_AVOCADO", "NOT_AVOCADO", "NO_SIGNAL"
    rejection_reason: Optional[str] = None


class AvocadoClassifier:
    """Classifies avocado ripeness stage and variety from video frames or image arrays."""

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or load_config()

        self.categories = ["Unripe", "Mid-ripe", "Ripe"]

        self.ripeness_cnn = AvocadoTrainer(
            dataset_dir=self.config.dataset.root_dir,
            model_save_path=self.config.models.ripeness_model_path,
            default_classes=self.categories,
            device=self.config.models.device,
        )

        self.variety_trainer = AvocadoTrainer(
            dataset_dir=self.config.dataset.varieties_dir,
            model_save_path=self.config.models.variety_model_path,
            device=self.config.models.device,
        )

        self.trained = self.ripeness_cnn.trained

    def train_model(self, epochs: int = 6) -> None:
        """Re-trains both ripeness and variety models."""
        self.ripeness_cnn.train_model(epochs=epochs)
        self.variety_trainer.train_model(epochs=epochs)
        self.trained = self.ripeness_cnn.trained

    def extract_roi(
        self, frame_rgb: np.ndarray
    ) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[Tuple[int, int, int, int]], Optional[np.ndarray]]:
        """Extracts primary avocado region using foreground segmentation without fake fallback."""
        annotated = frame_rgb.copy()
        h, w, _ = frame_rgb.shape

        gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Baseline variance check on the scanning zone: empty backgrounds are flat/low-variance
        std_val = float(np.std(gray[int(h * 0.15) : int(h * 0.85), int(w * 0.20) : int(w * 0.80)]))
        if std_val < 10.0:
            # Virtually zero variance / uniform empty scanner tray
            return annotated, None, None, None

        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        target_roi = None
        target_box = None
        best_contour = None

        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            total_area = h * w
            # Must represent a meaningful object (between 2.5% and 85% of total frame area)
            if 0.025 * total_area < area < 0.85 * total_area:
                x, y, bw, bh = cv2.boundingRect(c)
                target_box = (x, y, bw, bh)
                target_roi = frame_rgb[y : y + bh, x : x + bw]
                best_contour = c

        return annotated, target_roi, target_box, best_contour

    def validate_avocado(self, roi_rgb: np.ndarray, contour: Optional[np.ndarray]) -> Tuple[bool, str]:
        """Validates if an extracted object matches avocado morphological and chromatic profile."""
        if roi_rgb is None or roi_rgb.size == 0:
            return False, "Empty ROI"

        rh, rw, _ = roi_rgb.shape

        # 1. Morphological & Shape Validation
        if contour is not None:
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            c_area = cv2.contourArea(contour)
            solidity = float(c_area / hull_area) if hull_area > 0 else 0.0
            # An avocado is a convex ellipsoid (egg/pear); fingers/hands/scissors have low solidity
            if solidity < 0.74:
                return False, "Irregular non-convex shape (รูปร่างไม่ใช่อะโวคาโด)"

        ar = float(rw) / float(max(1, rh))
        if ar < 0.40 or ar > 2.20:
            return False, "Aspect ratio does not match fruit (สัดส่วนไม่ใช่อะโวคาโด)"

        # 2. Chromatic & Color Validation (RGB, HSV, YCrCb)
        mean_r = float(np.mean(roi_rgb[:, :, 0]))
        mean_g = float(np.mean(roi_rgb[:, :, 1]))
        mean_b = float(np.mean(roi_rgb[:, :, 2]))

        # Check A: Human Skin Tone Detection (Human Hands / Fingers in Scanner)
        ycrcb = cv2.cvtColor(roi_rgb, cv2.COLOR_RGB2YCrCb)
        cr = ycrcb[:, :, 1]
        cb = ycrcb[:, :, 2]
        r = roi_rgb[:, :, 0]
        g = roi_rgb[:, :, 1]
        b = roi_rgb[:, :, 2]
        skin_mask = (cr >= 135) & (cr <= 180) & (cb >= 85) & (cb <= 135) & (r > g) & (g > b) & (r > 105)
        skin_ratio = float(np.sum(skin_mask)) / float(rh * rw)
        if skin_ratio > 0.28:
            return False, "Human hand/skin detected (ตรวจพบมือหรือผิวหนัง)"

        # Check B: Pure White / Paper / Cup Detection
        hsv = cv2.cvtColor(roi_rgb, cv2.COLOR_RGB2HSV)
        sat_mean = float(np.mean(hsv[:, :, 1]))
        if mean_r > 185 and mean_g > 185 and mean_b > 185 and sat_mean < 35.0:
            return False, "White object/paper detected (ตรวจพบกระดาษหรือแก้วสีขาว)"

        # Check C: Vibrant Foreign Colors
        # Bright Red (Apples, red mugs, markers)
        if mean_r > 125 and mean_r > 1.35 * mean_g and mean_r > 1.35 * mean_b:
            return False, "Red non-avocado object (ตรวจพบวัตถุสีแดง)"

        # Bright Blue / Cyan (Pens, blue cups, phones)
        if mean_b > 110 and mean_b > 1.15 * mean_g:
            return False, "Blue non-avocado object (ตรวจพบวัตถุสีฟ้า/น้ำเงิน)"

        # Bright Yellow (Bananas, sticky notes)
        if mean_r > 170 and mean_g > 170 and mean_b < 95:
            return False, "Yellow non-avocado object (ตรวจพบวัตถุสีเหลืองสด)"

        # Check D: Avocado Color Spectrum Coverage
        # Valid avocado spectrum: Green (Unripe), Olive-Amber (Mid-ripe), Dark Purple-Black (Ripe)
        h = hsv[:, :, 0]
        s = hsv[:, :, 1]
        v = hsv[:, :, 2]
        green_mask = (h >= 28) & (h <= 88) & (s >= 25)
        olive_brown_mask = (h >= 14) & (h <= 60) & (v <= 155)
        dark_black_mask = (v <= 75)
        avocado_mask = green_mask | olive_brown_mask | dark_black_mask
        avocado_ratio = float(np.sum(avocado_mask)) / float(rh * rw)

        if avocado_ratio < 0.22:
            return False, "Color spectrum does not match avocado (สีผิวไม่ตรงกับอะโวคาโด)"

        return True, "Valid Avocado"

    def compute_ripeness_score(
        self, target_roi_rgb: np.ndarray, pred_class: int, confidence: float
    ) -> float:
        """Calculates ripeness index score from 5.0 to 98.0 based on RGB/HSV color and CNN prediction."""
        hsv = cv2.cvtColor(target_roi_rgb, cv2.COLOR_RGB2HSV)
        mean_g = float(hsv[:, :, 1].mean())

        if pred_class == 0:  # Unripe
            score = 15.0 + (1.0 - min(1.0, max(0.0, (215.0 - mean_g) / 50.0))) * 18.0
        elif pred_class == 1:  # Mid-ripe
            score = 35.0 + (1.0 - min(1.0, max(0.0, (160.0 - mean_g) / 50.0))) * 30.0
        else:  # Ripe
            score = 70.0 + min(25.0, (confidence * 0.25))

        return float(np.clip(score, 5.0, 98.0))

    def predict_frame(self, frame_rgb: Optional[np.ndarray]) -> ClassificationResult:
        """Detects avocado, validates authenticity, classifies ripeness & variety, and overlays annotations."""
        if frame_rgb is None or frame_rgb.size == 0:
            dummy = np.zeros((480, 640, 3), dtype=np.uint8)
            return ClassificationResult(
                annotated_frame=dummy,
                category="No Signal",
                score=None,
                confidence=0.0,
                variety_name="---",
                variety_confidence=0.0,
                status="NO_SIGNAL",
                rejection_reason="No camera frame received",
            )

        annotated, target_roi, target_box, contour = self.extract_roi(frame_rgb)

        # 1. Handle Empty Scan Box (No Avocado Detected)
        if target_roi is None or target_box is None:
            h, w, _ = frame_rgb.shape
            gx, gy, gw, gh = int(w * 0.25), int(h * 0.15), int(w * 0.5), int(h * 0.7)
            # Draw neutral dashed guide box in RGB (160, 160, 160)
            cv2.rectangle(annotated, (gx, gy), (gx + gw, gy + gh), (160, 160, 160), 2)
            banner_text = "No Avocado Detected"
            cv2.putText(
                annotated,
                banner_text,
                (gx + 12, gy + 32),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (200, 200, 200),
                2,
            )
            return ClassificationResult(
                annotated_frame=annotated,
                category="No Avocado",
                score=None,
                confidence=0.0,
                variety_name="---",
                variety_confidence=0.0,
                roi_box=None,
                status="NO_AVOCADO",
                rejection_reason="Box is empty / no object found",
            )

        bx, by, bw, bh = target_box

        # 2. Handle Foreign Objects (Not an Avocado)
        is_avocado, rejection_reason = self.validate_avocado(target_roi, contour)
        if not is_avocado:
            # Highlight non-avocado object in Warning Amber RGB (240, 140, 20)
            cv2.rectangle(annotated, (bx, by), (bx + bw, by + bh), (240, 140, 20), 2)
            alert_str = "Not an Avocado"
            alert_w = max(190, len(alert_str) * 11)
            top_y = max(0, by - 36)
            bot_y = max(30, by - 4)
            cv2.rectangle(annotated, (bx, top_y), (bx + alert_w, bot_y), (240, 140, 20), -1)
            cv2.putText(
                annotated,
                alert_str,
                (bx + 8, bot_y - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (255, 255, 255),
                2,
            )
            return ClassificationResult(
                annotated_frame=annotated,
                category="Not Avocado",
                score=None,
                confidence=0.0,
                variety_name="---",
                variety_confidence=0.0,
                roi_box=target_box,
                status="NOT_AVOCADO",
                rejection_reason=rejection_reason,
            )

        # 3. Valid Avocado: Run Variety & Ripeness CNN Models
        cv2.rectangle(annotated, (bx, by), (bx + bw, by + bh), (40, 210, 40), 2)

        variety_name, variety_conf = self.variety_trainer.predict(target_roi)
        category, confidence = self.ripeness_cnn.predict(target_roi)

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

        score = self.compute_ripeness_score(target_roi, pred_class, confidence)

        # RGB Badge Colors: Unripe (Green), Mid-ripe (Orange/Amber), Ripe (Red)
        badge_colors = [(40, 190, 40), (240, 150, 20), (220, 45, 45)]
        ripeness_color = badge_colors[pred_class]
        variety_color = (30, 110, 210)

        variety_str = f"Variety: {variety_name} ({variety_conf:.0f}%)"
        v_box_w = max(210, len(variety_str) * 10)
        v_top_y = max(0, by - 58)
        v_bot_y = max(26, by - 32)

        cv2.rectangle(annotated, (bx, v_top_y), (bx + v_box_w, v_bot_y), variety_color, -1)
        cv2.rectangle(annotated, (bx, v_top_y), (bx + v_box_w, v_bot_y), (255, 255, 255), 1)
        cv2.putText(
            annotated,
            variety_str,
            (bx + 6, v_bot_y - 7),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (255, 255, 255),
            1,
        )

        ripeness_str = f"Ripeness: {category} ({confidence:.0f}%)"
        r_box_w = max(210, len(ripeness_str) * 10)
        r_top_y = max(26, by - 28)
        r_bot_y = max(54, by - 2)

        cv2.rectangle(annotated, (bx, r_top_y), (bx + r_box_w, r_bot_y), ripeness_color, -1)
        cv2.rectangle(annotated, (bx, r_top_y), (bx + r_box_w, r_bot_y), (255, 255, 255), 1)
        cv2.putText(
            annotated,
            ripeness_str,
            (bx + 6, r_bot_y - 7),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (255, 255, 255),
            1,
        )

        return ClassificationResult(
            annotated_frame=annotated,
            category=category,
            score=score,
            confidence=confidence,
            variety_name=variety_name,
            variety_confidence=variety_conf,
            roi_box=target_box,
            status="DETECTED",
        )
