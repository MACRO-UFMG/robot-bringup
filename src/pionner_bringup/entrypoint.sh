#!/bin/bash

# Source ROS 2 environment
source /opt/ros/jazzy/setup.bash

# Source workspace setup
if [ -f "/home/ros/ros2_ws/install/setup.bash" ]; then
    source /home/ros/ros2_ws/install/setup.bash
fi

exec /home/ros/ros2_ws/install/rosaria2/lib/rosaria2/rosaria2_debug 