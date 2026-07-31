import argparse
from pathlib import Path

from ultralytics import YOLO


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_CONFIG = PROJECT_DIR / "train_set" / "data.yaml"
DEFAULT_BASE_MODEL = PROJECT_DIR / "yolov8n.pt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="로컬 데이터셋으로 YOLO 모델을 파인튜닝합니다."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_CONFIG,
        help="데이터셋 정의 yaml 경로 (기본: train_set/data.yaml)",
    )
    parser.add_argument(
        "--base-model",
        type=Path,
        default=DEFAULT_BASE_MODEL,
        help="베이스 가중치(.pt) 경로 (기본: yolov8n.pt)",
    )
    parser.add_argument("--epochs", type=int, default=50, help="학습 epoch 수")
    parser.add_argument("--imgsz", type=int, default=640, help="학습 이미지 크기")
    parser.add_argument("--batch", type=int, default=8, help="배치 크기")
    parser.add_argument(
        "--name", default="custom_detect", help="runs/ 하위 결과 폴더 이름"
    )
    return parser.parse_args()


def train_model(args: argparse.Namespace) -> None:
    """Fine-tune a pretrained YOLO model with the local dataset."""
    data_config = args.data.resolve()
    base_model = args.base_model.resolve()
    if not data_config.is_file():
        raise SystemExit(f"데이터셋 정의 파일이 없습니다: {data_config}")
    if not base_model.is_file():
        raise SystemExit(f"베이스 모델 파일이 없습니다: {base_model}")

    model = YOLO(base_model)
    model.train(
        data=data_config,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=PROJECT_DIR / "runs",
        name=args.name,
    )


if __name__ == "__main__":
    train_model(parse_args())
