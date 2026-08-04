"""이전 실행 방식 호환용 진입점.

새 실행 방식은 ``python main.py`` 또는 ``python -m yolo_app``이다.
"""
from yolo_app.config import (
    CONFIDENCE_THRESHOLD,
    IMAGE_EXTENSIONS,
    INPUT_DIR,
    OUTPUT_DIR,
    PREVIEW_SIZE,
    PROJECT_DIR,
)
from yolo_app.models import (
    DEFAULT_MODEL_FILENAME,
    DOWNLOADABLE_MODEL_FILENAMES,
    LOCAL_MODEL_FILENAMES,
    MODEL_FILENAMES,
    MODEL_SPECS,
    SPECS_BY_LABEL,
    ModelSpec,
    available_model_specs,
    download_model,
    missing_model_paths,
)
from yolo_app.viewer import YoloViewer, main

__all__ = [
    "CONFIDENCE_THRESHOLD",
    "IMAGE_EXTENSIONS",
    "INPUT_DIR",
    "OUTPUT_DIR",
    "PREVIEW_SIZE",
    "PROJECT_DIR",
    "DEFAULT_MODEL_FILENAME",
    "DOWNLOADABLE_MODEL_FILENAMES",
    "LOCAL_MODEL_FILENAMES",
    "MODEL_FILENAMES",
    "MODEL_SPECS",
    "SPECS_BY_LABEL",
    "ModelSpec",
    "available_model_specs",
    "download_model",
    "missing_model_paths",
    "YoloViewer",
    "main",
]

if __name__ == "__main__":
    main()
