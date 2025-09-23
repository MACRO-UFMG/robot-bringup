#!/bin/bash

# Source ROS 2 environment
source /opt/ros/jazzy/setup.bash

# Source workspace setup
if [ -f "/home/ros/ros2_ws/install/setup.bash" ]; then
    source /home/ros/ros2_ws/install/setup.bash
fi

exec ros2 run rosaria2 rosaria2_debug