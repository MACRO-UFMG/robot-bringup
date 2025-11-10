from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import PushRosNamespace
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='robot1',
        description='Namespace do robô'
    )

    params_arg = DeclareLaunchArgument(
        'params_file',
        default_value='/home/ros/ros2_ws/src/config/nav2_victor.yaml',
        description='Arquivo de parâmetros do Nav2'
    )

    map_arg = DeclareLaunchArgument(
        'map',
        default_value='/home/ros/ros2_ws/src/maps/quarter_map.yaml',
        description='Mapa para localization'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Usar tempo de simulação (true/false)'
    )

    namespace = LaunchConfiguration('namespace')
    params_file = LaunchConfiguration('params_file')
    map_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')

    bringup_dir = get_package_share_directory('nav2_bringup')

    # Lança a localização (AMCL)
    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'localization_launch.py')
        ),
        launch_arguments={
            'namespace': namespace,
            'params_file': params_file,
            'map': map_file,
            'use_sim_time': use_sim_time,
        }.items()
    )

    # Lança a navegação completa (planner, controller, BT, etc.)
    # navigation_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(bringup_dir, 'launch', 'navigation_launch.py')
    #     ),
    #     launch_arguments={
    #         'namespace': namespace,
    #         'params_file': params_file,
    #         'use_sim_time': use_sim_time,
    #     }.items()
    # )

    # Agrupa tudo sob o namespace
    namespaced_group = GroupAction([
        PushRosNamespace(namespace),
        localization_launch,
        # navigation_launch
    ])

    return LaunchDescription([
        namespace_arg,
        params_arg,
        map_arg,
        use_sim_time_arg,
        namespaced_group
    ])