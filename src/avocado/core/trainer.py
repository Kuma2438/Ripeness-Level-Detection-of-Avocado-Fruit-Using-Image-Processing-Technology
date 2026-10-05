"""PyTorch CNN Training and Evaluation Pipeline."""

from pathlib import Path
import random
from typing import List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import torchvision.transforms as transforms

from avocado.core.model import AvocadoCNN, load_model_checkpoint, save_model_checkpoint


class AvocadoTrainer:
    """Trains and evaluates AvocadoCNN models on directory datasets."""

    def __init__(
        self,
        dataset_dir: Path | str,
        model_save_path: Path | str,
        default_classes: Optional[List[str]] = None,
        device: Optional[torch.device | str] = None,
    ) -> None:
        self.dataset_dir = Path(dataset_dir)
        self.model_save_path = Path(model_save_path)
        self.classes: List[str] = default_classes or []

        if device is None or device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        elif isinstance(device, str):
            self.device = torch.device(device)
        else:
            self.device = device

        self.model: Optional[AvocadoCNN] = None
        self.trained: bool = False

        self.transform = transforms.Compose([
            transforms.Resize((128, 128)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        self.load_or_train()

    def train_model(
        self,
        epochs: int = 4,
        split_ratio: float = 0.70,
        batch_size: int = 32,
        lr: float = 0.001,
        max_train_per_class: int = 60,
        max_test_per_class: int = 30,
    ) -> bool:
        """Trains the CNN on the dataset directory and evaluates on holdout set."""
        if not self.dataset_dir.is_dir():
            return False

        folders = [
            f.name
            for f in self.dataset_dir.iterdir()
            if f.is_dir() and f.name.lower() != "varieties"
        ]
        if not folders:
            return False

        self.classes = sorted(folders)
        train_x_list: List[torch.Tensor] = []
        train_y_list: List[int] = []
        test_x_list: List[torch.Tensor] = []
        test_y_list: List[int] = []

        rng = random.Random(42)

        for class_idx, class_name in enumerate(self.classes):
            folder_path = self.dataset_dir / class_name
            valid_exts = {".jpg", ".jpeg", ".png", ".bmp"}
            files = [f for f in folder_path.iterdir() if f.suffix.lower() in valid_exts]

            if not files:
                continue

            rng.shuffle(files)
            split_idx = max(1, int(len(files) * split_ratio))
            train_files = files[:split_idx]
            test_files = files[split_idx:] if split_idx < len(files) else files[:1]

            for fpath in train_files[:max_train_per_class]:
                img_bgr = cv2.imread(str(fpath))
                if img_bgr is not None and img_bgr.size > 0:
                    img_rgb = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
                    train_x_list.append(self.transform(img_rgb))
                    train_y_list.append(class_idx)

            for fpath in test_files[:max_test_per_class]:
                img_bgr = cv2.imread(str(fpath))
                if img_bgr is not None and img_bgr.size > 0:
                    img_rgb = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
                    test_x_list.append(self.transform(img_rgb))
                    test_y_list.append(class_idx)

        if len(train_x_list) < 2:
            return False

        train_x_t = torch.stack(train_x_list).to(self.device)
        train_y_t = torch.tensor(train_y_list, dtype=torch.long).to(self.device)

        dataset = TensorDataset(train_x_t, train_y_t)
        dataloader = DataLoader(dataset, batch_size=min(batch_size, len(train_x_list)), shuffle=True)

        self.model = AvocadoCNN(num_classes=len(self.classes)).to(self.device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)

        self.model.train()
        for _ in range(epochs):
            for imgs, labels in dataloader:
                optimizer.zero_grad()
                outputs = self.model(imgs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

        self.trained = True

        test_acc = 100.0
        if test_x_list:
            self.model.eval()
            test_x_t = torch.stack(test_x_list).to(self.device)
            test_y_t = torch.tensor(test_y_list, dtype=torch.long).to(self.device)
            with torch.no_grad():
                test_outputs = self.model(test_x_t)
                _, test_preds = torch.max(test_outputs, 1)
                correct = (test_preds == test_y_t).sum().item()
                test_acc = (correct / len(test_y_list)) * 100.0

        save_model_checkpoint(self.model, self.classes, self.model_save_path)
        return True

    def load_or_train(self) -> None:
        """Loads weights from disk or runs initial training."""
        if self.model_save_path.is_file():
            try:
                model, classes = load_model_checkpoint(self.model_save_path, self.device)
                if model is not None:
                    self.model = model
                    self.classes = classes
                    self.trained = True
                    return
            except Exception:
                pass

        self.train_model()

    def predict(self, crop_bgr: np.ndarray) -> Tuple[str, float]:
        """Runs inference on a BGR image crop."""
        if not self.trained or self.model is None or crop_bgr is None or crop_bgr.size == 0:
            return "Unknown", 0.0

        try:
            self.model.eval()
            img_rgb = Image.fromarray(cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB))
            img_tensor = self.transform(img_rgb).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(img_tensor)
                probabilities = torch.softmax(outputs, dim=1)[0]
                conf, pred_idx = torch.max(probabilities, dim=0)

            pred_class_name = self.classes[pred_idx.item()] if self.classes else "Unknown"
            confidence_pct = float(conf.item() * 100.0)
            return pred_class_name, confidence_pct
        except Exception:
            return "Unknown", 0.0
