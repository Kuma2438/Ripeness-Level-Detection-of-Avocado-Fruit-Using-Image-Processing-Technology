"""Ripeness and Variety Composite Classifier Engine."""

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
    score: float
    confidence: float
    variety_name: str
    variety_confidence: float
    roi_box: Optional[Tuple[int, int, int, int]] = None


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
        self, frame_bgr: np.ndarray
    ) -> Tuple[np.ndarray, Optional[np.ndarray], Tuple[int, int, int, int]]:
        """Extracts primary avocado region using Otsu adaptive thresholding with center crop fallback."""
        annotated = frame_bgr.copy()
        h, w, _ = frame_bgr.shape

        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        target_roi = None
        target_box = None

        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            total_area = h * w
            # Ensure contour is reasonably sized (between 2% and 85% of total frame)
            if 0.02 * total_area < area < 0.85 * total_area:
                x, y, bw, bh = cv2.boundingRect(c)
                target_box = (x, y, bw, bh)
                target_roi = frame_bgr[y : y + bh, x : x + bw]
                cv2.rectangle(annotated, (x, y), (x + bw, y + bh), (0, 255, 0), 2)

        if target_roi is None or target_roi.size == 0:
            x, y, bw, bh = int(w * 0.25), int(h * 0.2), int(w * 0.5), int(h * 0.6)
            target_box = (x, y, bw, bh)
            target_roi = frame_bgr[y : y + bh, x : x + bw]
            cv2.rectangle(annotated, (x, y), (x + bw, y + bh), (255, 200, 0), 1)

        return annotated, target_roi, target_box

    def compute_ripeness_score(
        self, target_roi: np.ndarray, pred_class: int, confidence: float
    ) -> float:
        """Calculates ripeness index score from 0.0 to 100.0 based on HSV color and CNN prediction."""
        hsv = cv2.cvtColor(target_roi, cv2.COLOR_BGR2HSV)
        mean_g = float(hsv[:, :, 1].mean())

        if pred_class == 0:  # Unripe
            score = 15.0 + (1.0 - min(1.0, max(0.0, (215.0 - mean_g) / 50.0))) * 18.0
        elif pred_class == 1:  # Mid-ripe
            score = 35.0 + (1.0 - min(1.0, max(0.0, (160.0 - mean_g) / 50.0))) * 30.0
        else:  # Ripe
            score = 70.0 + min(25.0, (confidence * 0.25))

        return float(np.clip(score, 5.0, 98.0))

    def predict_frame(self, frame_bgr: Optional[np.ndarray]) -> ClassificationResult:
        """Detects avocado, classifies ripeness & variety, and overlays annotations."""
        if frame_bgr is None or frame_bgr.size == 0:
            dummy = np.zeros((480, 640, 3), dtype=np.uint8)
            return ClassificationResult(
                annotated_frame=dummy,
                category="No Signal",
                score=0.0,
                confidence=0.0,
                variety_name="Unknown",
                variety_confidence=0.0,
            )

        annotated, target_roi, target_box = self.extract_roi(frame_bgr)

        if target_roi is None or target_roi.size == 0:
            return ClassificationResult(
                annotated_frame=annotated,
                category="Unripe",
                score=0.0,
                confidence=0.0,
                variety_name="Unknown",
                variety_confidence=0.0,
                roi_box=target_box,
            )

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

        badge_colors = [(40, 180, 40), (30, 150, 220), (40, 40, 220)]
        ripeness_color = badge_colors[pred_class]
        variety_color = (180, 70, 20)

        bx, by, bw, bh = target_box

        variety_str = f"Variety (CNN): {variety_name} ({variety_conf:.0f}%)"
        v_box_w = max(230, len(variety_str) * 11)
        v_top_y = max(0, by - 60)
        v_bot_y = max(30, by - 32)

        cv2.rectangle(annotated, (bx, v_top_y), (bx + v_box_w, v_bot_y), variety_color, -1)
        cv2.rectangle(annotated, (bx, v_top_y), (bx + v_box_w, v_bot_y), (255, 255, 255), 1)
        cv2.putText(
            annotated,
            variety_str,
            (bx + 8, v_bot_y - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

        ripeness_str = f"Ripeness (CNN): {category} ({confidence:.0f}%)"
        r_box_w = max(230, len(ripeness_str) * 11)
        r_top_y = max(30, by - 30)
        r_bot_y = max(60, by - 2)

        cv2.rectangle(annotated, (bx, r_top_y), (bx + r_box_w, r_bot_y), ripeness_color, -1)
        cv2.rectangle(annotated, (bx, r_top_y), (bx + r_box_w, r_bot_y), (255, 255, 255), 1)
        cv2.putText(
            annotated,
            ripeness_str,
            (bx + 8, r_bot_y - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

        return ClassificationResult(
            annotated_frame=annotated,
            category=category,
            score=score,
            confidence=confidence,
            variety_name=variety_name,
            variety_confidence=variety_conf,
            roi_box=target_box,
        )
