"""Unit tests for AvocadoClassifier, empty box detection, and avocado validation."""

from pathlib import Path
import sys
import unittest

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    import cv2
    import numpy as np
    import torch
    from avocado.config import load_config
    from avocado.core.classifier import AvocadoClassifier
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


class TestClassifier(unittest.TestCase):
    def setUp(self) -> None:
        if not DEPS_AVAILABLE:
            self.skipTest("Required dependencies (torch/numpy/opencv) not installed")
        self.config = load_config()
        self.classifier = AvocadoClassifier(config=self.config)

    def test_empty_frame_returns_no_avocado(self) -> None:
        """Verifies that an empty flat background returns 'No Avocado' and score is None."""
        empty_frame = np.ones((480, 640, 3), dtype=np.uint8) * 200
        res = self.classifier.predict_frame(empty_frame)

        self.assertEqual(res.category, "No Avocado")
        self.assertIsNone(res.score)
        self.assertEqual(res.status, "NO_AVOCADO")
        self.assertIsNone(res.roi_box)
        self.assertEqual(res.annotated_frame.shape, empty_frame.shape)

    def test_classifier_none_frame(self) -> None:
        """Verifies that None frame returns 'No Signal' and score is None."""
        res = self.classifier.predict_frame(None)
        self.assertEqual(res.category, "No Signal")
        self.assertIsNone(res.score)
        self.assertEqual(res.status, "NO_SIGNAL")

    def test_foreign_object_human_skin_returns_not_avocado(self) -> None:
        """Verifies that a skin-tone colored object (hand/fingers) is detected as 'Not Avocado'."""
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 220
        # Draw hand/skin-tone ellipse in RGB: R=215, G=145, B=115
        cv2.ellipse(frame, (320, 240), (80, 110), 0, 0, 360, (215, 145, 115), -1)

        res = self.classifier.predict_frame(frame)
        self.assertEqual(res.category, "Not Avocado")
        self.assertIsNone(res.score)
        self.assertEqual(res.status, "NOT_AVOCADO")
        self.assertIsNotNone(res.roi_box)

    def test_foreign_object_bright_red_returns_not_avocado(self) -> None:
        """Verifies that a bright red object (cup/apple/marker) is detected as 'Not Avocado'."""
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 220
        # Draw red ellipse in RGB: R=220, G=30, B=30
        cv2.ellipse(frame, (320, 240), (80, 110), 0, 0, 360, (220, 30, 30), -1)

        res = self.classifier.predict_frame(frame)
        self.assertEqual(res.category, "Not Avocado")
        self.assertIsNone(res.score)
        self.assertEqual(res.status, "NOT_AVOCADO")

    def test_valid_avocado_sample_returns_ripeness(self) -> None:
        """Verifies that an avocado-colored fruit (green/unripe) classifies successfully with active score."""
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 220
        # Draw green avocado ellipse in RGB: R=50, G=160, B=45
        cv2.ellipse(frame, (320, 240), (80, 120), 0, 0, 360, (50, 160, 45), -1)

        res = self.classifier.predict_frame(frame)
        self.assertIn(res.category, ["Unripe", "Mid-ripe", "Ripe"])
        self.assertEqual(res.status, "DETECTED")
        self.assertIsNotNone(res.score)
        self.assertGreaterEqual(res.score, 5.0)
        self.assertLessEqual(res.score, 98.0)
        self.assertIsInstance(res.variety_name, str)
        self.assertIsNotNone(res.roi_box)


if __name__ == "__main__":
    unittest.main()
