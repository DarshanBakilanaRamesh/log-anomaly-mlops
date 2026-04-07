from src.config import METRICS_PATH, MODEL_PATH
from src.models.train import train_model


def test_training_creates_artifacts():
    metrics = train_model()

    assert MODEL_PATH.exists()
    assert METRICS_PATH.exists()
    assert metrics["roc_auc"] >= 0.5
