#!/bin/bash
set -e

# Source ROS 2 environment
source /opt/ros/jazzy/setup.bash

# Source workspace setup
USERNAME=${USERNAME:-ros}
if [ -f "/home/${USERNAME}/ros2_ws/install/setup.bash" ]; then
    source /home/${USERNAME}/ros2_ws/install/setup.bash
fi


ros2 launch nav2_bringup localization_launch.py   params_file:=/home/ros/ros2_ws/src/config/nav2_victor.yaml   map:=/home/ros/ros2_ws/src/maps/coro_victor.yaml &
ros2 launch nav2_bringup navigation_launch.py   params_file:=/home/ros/ros2_ws/src/config/nav2_navigation_victor.yaml map:=/home/ros/ros2_ws/src/maps/coro_victor.yaml
#ros2 launch nav2_bringup bringup_launch.py   params_file:=/home/ros/ros2_ws/src/config/nav2_test.yaml   map:=/home/ros/ros2_ws/src/maps/quarter_map.yaml

