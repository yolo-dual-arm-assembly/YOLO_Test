from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = PROJECT_DIR / "object"
OUTPUT_DIR = PROJECT_DIR / "result"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}
PREVIEW_SIZE = (620, 650)
CONFIDENCE_THRESHOLD = 0.05
