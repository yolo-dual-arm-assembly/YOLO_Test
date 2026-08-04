"""탐지 노드 + 팔 제어 예시 노드를 함께 띄우는 런치 파일.

사용 예:
    ros2 launch yolo_robot_vision detection.launch.py \
        model_path:=/home/user/YOLO_Test/best.pt image_topic:=/image_raw
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument("model_path", default_value="best.pt"),
            DeclareLaunchArgument("image_topic", default_value="/image_raw"),
            DeclareLaunchArgument("confidence_threshold", default_value="0.5"),
            DeclareLaunchArgument("target_class", default_value=""),
            DeclareLaunchArgument("min_confidence", default_value="0.6"),
            Node(
                package="yolo_robot_vision",
                executable="detector_node",
                name="yolo_detector",
                output="screen",
                parameters=[
                    {
                        "model_path": LaunchConfiguration("model_path"),
                        "image_topic": LaunchConfiguration("image_topic"),
                        "confidence_threshold": LaunchConfiguration(
                            "confidence_threshold"
                        ),
                        "target_class": LaunchConfiguration("target_class"),
                    }
                ],
            ),
            Node(
                package="yolo_robot_vision",
                executable="arm_controller_node",
                name="arm_controller",
                output="screen",
                parameters=[
                    {"min_confidence": LaunchConfiguration("min_confidence")}
                ],
            ),
        ]
    )
