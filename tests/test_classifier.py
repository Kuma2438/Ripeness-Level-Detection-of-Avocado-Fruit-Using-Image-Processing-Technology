"""Unit tests for AvocadoClassifier and ripeness score computation."""

from pathlib import Path
import sys
import unittest

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
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

    def test_classifier_prediction_dummy_frame(self) -> None:
        dummy_frame = np.ones((480, 640, 3), dtype=np.uint8) * 200
        res = self.classifier.predict_frame(dummy_frame)

        self.assertIn(res.category, ["Unripe", "Mid-ripe", "Ripe", "No Signal"])
        self.assertGreaterEqual(res.score, 0.0)
        self.assertLessEqual(res.score, 100.0)
        self.assertGreaterEqual(res.confidence, 0.0)
        self.assertLessEqual(res.confidence, 100.0)
        self.assertIsInstance(res.variety_name, str)
        self.assertEqual(res.annotated_frame.shape, dummy_frame.shape)

    def test_classifier_none_frame(self) -> None:
        res = self.classifier.predict_frame(None)
        self.assertEqual(res.category, "No Signal")
        self.assertEqual(res.score, 0.0)


if __name__ == "__main__":
    unittest.main()
