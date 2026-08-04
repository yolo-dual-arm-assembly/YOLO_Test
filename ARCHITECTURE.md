# 애플리케이션 구조

이 프로젝트는 하나의 데스크톱 앱이지만, 기능은 다음 경계를 지킨다.

```text
main.py / train_model.py             실행 진입점
              │
              ▼
viewer.py / webcam.py / omx_panel.py Tkinter 화면과 작업 조립
              │
              ▼
analysis.py / training.py            YOLO 분석·학습 유스케이스
camera.py / models.py                카메라·모델 리소스
omx_*.py                             OMX 통신·교시·비전 이동
```

## 모듈 책임

- `analysis.py`: 파일 이미지 추론 루프. Tkinter나 카메라를 알지 않는다.
- `training.py`: 학습 설정 검증과 학습 실행. `train_model.py`는 CLI 변환만 한다.
- `models.py`: 사용 가능한 모델 목록과 다운로드를 담당한다.
- `camera.py`: 운영체제별 카메라 탐색과 OpenCV 캡처 생성을 담당한다.
- `serial_ports.py`: 운영체제별 OMX 시리얼 포트 탐색을 담당한다.
- `webcam.py`: 웹캠 실시간 추론 창을 담당하며 장치 탐색은 `camera.py`에 맡긴다.
- `viewer.py`: 메인 화면, 이미지 선택, 분석 진행 표시를 조립한다.
- `omx_panel.py`: 메인 화면의 OMX 패널과 관련 창·스레드의 생명주기를 관리한다.
- `omx_controller.py`: Dynamixel 통신과 로봇 관절 명령을 담당한다.
- `omx_teaching.py`: 화면 좌표와 실제 관절값 교시 데이터 및 보간을 담당한다.
- `omx_*_window.py`: OMX 전용 Tkinter 창만 담당한다.
- `omx_*_runner.py`: 카메라 탐지부터 로봇 이동까지의 실행 흐름을 담당한다.

## 운영체제 대응

리눅스와 윈도우는 같은 코드로 실행하며 실행 방식을 나누지 않는다. OS마다
달라지는 값은 실행 시점에 확인해서 정한다.

- 시리얼 포트: 이름 규칙이 `/dev/ttyACM0`과 `COMx`로 달라, 연결된 포트를
  조회해 USB 장치를 고른다. 조회 결과가 없을 때만 OS별 기본값을 쓰고,
  GUI 입력칸과 `--port` 옵션으로 언제든 직접 지정할 수 있다.
- 한글 글꼴: 설치된 글꼴이 OS마다 다르므로 후보를 우선순위대로 두고 실제로
  설치된 글꼴을 고른다. 설치되지 않은 이름을 폴백으로 쓰면 Tk가 조용히 다른
  글꼴로 대체하므로, 폴백도 시스템이 이미 쓰는 글꼴에서 가져온다.

통합 GUI의 공식 실행 방식은 `python main.py`이다. 패키지 실행 방식인
`python -m yolo_app`과 설치 후 명령인 `yolo-app`도 같은 `viewer.main`을
호출한다. `yolo_demo.py`는 기존 사용자와 실행 설정을 위한 호환 파일이다.

## 새 기능을 추가할 때

1. 계산·파일 처리·검증 로직은 GUI 콜백 안에 넣지 않고 독립 함수나 서비스
   모듈로 만든다.
2. 새 카메라 사용 기능은 `camera.py`의 캡처 함수를 재사용한다.
3. 새 로봇 동작은 실행기 모듈로 만들고 `OmxPanel`에는 시작·중지 버튼과 상태
   연결만 추가한다.
4. 새 YOLO 모델은 `models.py`에 등록하고, 추론 방식 자체가 다를 때만 별도
   분석 모듈을 추가한다.
5. GUI를 import하지 않고 검사할 수 있는 로직에는 `tests/` 단위 테스트를 붙인다.

## 향후 패키지 분리 기준

현재 규모에서는 파일을 `yolo_app` 바로 아래에 두는 편이 실행과 디버깅이 쉽다.
각 영역의 파일이 더 늘어나면 그때 다음 하위 패키지로 이동한다.

```text
yolo_app/
├─ vision/    # analysis, models, training
├─ ui/        # viewer, webcam, console
├─ camera/    # 장치 탐색, 캡처 백엔드
└─ robot/     # OMX controller, teaching, runner, window
```

이 이동은 기능 추가와 동시에 하지 않고, 기존 import 호환 모듈을 남기는 별도
리팩터링으로 진행한다.
