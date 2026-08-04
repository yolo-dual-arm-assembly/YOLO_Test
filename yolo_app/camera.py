"""운영체제별 카메라 탐색과 OpenCV 캡처 생성."""
from __future__ import annotations

import sys
from pathlib import Path

import cv2


WINDOWS_CAMERA_INDEXES = (1, 0)
PREFERRED_CAMERA_NAMES = ("C270", "Logi")
LINUX_V4L_SYS_DIR = Path("/sys/class/video4linux")
CAPTURE_WIDTH = 1280
CAPTURE_HEIGHT = 720


def open_camera(
    index: int,
    width: int = CAPTURE_WIDTH,
    height: int = CAPTURE_HEIGHT,
) -> cv2.VideoCapture:
    """카메라를 열고 실시간 표시에 적합한 옵션을 설정한다."""
    backend = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY
    capture = cv2.VideoCapture(index, backend)
    if not capture.isOpened() and backend != cv2.CAP_ANY:
        capture = cv2.VideoCapture(index, cv2.CAP_ANY)
    if not capture.isOpened():
        raise RuntimeError(
            f"카메라 {index}번을 열 수 없습니다. "
            "웹캠 연결과 다른 앱의 점유 여부를 확인하세요."
        )

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return capture


def linux_camera_indexes(
    sys_dir: Path = LINUX_V4L_SYS_DIR,
) -> tuple[int, ...]:
    """리눅스 video 노드에서 USB 외장 카메라를 앞세운다."""
    entries: list[tuple[int, str]] = []
    for node in sys_dir.glob("video*"):
        suffix = node.name.removeprefix("video")
        if not suffix.isdigit():
            continue
        try:
            name = (node / "name").read_text(encoding="utf-8").strip()
        except OSError:
            continue
        entries.append((int(suffix), name))

    capture_index_by_name: dict[str, int] = {}
    for index, name in sorted(entries):
        capture_index_by_name.setdefault(name, index)

    preferred = [
        index
        for name, index in capture_index_by_name.items()
        if any(tag.casefold() in name.casefold() for tag in PREFERRED_CAMERA_NAMES)
    ]
    others = [
        index
        for index in capture_index_by_name.values()
        if index not in preferred
    ]
    return tuple(preferred + others) or (0,)


def preferred_camera_indexes() -> tuple[int, ...]:
    """운영체제별 카메라 인덱스를 우선순위대로 반환한다."""
    if sys.platform.startswith("linux"):
        return linux_camera_indexes()
    return WINDOWS_CAMERA_INDEXES


def open_preferred_camera(
    width: int = CAPTURE_WIDTH,
    height: int = CAPTURE_HEIGHT,
) -> tuple[cv2.VideoCapture, int]:
    """선호 카메라를 열어 ``(capture, index)``로 반환한다."""
    last_error: RuntimeError | None = None
    for index in preferred_camera_indexes():
        try:
            capture = open_camera(index, width, height)
        except RuntimeError as error:
            last_error = error
            continue
        grabbed, _frame = capture.read()
        if grabbed:
            return capture, index
        capture.release()
        last_error = RuntimeError(
            f"카메라 {index}번이 프레임을 반환하지 않습니다."
        )

    if last_error is None:
        last_error = RuntimeError(
            "사용 가능한 카메라를 찾지 못했습니다."
        )
    raise last_error


# 이전 코드가 가져가던 private 이름도 당분간 유지한다.
_linux_camera_indexes = linux_camera_indexes
