"""Configuration dataclasses and loaders with dynamic project root resolution."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


def get_project_root() -> Path:
    """Finds the repository root containing configs or models folder."""
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "configs").is_dir() or (parent / "models").is_dir() or (parent / "dataset").is_dir():
            return parent
    return current.parent.parent.parent


@dataclass
class CameraConfig:
    driver: str = "auto"
    cam1_id: int = 0
    cam2_id: Optional[int] = 1
    width: int = 640
    height: int = 480
    fps: int = 30
    auto_fallback: bool = True
    backend: str = "default"


@dataclass
class ModelConfig:
    ripeness_model_path: Path = field(default_factory=lambda: get_project_root() / "models" / "ripeness_cnn.pth")
    variety_model_path: Path = field(default_factory=lambda: get_project_root() / "models" / "variety_cnn.pth")
    image_size: tuple[int, int] = (64, 64)
    device: str = "auto"


@dataclass
class DatasetConfig:
    root_dir: Path = field(default_factory=lambda: get_project_root() / "dataset")
    varieties_dir: Path = field(default_factory=lambda: get_project_root() / "dataset" / "varieties")
    categories: List[str] = field(default_factory=lambda: ["unripe", "mid_ripe", "ripe"])


@dataclass
class TrainingConfig:
    batch_size: int = 16
    epochs: int = 20
    learning_rate: float = 0.001
    validation_split: float = 0.2


@dataclass
class InferenceConfig:
    ripeness_weight_color: float = 0.35
    ripeness_weight_cnn: float = 0.65
    unripe_threshold: float = 35.0
    mid_ripe_threshold: float = 70.0


@dataclass
class AppConfig:
    camera: CameraConfig = field(default_factory=CameraConfig)
    models: ModelConfig = field(default_factory=ModelConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    project_root: Path = field(default_factory=get_project_root)


def load_config(config_path: Optional[Path | str] = None) -> AppConfig:
    """Loads configuration from a YAML file or returns defaults."""
    root = get_project_root()
    if config_path is None:
        default_yaml = root / "configs" / "default.yaml"
        if default_yaml.is_file():
            config_path = default_yaml

    cfg = AppConfig(project_root=root)

    if config_path and Path(config_path).is_file():
        with open(config_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = yaml.safe_load(f) or {}

        if "camera" in data:
            c = data["camera"]
            cfg.camera = CameraConfig(
                driver=c.get("driver", "auto"),
                cam1_id=c.get("cam1_id", 0),
                cam2_id=c.get("cam2_id", 1),
                width=c.get("width", 640),
                height=c.get("height", 480),
                fps=c.get("fps", 30),
                auto_fallback=c.get("auto_fallback", True),
                backend=c.get("backend", "default"),
            )

        if "models" in data:
            m = data["models"]
            r_path = Path(m.get("ripeness_model_path", "models/ripeness_cnn.pth"))
            v_path = Path(m.get("variety_model_path", "models/variety_cnn.pth"))
            cfg.models = ModelConfig(
                ripeness_model_path=r_path if r_path.is_absolute() else root / r_path,
                variety_model_path=v_path if v_path.is_absolute() else root / v_path,
                image_size=tuple(m.get("image_size", [64, 64])),
                device=m.get("device", "auto"),
            )

        if "dataset" in data:
            d = data["dataset"]
            root_d = Path(d.get("root_dir", "dataset"))
            var_d = Path(d.get("varieties_dir", "dataset/varieties"))
            cfg.dataset = DatasetConfig(
                root_dir=root_d if root_d.is_absolute() else root / root_d,
                varieties_dir=var_d if var_d.is_absolute() else root / var_d,
                categories=d.get("categories", ["unripe", "mid_ripe", "ripe"]),
            )

        if "training" in data:
            t = data["training"]
            cfg.training = TrainingConfig(
                batch_size=t.get("batch_size", 16),
                epochs=t.get("epochs", 20),
                learning_rate=t.get("learning_rate", 0.001),
                validation_split=t.get("validation_split", 0.2),
            )

        if "inference" in data:
            i = data["inference"]
            cfg.inference = InferenceConfig(
                ripeness_weight_color=i.get("ripeness_weight_color", 0.35),
                ripeness_weight_cnn=i.get("ripeness_weight_cnn", 0.65),
                unripe_threshold=i.get("unripe_threshold", 35.0),
                mid_ripe_threshold=i.get("mid_ripe_threshold", 70.0),
            )

    return cfg
