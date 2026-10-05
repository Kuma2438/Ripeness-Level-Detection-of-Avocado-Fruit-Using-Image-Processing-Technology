"""Core models, classification and training modules."""

from avocado.core.model import AvocadoCNN, load_model_checkpoint, save_model_checkpoint
from avocado.core.trainer import AvocadoTrainer
from avocado.core.classifier import AvocadoClassifier, ClassificationResult

__all__ = [
    "AvocadoCNN",
    "load_model_checkpoint",
    "save_model_checkpoint",
    "AvocadoTrainer",
    "AvocadoClassifier",
    "ClassificationResult",
]
