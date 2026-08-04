"""YOLO로 컴퓨터 마우스를 찾아 OMX를 물체 위 안전 높이까지 이동한다.

VS Code에서 이 파일을 열고 ``Run Python File`` 버튼으로 실행할 수 있다.
Q: 종료 및 홈 복귀, R: 홈 복귀 후 다음 mouse 다시 탐지.
"""
from __future__ import annotations

from pathlib import Path

from yolo_app.omx_controller import OmxConfig
from yolo_app.omx_taught_vision_runner import OmxTaughtVisionRunner
from yolo_app.omx_teaching import OmxTeachingDataset
from yolo_app.serial_ports import default_omx_port


PROJECT_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_DIR / "yolov8n.pt"
TEACHING_PATH = PROJECT_DIR / "omx_mouse_teaching.json"
# 리눅스(/dev/ttyACM0)와 윈도우(COMx)에서 모두 동작하도록 자동 선택한다.
ROBOT_PORT = default_omx_port()
CAMERA_INDEX = 0


def main() -> None:
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"YOLO 모델 파일 없음: {MODEL_PATH}")
    if not TEACHING_PATH.is_file():
        raise RuntimeError(
            f"Mouse 교시 파일 없음: {TEACHING_PATH}\n"
            "yolo_demo.py의 'Mouse 관절 교시 모드'에서 먼저 교시하세요."
        )

    teaching = OmxTeachingDataset.load(TEACHING_PATH)
    runner = OmxTaughtVisionRunner(
        model_path=MODEL_PATH,
        teaching=teaching,
        config=OmxConfig(port=ROBOT_PORT),
        confidence=0.5,
        hit_frames=5,
        camera_index=CAMERA_INDEX,
    )
    runner.run()


if __name__ == "__main__":
    main()
