#!/bin/bash 
set -e

# Inherit from fastlio2_bringup entrypoint
# Configure library path (inherited from livox_bringup)
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Source ROS 2 environment
source /opt/ros/jazzy/setup.bash

# Source workspace setup
USERNAME=${USERNAME:-ros}
if [ -f "/home/${USERNAME}/ros2_ws/install/setup.bash" ]; then
    source /home/${USERNAME}/ros2_ws/install/setup.bash
fi

# Parameters are set on config/.env


echo "🔄 PointCloud to LaserScan Converter Ready!"
echo "Namespace: $NAMESPACE"
echo "📡 Input cloud topic: ${INPUT_CLOUD_TOPIC}"
echo "📡 Output scan topic: ${OUTPUT_SCAN_TOPIC}"
echo "📏 Height range: [${MIN_HEIGHT}, ${MAX_HEIGHT}]"
echo "📏 Range: [${RANGE_MIN}, ${RANGE_MAX}]"
echo ""

# Launch pointcloud_to_laserscan node
# ros2 launch pointcloud_to_laserscan sample_pointcloud_to_laserscan_launch.py

exec ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node \
    --ros-args \
    -r cloud_in:=${INPUT_CLOUD_TOPIC} \
    -r scan:=${OUTPUT_SCAN_TOPIC} \
    -p min_height:=${MIN_HEIGHT} \
    -p max_height:=${MAX_HEIGHT} \
    -p range_min:=${RANGE_MIN} \
    -p range_max:=${RANGE_MAX}

