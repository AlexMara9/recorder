# tul_launch.py
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    config_path = os.path.join(
        get_package_share_directory("tul"),
        "config",
        "config.yml"
    )

    return LaunchDescription([
        Node(
            package="tul",
            executable="tul_node",
            name="tul_node",
            parameters=[{"config_path": config_path}]
        )
    ])