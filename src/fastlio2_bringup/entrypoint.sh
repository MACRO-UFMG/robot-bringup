#!/bin/bash
set -e

# Inherit from livox_bringup entrypoint
# Configure library path (inherited from livox_bringup)
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Source ROS 2 environment
source /opt/ros/jazzy/setup.bash

# Source workspace setup
USERNAME=${USERNAME:-ros}
if [ -f "/home/${USERNAME}/ros2_ws/install/setup.bash" ]; then
    source /home/${USERNAME}/ros2_ws/install/setup.bash
fi

# Set default configuration file if not provided
CONFIG_FILE=${CONFIG_FILE:-"mid360_mod.yaml"}

echo "🚀 FastLIO2 SLAM Ready!"
echo "📋 Available config files:"
ls -la /home/${USERNAME}/ros2_ws/src/FAST_LIO_ROS2/config/ || echo "No config directory found"
echo ""
echo "🎯 Starting FastLIO2 SLAM with config: ${CONFIG_FILE}"
echo ""

# Launch FastLIO2 SLAM
ros2 launch fast_lio mapping.launch.py \
    config_file:=${CONFIG_FILE} \
    namespace:=$NAMESPACE
