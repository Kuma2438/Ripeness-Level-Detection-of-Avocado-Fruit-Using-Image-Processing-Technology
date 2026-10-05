"""Unit tests for DualCameraManager fallback and frame generation."""

from pathlib import Path
import sys
import unittest

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    import numpy as np
    from avocado.camera.manager import DualCameraManager
    from avocado.config import load_config
    CAMERA_DEPS_AVAILABLE = True
except ImportError:
    CAMERA_DEPS_AVAILABLE = False


class TestCamera(unittest.TestCase):
    def test_camera_manager_simulated_stream(self) -> None:
        if not CAMERA_DEPS_AVAILABLE:
            self.skipTest("OpenCV or NumPy not installed")

        config = load_config()
        # Force simulation mode with -1 ids
        cam_manager = DualCameraManager(config=config, cam1_id=-1, cam2_id=-1)

        f1, f2 = cam_manager.read_frames()
        self.assertIsNotNone(f1)
        self.assertIsNotNone(f2)
        self.assertEqual(f1.shape, (config.camera.height, config.camera.width, 3))
        self.assertEqual(f2.shape, (config.camera.height, config.camera.width, 3))

        cam_manager.release()


if __name__ == "__main__":
    unittest.main()
