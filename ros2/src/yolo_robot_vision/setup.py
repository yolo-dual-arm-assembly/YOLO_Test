from setuptools import setup

package_name = "yolo_robot_vision"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/detection.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="BKD",
    maintainer_email="jinwoong0728@gmail.com",
    description="YOLO 탐지 노드와 탐지 flag 기반 로봇팔 제어 예시 노드",
    license="MIT",
    entry_points={
        "console_scripts": [
            "detector_node = yolo_robot_vision.detector_node:main",
            "arm_controller_node = yolo_robot_vision.arm_controller_node:main",
        ],
    },
)
