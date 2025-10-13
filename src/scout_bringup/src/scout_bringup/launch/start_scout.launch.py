from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    
    scout_base_launch_path = FindPackageShare('scout_base').find('scout_base') + '/launch/scout_base.launch.py'
    livox_launch_path = FindPackageShare('livox_ros_driver2').find('livox_ros_driver2') + '/launch_ROS2/rviz_MID360_launch.py'

    return LaunchDescription([
#        ExecuteProcess(
#            cmd=['sudo', 'ip', 'link', 'set', 'can0', 'up', 'type', 'can', 'bitrate', '500000'],
#            output='screen',
#            shell=True
#        ),
#        ExecuteProcess(
#            cmd=['sudo', 'ifconfig', 'eth0', '192.168.1.5'],
#            output='screen',
#            shell=True
#        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(scout_base_launch_path)
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(livox_launch_path)
        ),
        # Adicione outros nós conforme necessário
    ])
