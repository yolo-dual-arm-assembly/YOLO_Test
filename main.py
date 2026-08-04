"""YOLO·웹캠·OMX 통합 데스크톱 애플리케이션 실행 진입점.

윈도우와 리눅스 모두 ``python main.py``로 실행한다. 의존성이 없는 Python으로
실행하면 아래 점검이 의존성을 갖춘 Python을 찾아 대신 실행한다.
"""

from yolo_app.bootstrap import ensure_runtime

# viewer는 Pillow·OpenCV·ultralytics를 import하므로 런타임 점검 뒤에 부른다.
ensure_runtime()

from yolo_app.viewer import main  # noqa: E402


if __name__ == "__main__":
    main()
