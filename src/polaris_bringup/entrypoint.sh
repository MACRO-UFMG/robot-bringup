#!/bin/bash
set -e

# Source ROS 2 environment
source /opt/ros/jazzy/setup.bash

# Source workspace setup
if [ -f "/home/ros/ros2_ws/install/setup.bash" ]; then
    source /home/ros/ros2_ws/install/setup.bash
fi

# Mantém o container rodando
exec tail -f /dev/null