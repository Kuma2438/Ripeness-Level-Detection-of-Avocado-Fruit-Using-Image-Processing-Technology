"""Unit tests for AvocadoCNN PyTorch model and serialization."""

from pathlib import Path
import sys
import tempfile
import unittest

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    import torch
    from avocado.core.model import AvocadoCNN, load_model_checkpoint, save_model_checkpoint
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class TestModel(unittest.TestCase):
    def test_model_forward_shape(self) -> None:
        if not TORCH_AVAILABLE:
            self.skipTest("torch is not installed in current environment")

        model = AvocadoCNN(num_classes=3)
        dummy_input = torch.randn(2, 3, 128, 128)
        output = model(dummy_input)
        self.assertEqual(output.shape, (2, 3))

    def test_model_save_and_load(self) -> None:
        if not TORCH_AVAILABLE:
            self.skipTest("torch is not installed in current environment")

        model = AvocadoCNN(num_classes=3)
        classes = ["unripe", "mid_ripe", "ripe"]

        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "test_model.pth"
            save_model_checkpoint(model, classes, model_path)
            self.assertTrue(model_path.is_file())

            loaded_model, loaded_classes = load_model_checkpoint(model_path, torch.device("cpu"))
            self.assertIsNotNone(loaded_model)
            self.assertEqual(loaded_classes, classes)

            dummy_input = torch.randn(1, 3, 128, 128)
            out = loaded_model(dummy_input)
            self.assertEqual(out.shape, (1, 3))

    def test_model_export_torchscript(self) -> None:
        if not TORCH_AVAILABLE:
            self.skipTest("torch is not installed in current environment")

        from avocado.core.model import export_to_torchscript
        model = AvocadoCNN(num_classes=3)
        with tempfile.TemporaryDirectory() as tmpdir:
            ts_path = Path(tmpdir) / "model.ts"
            export_to_torchscript(model, ts_path, device=torch.device("cpu"))
            self.assertTrue(ts_path.is_file())
            self.assertGreater(ts_path.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
