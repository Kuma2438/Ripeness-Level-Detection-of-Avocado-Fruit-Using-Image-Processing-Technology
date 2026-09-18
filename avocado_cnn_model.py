import os
import random
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import torchvision.transforms as transforms
from PIL import Image

# 1. Custom Lightweight CNN Model for Avocado Ripeness & Variety Classification
class AvocadoCNN(nn.Module):
    def __init__(self, num_classes=3):
        super(AvocadoCNN, self).__init__()
        
        # Conv Block 1
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2)
        )
        # Conv Block 2
        self.conv2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2)
        )
        # Conv Block 3
        self.conv3 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2)
        )
        
        # Adaptive pooling & FC classifier
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(inplace=True),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.gap(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x

# 2. Fast PyTorch CNN Engine with Automatic 70% Train / 30% Test Split
class PyTorchCNNEngine:
    def __init__(self, dataset_dir, model_save_path, default_classes=None):
        self.dataset_dir = dataset_dir
        self.model_save_path = model_save_path
        self.classes = default_classes if default_classes else []
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.trained = False

        self.transform = transforms.Compose([
            transforms.Resize((128, 128)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        self.load_or_train()

    def train_model(self, epochs=4, split_ratio=0.70):
        if not os.path.exists(self.dataset_dir):
            return False

        folders = [f for f in os.listdir(self.dataset_dir) if os.path.isdir(os.path.join(self.dataset_dir, f))]
        if len(folders) == 0:
            return False

        self.classes = sorted(folders)
        train_x_list, train_y_list = [], []
        test_x_list, test_y_list = [], []

        random.seed(42) # Fixed seed for reproducible 70/30 split

        for class_idx, class_name in enumerate(self.classes):
            folder_path = os.path.join(self.dataset_dir, class_name)
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            
            if len(files) == 0:
                continue

            random.shuffle(files)
            
            # --- Automatic 70% Train / 30% Test Split ---
            split_idx = max(1, int(len(files) * split_ratio))
            train_files = files[:split_idx]
            test_files = files[split_idx:] if split_idx < len(files) else files[:1]

            # Read 70% Train Images
            for fname in train_files[:60]: # Fast interactive loader
                fpath = os.path.join(folder_path, fname)
                img_bgr = cv2.imread(fpath)
                if img_bgr is not None and img_bgr.size > 0:
                    img_resized = cv2.resize(img_bgr, (128, 128))
                    img_rgb = Image.fromarray(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))
                    train_x_list.append(self.transform(img_rgb))
                    train_y_list.append(class_idx)

            # Read 30% Test Images (Holdout Evaluation Set)
            for fname in test_files[:30]:
                fpath = os.path.join(folder_path, fname)
                img_bgr = cv2.imread(fpath)
                if img_bgr is not None and img_bgr.size > 0:
                    img_resized = cv2.resize(img_bgr, (128, 128))
                    img_rgb = Image.fromarray(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))
                    test_x_list.append(self.transform(img_rgb))
                    test_y_list.append(class_idx)

        if len(train_x_list) < 2:
            return False

        train_x_t = torch.stack(train_x_list).to(self.device)
        train_y_t = torch.tensor(train_y_list, dtype=torch.long).to(self.device)

        dataset = TensorDataset(train_x_t, train_y_t)
        dataloader = DataLoader(dataset, batch_size=min(32, len(train_x_list)), shuffle=True)

        # Train CNN Model on 70% Training Set
        self.model = AvocadoCNN(num_classes=len(self.classes)).to(self.device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        self.model.train()
        for epoch in range(epochs):
            for imgs, labels in dataloader:
                optimizer.zero_grad()
                outputs = self.model(imgs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

        self.trained = True

        # --- Automatic Accuracy Evaluation on 30% Unseen Test Set ---
        test_acc = 100.0
        if len(test_x_list) > 0:
            self.model.eval()
            test_x_t = torch.stack(test_x_list).to(self.device)
            test_y_t = torch.tensor(test_y_list, dtype=torch.long).to(self.device)
            with torch.no_grad():
                test_outputs = self.model(test_x_t)
                _, test_preds = torch.max(test_outputs, 1)
                correct = (test_preds == test_y_t).sum().item()
                test_acc = (correct / len(test_y_list)) * 100.0

        # Save PyTorch CNN weights and class payload
        os.makedirs(os.path.dirname(self.model_save_path), exist_ok=True)
        checkpoint = {
            'state_dict': self.model.state_dict(),
            'classes': self.classes
        }
        torch.save(checkpoint, self.model_save_path)
        print(f"PyTorch CNN trained on 70% set ({len(train_x_list)} imgs). Auto evaluated on 30% test set ({len(test_x_list)} imgs) -> Accuracy: {test_acc:.2f}%. Model saved to {self.model_save_path}")
        return True

    def load_or_train(self):
        if os.path.exists(self.model_save_path):
            try:
                checkpoint = torch.load(self.model_save_path, map_location=self.device)
                self.classes = checkpoint['classes']
                self.model = AvocadoCNN(num_classes=len(self.classes)).to(self.device)
                self.model.load_state_dict(checkpoint['state_dict'])
                self.model.eval()
                self.trained = True
                return
            except Exception as e:
                print(f"Failed to load PyTorch CNN model: {e}, retraining...")

        self.train_model()

    def predict(self, crop_bgr):
        if not self.trained or self.model is None or crop_bgr is None or crop_bgr.size == 0:
            return "Unknown", 0.0

        try:
            self.model.eval()
            img_resized = cv2.resize(crop_bgr, (128, 128))
            img_rgb = Image.fromarray(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))
            img_tensor = self.transform(img_rgb).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(img_tensor)
                probabilities = torch.softmax(outputs, dim=1)[0]
                conf, pred_idx = torch.max(probabilities, dim=0)

            pred_class_name = self.classes[pred_idx.item()]
            confidence_pct = conf.item() * 100.0
            return pred_class_name, confidence_pct
        except Exception as e:
            print(f"CNN Prediction error: {e}")
            return "Unknown", 0.0
