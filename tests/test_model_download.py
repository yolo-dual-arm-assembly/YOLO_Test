from pathlib import Path

import pytest

import yolo_demo


def test_missing_model_paths_returns_only_missing_models(tmp_path: Path) -> None:
    existing_model = tmp_path / yolo_demo.DOWNLOADABLE_MODEL_FILENAMES[0]
    existing_model.touch()

    assert yolo_demo.missing_model_paths(tmp_path) == [
        tmp_path / filename
        for filename in yolo_demo.DOWNLOADABLE_MODEL_FILENAMES[1:]
    ]


def test_missing_model_paths_excludes_local_custom_models(tmp_path: Path) -> None:
    assert "best.pt" in yolo_demo.MODEL_FILENAMES
    assert "best.pt" not in yolo_demo.DOWNLOADABLE_MODEL_FILENAMES
    assert tmp_path / "best.pt" not in yolo_demo.missing_model_paths(tmp_path)


def test_download_model_returns_downloaded_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model_path = tmp_path / "yolov8n.pt"

    def fake_download(path: Path) -> str:
        path.write_bytes(b"model")
        return str(path)

    monkeypatch.setattr(yolo_demo, "attempt_download_asset", fake_download)

    assert yolo_demo.download_model(model_path) == model_path


def test_download_model_raises_when_file_was_not_created(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model_path = tmp_path / "yolov8n.pt"
    monkeypatch.setattr(
        yolo_demo,
        "attempt_download_asset",
        lambda path: str(path),
    )

    with pytest.raises(FileNotFoundError, match="모델 다운로드에 실패했습니다"):
        yolo_demo.download_model(model_path)
