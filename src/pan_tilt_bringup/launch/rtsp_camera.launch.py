#!/usr/bin/env python3
"""
ROS 2 Launch file for RTSP Camera System
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Declare launch arguments
    config_file_arg = DeclareLaunchArgument(
        'config_file',
        default_value=PathJoinSubstitution([
            FindPackageShare('rtsp_cam'),
            'config',
            'cameras.json'
        ]),
        description='Path to camera configuration file'
    )
    
    jpeg_quality_arg = DeclareLaunchArgument(
        'jpeg_quality',
        default_value='20',
        description='JPEG compression quality (0-100)'
    )
    
    launch_rviz_arg = DeclareLaunchArgument(
        'launch_rviz',
        default_value='false',
        description='Launch RViz2 for visualization'
    )
    
    publisher_only_arg = DeclareLaunchArgument(
        'publisher_only',
        default_value='true',
        description='Only run publisher (streamer runs in separate container)'
    )
    
    # ROS 2 Publisher Node
    publisher_node = Node(
        package='rtsp_cam',
        executable='rtsp_publisher_node.py',
        name='rtsp_publisher',
        output='screen',
        parameters=[{
            'config_file': LaunchConfiguration('config_file'),
            'jpeg_quality': LaunchConfiguration('jpeg_quality'),
        }],
        condition=UnlessCondition(LaunchConfiguration('publisher_only'))
    )
    
    # Static transform publishers for camera frames
    camera1_main_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='camera1_main_tf',
        arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'camera1_main_optical_frame'],
        output='screen'
    )
    
    camera1_sub_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='camera1_sub_tf',
        arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'camera1_sub_optical_frame'],
        output='screen'
    )
    
    camera2_main_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='camera2_main_tf',
        arguments=['1', '0', '0', '0', '0', '0', 'base_link', 'camera2_main_optical_frame'],
        output='screen'
    )
    
    camera2_sub_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='camera2_sub_tf',
        arguments=['1', '0', '0', '0', '0', '0', 'base_link', 'camera2_sub_optical_frame'],
        output='screen'
    )
    
    # RViz2 node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', PathJoinSubstitution([
            FindPackageShare('rtsp_cam'),
            'config',
            'camera_display.rviz'
        ])],
        output='screen',
        condition=IfCondition(LaunchConfiguration('launch_rviz'))
    )
    
    # Publisher-only group (for container usage)
    publisher_only_group = GroupAction(
        condition=IfCondition(LaunchConfiguration('publisher_only')),
        actions=[
            Node(
                package='rtsp_cam',
                executable='rtsp_publisher_node.py',
                name='rtsp_publisher',
                output='screen',
                parameters=[{
                    'config_file': LaunchConfiguration('config_file'),
                    'jpeg_quality': LaunchConfiguration('jpeg_quality'),
                }]
            )
        ]
    )
    
    return LaunchDescription([
        # Launch arguments
        config_file_arg,
        jpeg_quality_arg,
        launch_rviz_arg,
        publisher_only_arg,
        
        # Nodes
        publisher_node,
        publisher_only_group,
        
        # Transform publishers
        camera1_main_tf,
        camera1_sub_tf,
        camera2_main_tf,
        camera2_sub_tf,
        
        # RViz2
        rviz_node,
    ])
