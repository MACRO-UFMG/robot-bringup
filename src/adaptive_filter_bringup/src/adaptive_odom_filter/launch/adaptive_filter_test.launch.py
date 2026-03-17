from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # -------------------- Arguments (same names as ROS1) --------------------
    filter_arg   = DeclareLaunchArgument('filter',  default_value='true')
    test_arg     = DeclareLaunchArgument('test',    default_value='true')

    imu_arg      = DeclareLaunchArgument('imu',                  default_value='/imu/data')
    lidar_arg    = DeclareLaunchArgument('lidar_slam_odom',      default_value='/lidar/odom')
    track_arg    = DeclareLaunchArgument('tracking_camera_odom', default_value='/camera/odom')
    depth_arg    = DeclareLaunchArgument('depth_camera_odom',    default_value='/camera/odom')
    wheel_arg    = DeclareLaunchArgument('wheel_odom',           default_value='/wheel/odom')

    left_cam_arg  = DeclareLaunchArgument('stereo_cam_left',     default_value='/t265/fisheye2/image_raw')
    right_cam_arg = DeclareLaunchArgument('stereo_cam_right',    default_value='/t265/fisheye1/image_raw')
    color_arg     = DeclareLaunchArgument('color_image',         default_value='/d435i/color/image_raw')

    out_odom_arg  = DeclareLaunchArgument('filter_odom',         default_value='/filter_odom')
    rtab_srv_arg  = DeclareLaunchArgument('rtabmap_service',     default_value='/rtabmap/reset_odom_to_pose')

    # -------------------- Parameters YAML --------------------
    params_yaml = PathJoinSubstitution([
        FindPackageShare('adaptive_odom_filter'),
        'config',
        'adaptive_filter_parameters.yaml'
    ])

    # -------------------- Optional fake publishers --------------------
    fake_pub_node = Node(
        condition=IfCondition(LaunchConfiguration('test')),
        package='adaptive_odom_filter',
        # use the ROS 2 console_script you set in setup.py
        executable='fake_odometry_path.py',
        name='fake_odometry_path',
        output='screen',
        parameters=[{
            'camera_rate_hz': 5.0,
            'wheel_rate_hz':  10.0,
            'lidar_rate_hz':  5.0,
            'imu_rate_hz':    10.0,
        }]
        # If you ever want to remap the fake topics, add "remappings=[(...)]" here.
    )

    # -------------------- EKF filter node --------------------
    filter_node = Node(
        condition=IfCondition(LaunchConfiguration('filter')),
        package='adaptive_odom_filter',
        # C++ node from the ROS 2 port (the executable you added in CMake)
        executable='adaptive_odom_filter_node',
        name='adaptive_odom_filter',
        output='screen',
        parameters=[params_yaml],
        remappings=[
            ('/livox/imu',                   LaunchConfiguration('imu')),
            ('/Odometry',                 LaunchConfiguration('lidar_slam_odom')),
            ('/tracking_odom',              LaunchConfiguration('tracking_camera_odom')),
            ('/depth_odom',                 LaunchConfiguration('depth_camera_odom')),
            ('/robot/odom',                       LaunchConfiguration('wheel_odom')),
            ('/left_camera',                LaunchConfiguration('stereo_cam_left')),
            ('/rigth_camera',               LaunchConfiguration('stereo_cam_right')),
            ('/camera_color',               LaunchConfiguration('color_image')),
            ('/filter_odom',                LaunchConfiguration('filter_odom')),
            # service remap works via the same remappings tuple:
            ('/rtabmap/reset_odom_to_pose', LaunchConfiguration('rtabmap_service')),
        ],
    )

    return LaunchDescription([
        # args
        filter_arg, test_arg,
        imu_arg, lidar_arg, track_arg, depth_arg, wheel_arg,
        left_cam_arg, right_cam_arg, color_arg,
        out_odom_arg, rtab_srv_arg,
        # nodes
        fake_pub_node,
        filter_node,
    ])
