from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='laser_to_body',
            arguments=['0', '0', '0', '0', '0', '0', 'livox_frame', 'body'],
            # x, y, z, yaw, pitch, roll, frame_id, child_frame_id
            output='screen'
        )
    ])