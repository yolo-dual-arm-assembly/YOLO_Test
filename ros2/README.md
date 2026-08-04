# ROS2 탐지 → 로봇팔 제어 파이프라인

YOLO 탐지 결과를 성공/실패 flag와 함께 발행하고, 그 flag로 로봇팔 동작을 결정하는
ROS2 패키지 모음이다. **Windows에서는 빌드하지 않는다** — Ubuntu 22.04(Humble) 또는
24.04(Jazzy) 환경에서 아래 절차대로 빌드한다.

## 구성

```
ros2/src/
├── yolo_robot_msgs/      # DetectionResult.msg 정의 (ament_cmake)
└── yolo_robot_vision/    # 노드 2개 (ament_python)
    ├── detector_node     # 이미지 토픽 구독 → YOLO 추론 → /yolo/detection 발행
    └── arm_controller_node  # flag 구독 → 디바운싱/워치독 → 팔 명령 (예시)
```

### 메시지: `yolo_robot_msgs/msg/DetectionResult`

| 필드 | 의미 |
|---|---|
| `header` | 원본 이미지 프레임의 stamp/frame_id |
| `detected` | **탐지 성공/실패 flag** (물체 없음·추론 에러 모두 `false`) |
| `class_name`, `confidence` | 최고 신뢰도 탐지의 클래스/신뢰도 |
| `cx`, `cy`, `width`, `height` | bbox 중심과 크기 (픽셀) |

탐지 실패여도 **매 프레임 발행**한다. 구독자는 `detected=false`(실패)와
"메시지 자체가 안 옴"(탐지 노드 다운)을 구분할 수 있고, 후자는
`arm_controller_node`의 워치독이 잡아서 정지 명령을 낸다.

## 빌드 (Linux)

```bash
# 의존성
sudo apt install ros-$ROS_DISTRO-cv-bridge ros-$ROS_DISTRO-vision-opencv
pip install ultralytics==8.4.102

# 빌드 — 이 폴더(ros2/)가 곧 워크스페이스다
cd ros2
colcon build --symlink-install
source install/setup.bash
```

기존 워크스페이스가 있다면 `src/` 아래 두 패키지를 그쪽 `src/`로 복사(또는 심링크)해도 된다.

## 실행

```bash
# 카메라 드라이버 (예: USB 웹캠 → /image_raw 발행)
sudo apt install ros-$ROS_DISTRO-v4l2-camera
ros2 run v4l2_camera v4l2_camera_node

# 탐지 + 팔 제어 노드
ros2 launch yolo_robot_vision detection.launch.py \
    model_path:=/absolute/path/to/best.pt \
    target_class:=robot
```

## 카메라 없이 정지 이미지로 테스트

```bash
sudo apt install ros-$ROS_DISTRO-image-publisher
ros2 run image_publisher image_publisher_node /absolute/path/to/object/bus.jpg \
    --ros-args -r image_raw:=/image_raw

# 다른 터미널에서 flag 확인
ros2 topic echo /yolo/detection
```

`detected: true`와 bbox 좌표가 흐르면 정상. 물체 없는 이미지를 주면
`detected: false`가 매 프레임 발행되는 것을 확인할 수 있다.

## 주요 파라미터

| 노드 | 파라미터 | 기본값 | 의미 |
|---|---|---|---|
| detector | `model_path` | `best.pt` | 가중치 경로 (절대경로 권장) |
| detector | `confidence_threshold` | `0.5` | YOLO conf 임계값 |
| detector | `target_class` | `""` | 지정 시 해당 클래스만 탐지로 인정 |
| arm_controller | `min_confidence` | `0.6` | 이 값 미만이면 실패로 취급 |
| arm_controller | `hit_frames` | `3` | 연속 N프레임 탐지 시 이동 시작 |
| arm_controller | `miss_frames` | `5` | 연속 N프레임 실패 시 홈 복귀 |
| arm_controller | `watchdog_sec` | `1.0` | 이 시간 동안 메시지 없으면 정지 |

## 실제 로봇팔 연결

`arm_controller_node.py`의 `command_move` / `command_home` / `command_stop`은
로그만 찍는 자리표시자다. MoveIt2나 제조사 드라이버 호출로 교체하면 된다.
픽셀 좌표(`cx`, `cy`)를 로봇 좌표로 바꾸려면 카메라 캘리브레이션
(hand-eye calibration)과 깊이 정보가 추가로 필요하다.
