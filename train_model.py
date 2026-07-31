from pathlib import Path

from ultralytics import YOLO


PROJECT_DIR = Path(__file__).resolve().parent
DATA_CONFIG = PROJECT_DIR / "train_set" / "data.yaml"
BASE_MODEL = PROJECT_DIR / "yolov8n.pt"


def train_model() -> None:
    """Fine-tune a pretrained YOLO model with the local dataset."""
    model = YOLO(BASE_MODEL)
    model.train(
        data=DATA_CONFIG,
        epochs=50,
        imgsz=640,
        batch=8,
        project=PROJECT_DIR / "runs",
        name="custom_detect",
    )


if __name__ == "__main__":
    train_model()
