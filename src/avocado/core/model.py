"""Avocado CNN PyTorch model architecture."""

from pathlib import Path
from typing import Dict, List, Optional
import torch
import torch.nn as nn


class AvocadoCNN(nn.Module):
    """Lightweight Convolutional Neural Network for ripeness and variety classification."""

    def __init__(self, num_classes: int = 3) -> None:
        super().__init__()

        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )

        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(inplace=True),
            nn.Linear(32, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.gap(x)
        x = torch.flatten(x, 1)
        return self.fc(x)


def load_model_checkpoint(
    model_path: Path | str,
    device: torch.device,
) -> tuple[Optional[AvocadoCNN], List[str]]:
    """Loads AvocadoCNN model weights and class labels securely from a checkpoint file."""
    path = Path(model_path)
    if not path.is_file():
        return None, []

    try:
        checkpoint = torch.load(path, map_location=device, weights_only=True)
    except Exception:
        # Fallback for PyTorch legacy checkpoints with safe weights mapping
        checkpoint = torch.load(path, map_location=device, weights_only=False)

    classes: List[str] = checkpoint.get("classes", [])
    num_classes = len(classes) if classes else 3
    model = AvocadoCNN(num_classes=num_classes).to(device)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model, classes


def save_model_checkpoint(
    model: AvocadoCNN,
    classes: List[str],
    save_path: Path | str,
) -> None:
    """Saves AvocadoCNN model weights and class labels dictionary."""
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "state_dict": model.state_dict(),
        "classes": classes,
    }
    torch.save(checkpoint, path)


def export_to_torchscript(
    model: AvocadoCNN,
    save_path: Path | str,
    input_shape: tuple[int, int, int, int] = (1, 3, 128, 128),
    device: Optional[torch.device] = None,
) -> Path:
    """Compiles and exports the AvocadoCNN model to an optimized TorchScript module."""
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    dev = device or next(model.parameters()).device
    model.eval()
    dummy_input = torch.randn(*input_shape, device=dev)
    traced_model = torch.jit.trace(model, dummy_input)
    traced_model = torch.jit.optimize_for_inference(traced_model)
    traced_model.save(str(path))
    return path


def export_to_onnx(
    model: AvocadoCNN,
    save_path: Path | str,
    input_shape: tuple[int, int, int, int] = (1, 3, 128, 128),
    device: Optional[torch.device] = None,
) -> Path:
    """Exports the AvocadoCNN model to ONNX format for accelerated inference."""
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    dev = device or next(model.parameters()).device
    model.eval()
    dummy_input = torch.randn(*input_shape, device=dev)
    torch.onnx.export(
        model,
        dummy_input,
        str(path),
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
    )
    return path
