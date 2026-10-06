"""Synthetic avocado dataset sample generator for testing and demonstration."""

from pathlib import Path
from typing import Optional
import cv2
import numpy as np

from avocado.config import get_project_root


def generate_sample_dataset(output_dir: Optional[Path | str] = None, samples_per_category: int = 15) -> Path:
    """Generates synthetic avocado sample images across 3 ripeness categories."""
    out_path = Path(output_dir) if output_dir else get_project_root() / "dataset"
    categories = ["unripe", "mid_ripe", "ripe"]

    for cat in categories:
        (out_path / cat).mkdir(parents=True, exist_ok=True)

    np.random.seed(42)

    for cat in categories:
        for i in range(samples_per_category):
            img = np.ones((480, 640, 3), dtype=np.uint8) * 220

            center = (320 + np.random.randint(-15, 16), 240 + np.random.randint(-15, 16))
            axes = (90 + np.random.randint(-5, 6), 130 + np.random.randint(-8, 9))
            angle = np.random.randint(-15, 16)

            if cat == "unripe":
                base_bgr = [np.random.randint(30, 60), np.random.randint(130, 180), np.random.randint(40, 80)]
            elif cat == "mid_ripe":
                base_bgr = [np.random.randint(20, 45), np.random.randint(85, 115), np.random.randint(65, 95)]
            else:
                base_bgr = [np.random.randint(25, 45), np.random.randint(30, 55), np.random.randint(40, 65)]

            mask = np.zeros((480, 640), dtype=np.uint8)
            cv2.ellipse(mask, center, axes, angle, 0, 360, 255, -1)

            for c in range(3):
                noise = np.random.normal(0, 15, (480, 640)).astype(np.int16)
                channel = np.clip(base_bgr[c] + noise, 0, 255).astype(np.uint8)
                img[:, :, c] = np.where(mask == 255, channel, img[:, :, c])

            spots_mask = (np.random.rand(480, 640) > 0.95) & (mask == 255)
            img[spots_mask] = np.clip(img[spots_mask].astype(int) - 35, 0, 255).astype(np.uint8)

            filepath = out_path / cat / f"{cat}_{i+1:02d}.jpg"
            cv2.imwrite(str(filepath), img)

    return out_path
