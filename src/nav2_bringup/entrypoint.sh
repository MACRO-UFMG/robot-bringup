#!/bin/bash
set -e

# Source ROS 2 environment
source /opt/ros/jazzy/setup.bash

# Source workspace setup
USERNAME=${USERNAME:-ros}
if [ -f "/home/${USERNAME}/ros2_ws/install/setup.bash" ]; then
    source /home/${USERNAME}/ros2_ws/install/setup.bash
fi

# Launch FASTLIO2 mapping
ros2 launch nav2_bringup localization_launch.py   # params_file:=/home/ros/ros2_ws/src/scout-bringup/scout_bringup/config/nav2_test.yaml   map:=/home/ros/ros2_ws/src/maps/2d/quarter_map.yaml