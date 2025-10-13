from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    
    scout_base_launch_path = FindPackageShare('scout_base').find('scout_base') + '/launch/scout_base.launch.py'
    # livox_launch_path = FindPackageShare('livox_ros_driver2').find('livox_ros_driver2') + '/launch_ROS2/rviz_MID360_launch.py'

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(scout_base_launch_path)
        ),
        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource(livox_launch_path)
        # ),
        Node(
            package='scout_bringup',
            executable='target_transform',
            name='target_transform_node',
            output='screen'
        ),

        Node(
            package='scout_bringup',
            executable='pose_transform',
            name='pose_transform_node',
            output='screen'
        ),
    ])
