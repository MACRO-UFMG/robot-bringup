#!/bin/bash

# Source ROS 2 environment
source /opt/ros/jazzy/setup.bash

# Source workspace setup
USERNAME=${USERNAME:-ros}
if [ -f "/home/${USERNAME}/ros2_ws/install/setup.bash" ]; then
    source /home/${USERNAME}/ros2_ws/install/setup.bash
fi

# Set default configuration file if not provided
CONFIG_FILE=${CONFIG_FILE:-"avia.yaml"}

# Launch FASTLIO2 mapping
exec ros2 launch fast_lio mapping.launch.py config_file:=${CONFIG_FILE}