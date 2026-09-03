import os
import cv2
import numpy as np
from avocado_cnn_model import PyTorchCNNEngine

class AvocadoVarietyTrainer:
    def __init__(self, dataset_dir=r"d:\Project\dataset\varieties", model_path=r"d:\Project\models\variety_cnn.pth"):
        self.dataset_dir = dataset_dir
        self.model_path = model_path
        
        # PyTorch CNN Engine
        self.cnn_engine = PyTorchCNNEngine(
            dataset_dir=self.dataset_dir,
            model_save_path=self.model_path
        )
        
        self.classes = self.cnn_engine.classes
        self.trained = self.cnn_engine.trained

    def train(self):
        """Train PyTorch CNN model on variety dataset"""
        success = self.cnn_engine.train_model(epochs=6)
        self.classes = self.cnn_engine.classes
        self.trained = self.cnn_engine.trained
        
        if success:
            # Count total images
            total_samples = 0
            for class_name in self.classes:
                folder_path = os.path.join(self.dataset_dir, class_name)
                if os.path.exists(folder_path):
                    total_samples += len([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
            return True, total_samples, len(self.classes)
        else:
            return False, 0, 0

    def load_or_train(self):
        self.cnn_engine.load_or_train()
        self.classes = self.cnn_engine.classes
        self.trained = self.cnn_engine.trained

    def predict(self, crop_bgr):
        """Predicts variety class and confidence score using PyTorch CNN"""
        return self.cnn_engine.predict(crop_bgr)

if __name__ == "__main__":
    trainer = AvocadoVarietyTrainer()
    trainer.train()
