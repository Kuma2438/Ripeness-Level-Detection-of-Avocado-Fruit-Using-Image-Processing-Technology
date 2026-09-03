import os
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

# 2. Fast PyTorch CNN Engine with In-Memory Pre-loaded Tensors
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

    def train_model(self, epochs=4):
        if not os.path.exists(self.dataset_dir):
            return False

        folders = [f for f in os.listdir(self.dataset_dir) if os.path.isdir(os.path.join(self.dataset_dir, f))]
        if len(folders) == 0:
            return False

        self.classes = sorted(folders)
        x_list = []
        y_list = []

        for class_idx, class_name in enumerate(self.classes):
            folder_path = os.path.join(self.dataset_dir, class_name)
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            
            # Limit up to 60 images per class for fast interactive training
            files = files[:60]
            
            for fname in files:
                fpath = os.path.join(folder_path, fname)
                img_bgr = cv2.imread(fpath)
                if img_bgr is not None and img_bgr.size > 0:
                    img_resized = cv2.resize(img_bgr, (128, 128))
                    img_rgb = Image.fromarray(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))
                    img_tensor = self.transform(img_rgb)
                    x_list.append(img_tensor)
                    y_list.append(class_idx)

        if len(x_list) < 2:
            return False

        x_tensors = torch.stack(x_list).to(self.device)
        y_tensors = torch.tensor(y_list, dtype=torch.long).to(self.device)

        dataset = TensorDataset(x_tensors, y_tensors)
        dataloader = DataLoader(dataset, batch_size=min(32, len(x_list)), shuffle=True)

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

        # Save PyTorch CNN weights and class names payload
        os.makedirs(os.path.dirname(self.model_save_path), exist_ok=True)
        checkpoint = {
            'state_dict': self.model.state_dict(),
            'classes': self.classes
        }
        torch.save(checkpoint, self.model_save_path)
        print(f"PyTorch CNN Model trained on {len(x_list)} images across {len(self.classes)} classes. Saved to {self.model_save_path}")
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
