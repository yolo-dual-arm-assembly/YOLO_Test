from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = PROJECT_DIR / "object"
OUTPUT_DIR = PROJECT_DIR / "result"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}
PREVIEW_SIZE = (620, 650)
CONFIDENCE_THRESHOLD = 0.1

# OMX 연동 기본 리소스. 창과 실행기는 이 경로를 주입받을 수도 있다.
OMX_MODEL_PATH = PROJECT_DIR / "yolov8n.pt"
OMX_CALIBRATION_PATH = PROJECT_DIR / "calibration.json"
OMX_TEACHING_PATH = PROJECT_DIR / "omx_mouse_teaching.json"
