# minimal_nav2.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Planejador global
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'expected_planner_frequency': 1.0,
                'global_frame': 'map',
                'robot_base_frame': 'fast_lio/base_link',
                'odom_topic': '/fast_lio/odom',
            }]
        ),

        # Controlador local
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'controller_frequency': 10.0,
                'odom_topic': '/fast_lio/odom',
                'cmd_vel_topic': '/cmd_vel',
                'global_frame': 'map',
                'robot_base_frame': 'fast_lio/base_link',
            }]
        ),

        # Servidor de comportamento (BT)
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'global_frame': 'map',
                'robot_base_frame': 'fast_lio/base_link',
            }]
        ),

        # Costmaps (para evitar obstáculos)
        Node(
            package='nav2_costmap_2d',
            executable='costmap_2d_node',
            name='global_costmap',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'global_frame': 'map',
                'robot_base_frame': 'fast_lio/base_link',
                'odom_topic': '/fast_lio/odom',
                'scan_topic': '/livox/scan',
                'plugin_names': ['static_layer', 'obstacle_layer'],
                'plugin_types': ['nav2_costmap_2d::StaticLayer', 'nav2_costmap_2d::ObstacleLayer'],
            }]
        ),
    ])
