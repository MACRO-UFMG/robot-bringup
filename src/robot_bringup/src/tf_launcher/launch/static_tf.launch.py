from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="livox_to_body_tf",
            arguments=["0", "0", "0", "0", "0", "0", "livox_frame", "body"]
        )
    ])
