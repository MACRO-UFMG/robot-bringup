#!/bin/bash
set -e

# Source ROS 2 environment
source /opt/ros/jazzy/setup.bash

# Source workspace setup
USERNAME=${USERNAME:-ros}
if [ -f "/home/${USERNAME}/ros2_ws/install/setup.bash" ]; then
    source /home/${USERNAME}/ros2_ws/install/setup.bash
fi

# Launch Nav2 mapping
#ros2 launch nav2_bringup slam_launch.py params_file:=/home/${USERNAME}/ros2_ws/src/nav2_params.yaml use_sim_time:=false
#ros2 launch nav2_bringup slam_launch.py params_file:=/home/${USERNAME}/ros2_ws/src/nav2_params.yaml use_sim_time:=false
 # params_file:=/home/ros/ros2_ws/src/scout-bringup/scout_bringup/config/nav2_test.yaml   map:=/home/ros/ros2_ws/src/maps/2d/quarter_map.yaml
 
# ros2 run slam_toolbox sync_slam_toolbox_node \
#   --ros-args \
#   -p odom_frame:=fast_lio/odom \
#   -p map_frame:=map \
#   -p base_frame:=fast_lio/base_link \
#   -p scan_topic:=livox/scan

ros2 launch nav2_bringup localization_launch.py   params_file:=/home/ros/ros2_ws/src/config/nav2_test.yaml   map:=/home/ros/ros2_ws/src/maps/quarter_map.yaml
# ros2 launch nav2_bringup bringup_launch.py   params_file:=/home/ros/ros2_ws/src/config/nav2_test.yaml   map:=/home/ros/ros2_ws/src/maps/quarter_map.yaml
# ros2 launch nav2_bringup navigation_launch.py   params_file:=/home/ros/ros2_ws/src/config/nav2_test.yaml