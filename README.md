# YOLO 이미지 분석 도구

`object` 폴더의 이미지를 YOLO 모델로 분석하고, 원본 이미지와 분석 결과를
나란히 보여 주는 Windows용 Tkinter GUI 프로그램입니다. 분석 결과는 모델별로
`result` 폴더에 저장됩니다.

## 1. 준비 사항

- Windows 10 또는 Windows 11
- 64비트 Python 3.13 권장
- 인터넷 연결(최초 패키지 및 모델 설치 시 필요)

이 프로젝트는 Python 3.13 기준으로 사용합니다. MSYS2의 Python이나 아직 패키지
지원이 충분하지 않은 새 Python 버전 대신
[python.org](https://www.python.org/downloads/)에서 설치한 64비트 Python 3.13을
권장합니다. Python 설치 화면에서는 `Add python.exe to PATH` 또는 Python
Launcher 설치 항목을 선택합니다.

프로젝트 최상위 폴더에는 최소한 다음 파일과 폴더가 있어야 합니다.

```text
YOLO/
├─ yolo_demo.py
├─ yolo_app/
├─ train_model.py
├─ requirements.txt
├─ pyproject.toml
├─ tests/
├─ train_set/
├─ object/
└─ result/
```

`object`와 `result` 폴더는 프로그램이 없으면 자동으로 만듭니다. 모델 파일
`yolov8n.pt`, `yolov8m.pt`, `yolo11m-seg.pt`가 없으면 프로그램을 처음 실행할 때
Ultralytics 공식 배포본을 프로젝트 최상위 폴더에 자동으로 다운로드합니다.

## 2. 프로젝트 폴더에서 PowerShell 열기

파일 탐색기에서 프로젝트 폴더를 연 뒤 주소 표시줄에 `powershell`을 입력하거나,
PowerShell에서 직접 프로젝트 폴더로 이동합니다.

```powershell
Set-Location "C:\프로젝트를\저장한\경로\YOLO"
```

현재 위치가 맞는지 확인합니다.

```powershell
Get-Location
Get-ChildItem
```

출력 목록에 `yolo_demo.py`와 `requirements.txt`가 보여야 합니다. 프로젝트 복사본이
여러 개 있다면, 패키지를 설치한 폴더와 프로그램을 실행하는 폴더가 같은지 특히
확인하십시오.

## 3. 가상환경 만들기

설치된 Python 목록을 확인합니다.

```powershell
py -0p
```

Python 3.13으로 프로젝트 전용 가상환경을 만듭니다.

```powershell
py -3.13 -m venv .venv
```

가상환경을 활성화합니다.

```powershell
.\.venv\Scripts\Activate.ps1
```

PowerShell 실행 정책 때문에 활성화가 차단되면 현재 PowerShell 창에서만 정책을
완화한 뒤 다시 활성화합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

활성화되면 명령 프롬프트 앞에 `(.venv)`가 표시됩니다.

## 4. 패키지 설치

반드시 프로젝트 폴더에서 다음 명령을 실행합니다.

```powershell
python -m pip install --upgrade pip
python -m pip install -r .\requirements.txt
```

설치가 끝난 뒤 현재 Python과 `pip`가 모두 `.venv`를 가리키는지 확인합니다.

```powershell
python -c "import sys; print(sys.executable)"
python -m pip --version
```

두 출력 경로에 모두 프로젝트의 `.venv`가 포함되어 있어야 합니다. 이어서 주요
패키지를 실제로 import할 수 있는지 확인합니다.

```powershell
python -c "from PIL import Image; from ultralytics import YOLO; print('의존성 확인 완료')"
python -m tkinter
```

마지막 명령을 실행했을 때 작은 Tk 창이 나타나면 GUI 실행 준비가 끝난 것입니다.

### 가상환경을 활성화하지 않고 설치하는 방법

활성화 과정이 번거롭거나 셸 설정의 영향을 피하고 싶다면 가상환경의 Python을
직접 지정해도 됩니다.

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

이 방식을 사용했다면 실행할 때도 같은 Python을 직접 지정합니다.

```powershell
.\.venv\Scripts\python.exe .\yolo_demo.py
```

## 5. 분석할 이미지 준비

분석할 이미지를 프로젝트의 `object` 폴더에 넣습니다. 지원 확장자는 다음과
같습니다.

- `.png`
- `.jpg`
- `.jpeg`
- `.bmp`

모델 파일은 처음 실행할 때 자동으로 준비되며, 이후에는 다운로드한 파일을
재사용합니다.

## 6. 프로그램 실행

가상환경이 활성화된 PowerShell에서 실행합니다.

```powershell
python .\yolo_demo.py
```

프로그램을 실행하면 `object` 폴더의 이미지 목록이 왼쪽에 표시됩니다. 이미지를
선택하면 오른쪽에서 원본과 분석 결과를 비교할 수 있습니다. 기존 결과가 있으면
시작할 때 유지할지 다시 분석할지 묻습니다.

처음 실행할 때 모델 파일이 없으면 GUI 하단 콘솔에 다운로드 진행 상황이
표시됩니다. 세 모델을 모두 준비한 뒤 분석을 시작하므로 첫 실행에는 인터넷 연결과
추가 시간이 필요합니다. 이미 존재하는 모델 파일은 다시 다운로드하지 않습니다.

상단의 모델 선택 목록에서 다음 모델을 전환할 수 있습니다.

- `best.pt` (Robot Custom): `train_model.py`로 직접 학습한 로봇 객체 탐지 모델.
  파일이 있을 때만 목록에 표시됩니다.
- `yolov8n.pt`: 가장 가볍고 빠른 객체 탐지 모델
- `yolov8m.pt`: 속도와 정확도의 균형을 고려한 객체 탐지 모델
- `yolo11m-seg.pt`: 객체별 마스크를 생성하는 인스턴스 세그멘테이션 모델

`best.pt`는 자동 다운로드 대상이 아닙니다. `train_set` 데이터셋을 준비한 뒤
다음 명령으로 학습하면 `runs/custom_detect/weights/best.pt`가 생성되며, 이를
프로젝트 최상위 폴더에 복사하면 Robot Custom 모델이 활성화됩니다.

```powershell
python .\train_model.py
python .\train_model.py --epochs 100 --batch 16  # 하이퍼파라미터 변경 예시
```

결과 파일은 다음 형식의 폴더에 저장됩니다.

```text
result/
├─ best/
├─ yolov8n/
├─ yolov8m/
└─ yolo11m-seg/
```

모델별 폴더가 분리되어 있으므로 모델을 전환해도 다른 모델의 결과를 덮어쓰지
않습니다.

## 7. 자주 발생하는 오류

### `ModuleNotFoundError: No module named 'PIL'`

`PIL`은 `Pillow` 패키지가 제공하는 모듈입니다. 대부분 패키지를 설치한 Python과
프로그램을 실행한 Python이 서로 다를 때 이 오류가 발생합니다. 프로젝트 폴더에서
가상환경의 Python을 명시해 다시 설치하고 실행합니다.

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
.\.venv\Scripts\python.exe -c "from PIL import Image; print('Pillow 정상')"
.\.venv\Scripts\python.exe .\yolo_demo.py
```

`pip install ...`처럼 `pip`만 단독으로 실행하지 말고, 항상
`python -m pip ...` 또는 `.\.venv\Scripts\python.exe -m pip ...` 형식을
사용하십시오.

### `ModuleNotFoundError: No module named 'ultralytics'`

현재 실행 중인 Python에 의존성이 설치되지 않은 상태입니다.

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

설치 중 오류가 발생했다면 마지막 오류 메시지를 확인합니다. Python 버전과 경로는
다음 명령으로 확인할 수 있습니다.

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
```

### `No module named '_tkinter'` 또는 GUI 창이 열리지 않음

현재 Python에 Tkinter가 포함되지 않았을 수 있습니다. python.org의 Windows용
64비트 Python 3.13을 설치할 때 `tcl/tk and IDLE` 항목을 포함한 뒤 가상환경을
다시 만드십시오.

### 모델 파일이 없다는 메시지

프로그램 시작 시 누락된 모델은 자동으로 다운로드합니다. 다운로드 오류가
표시되면 인터넷 연결과 디스크 여유 공간을 확인한 뒤 프로그램을 다시 실행합니다.
파일명을 임의로 바꾸면 프로그램이 찾지 못합니다.

자동 다운로드가 계속 실패하면 프로젝트 폴더에서 다음 명령을 실행해 모델을
수동으로 준비할 수 있습니다.

```powershell
.\.venv\Scripts\python.exe -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
.\.venv\Scripts\python.exe -c "from ultralytics import YOLO; YOLO('yolov8m.pt')"
.\.venv\Scripts\python.exe -c "from ultralytics import YOLO; YOLO('yolo11m-seg.pt')"
```

### 입력 이미지가 없다는 메시지

이미지를 `yolo_demo.py` 옆이 아니라 `object` 폴더 안에 넣었는지, 파일 확장자가
지원 목록에 포함되는지 확인한 뒤 프로그램을 다시 실행합니다.

### 설치는 했는데 계속 같은 모듈 오류가 발생함

아래 두 명령의 경로가 같은 Python 환경을 가리키는지 비교합니다.

```powershell
python -c "import sys; print(sys.executable)"
python -m pip --version
```

예를 들어 프로그램은 `C:\msys64\ucrt64\bin\python3.14.exe`로 실행하면서 패키지는
다른 Python 또는 `.venv`에 설치했다면 모듈을 찾을 수 없습니다. VS Code를
사용한다면 `Python: Select Interpreter`에서 프로젝트의
`.venv\Scripts\python.exe`를 선택하십시오.

## 8. 개발 확인

코드를 수정한 뒤에는 최소한 문법 검사를 실행합니다.

```powershell
python -m compileall yolo_app yolo_demo.py train_model.py
```

단위 테스트(모델 다운로드·분석 루프 로직)는 다음과 같이 실행합니다.

```powershell
python -m pip install pytest
python -m pytest -q
```
