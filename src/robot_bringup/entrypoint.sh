#!/bin/bash
set -e

# Source ROS 2
source /opt/ros/jazzy/setup.bash

# Source workspace (se existir)
if [ -f "/home/ros/ros2_ws/install/setup.bash" ]; then
    source /home/ros/ros2_ws/install/setup.bash
fi

python3 /home/ros/ros2_ws/src/scripts/dynamic_livox_tf.py --ros-args -r __ns:=$NAMESPACE 
