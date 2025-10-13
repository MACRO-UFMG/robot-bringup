from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    scout_base_launch_path = FindPackageShare('scout_base').find('scout_base') + '/launch/scout_base.launch.py'
    livox_launch_path      = FindPackageShare('livox_ros_driver2').find('livox_ros_driver2') + '/launch_ROS2/rviz_MID360_launch.py'
    fast_lio_launch_path   = FindPackageShare('fast_lio').find('fast_lio') + '/launch/mapping.launch.py'
    dyn_tf_script_path     = FindPackageShare('scout_bringup').find('scout_bringup') + '/scripts/dynamic_livox_tf.py'

    # pointcloud_to_laserscan node
    pcl2ls = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pcl2ls',
        output='screen',
        # Remap your Livox cloud in; adjust output scan topic if you prefer another name
        remappings=[('cloud_in', '/livox/lidar'), ('scan', '/scan')],
        # Optional parameters — tune only if needed
        # parameters=[{
        #     # 'target_frame': 'base_link',  # uncomment if you want forced projection frame
        #     'min_height': -1.0,
        #     'max_height':  1.0,
        #     'range_min': 0.05,
        #     'range_max': 30.0,
        # }]
    )

    # Run your dynamic TF helper (plain Python script)
    dyn_tf = ExecuteProcess(
        cmd=['python3', dyn_tf_script_path],
        output='screen'
    )

    return LaunchDescription([
        # --- network bring-up examples you had (kept commented) ---
        # ExecuteProcess(
        #     cmd=['sudo', 'ip', 'link', 'set', 'can0', 'up', 'type', 'can', 'bitrate', '500000'],
        #     output='screen',
        #     shell=True
        # ),
        # ExecuteProcess(
        #     cmd=['sudo', 'ifconfig', 'eth0', '192.168.1.5'],
        #     output='screen',
        #     shell=True
        # ),

        # Your existing includes
        IncludeLaunchDescription(PythonLaunchDescriptionSource(scout_base_launch_path)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(livox_launch_path)),

        # New: FAST-LIO mapping
        IncludeLaunchDescription(PythonLaunchDescriptionSource(fast_lio_launch_path)),

        # New: pointcloud_to_laserscan node
        pcl2ls,

        # New: dynamic TF script
        dyn_tf,
    ])
