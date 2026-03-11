from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    imu_arg = DeclareLaunchArgument('imu', default_value='/imu/data')
    lidar_arg = DeclareLaunchArgument('lidar_odom', default_value='/lidar_odom')
    wheel_arg = DeclareLaunchArgument('wheel_odom', default_value='/odom')
    out_arg = DeclareLaunchArgument('filter_odom_out', default_value='/filter_odom')

    params_file_arg = DeclareLaunchArgument(
        'params_file',
        default_value=PathJoinSubstitution([
            FindPackageShare('adaptive_odom_filter'),
            'config',
            'adaptive_filter_parameters.yaml'
        ])
    )

    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value=''
    )

    node = Node(
        package='adaptive_odom_filter',
        executable='adaptive_odom_filter_node',
        name='adaptive_odom_filter',
        namespace=LaunchConfiguration('namespace'),
        output='screen',
        parameters=[LaunchConfiguration('params_file')],
        remappings=[
            ('/imu/data', LaunchConfiguration('imu')),
            ('/lidar_odom', LaunchConfiguration('lidar_odom')),
            ('/odom', LaunchConfiguration('wheel_odom')),
            ('/filter_odom', LaunchConfiguration('filter_odom_out')),
        ],
        arguments=['--ros-args', '--log-level', 'adaptive_odom_filter:=debug'],
    )

    return LaunchDescription([
        imu_arg,
        lidar_arg,
        wheel_arg,
        out_arg,
        params_file_arg,
        namespace_arg,
        node
    ])