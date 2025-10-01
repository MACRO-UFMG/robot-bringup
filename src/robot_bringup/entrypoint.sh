#!/bin/bash
set -e

# Source ROS 2
source /opt/ros/jazzy/setup.bash

# Source workspace (se existir)
if [ -f "/home/ros/ros2_ws/install/setup.bash" ]; then
    source /home/ros/ros2_ws/install/setup.bash
fi

exec ros2 launch tf_launcher static_tf.launch.py 