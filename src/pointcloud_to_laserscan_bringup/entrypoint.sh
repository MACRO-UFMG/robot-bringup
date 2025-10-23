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

# Set default parameters
# Set topic names based on namespace
if [ "$NAMESPACE" = "/" ]; then
    INPUT_CLOUD_TOPIC="livox/lidar"
    OUTPUT_SCAN_TOPIC="scan"
else
    INPUT_CLOUD_TOPIC="${NAMESPACE}/livox/lidar"
    OUTPUT_SCAN_TOPIC="${NAMESPACE}/scan"
fi
MIN_HEIGHT=${MIN_HEIGHT:-"-0.3"}
MAX_HEIGHT=${MAX_HEIGHT:-"0.1"}
RANGE_MIN=${RANGE_MIN:-"0.3"}
RANGE_MAX=${RANGE_MAX:-"100.0"}

echo "🔄 PointCloud to LaserScan Converter Ready!"
echo "Namespace: $NAMESPACE"
echo "📡 Input cloud topic: ${INPUT_CLOUD_TOPIC}"
echo "📡 Output scan topic: ${OUTPUT_SCAN_TOPIC}"
echo "📏 Height range: [${MIN_HEIGHT}, ${MAX_HEIGHT}]"
echo "📏 Range: [${RANGE_MIN}, ${RANGE_MAX}]"
echo ""

# Launch pointcloud_to_laserscan node
exec ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node \
    --ros-args \
    -r cloud_in:=${INPUT_CLOUD_TOPIC} \
    -r scan:=${OUTPUT_SCAN_TOPIC} \
    -p min_height:=${MIN_HEIGHT} \
    -p max_height:=${MAX_HEIGHT} \
    -p range_min:=${RANGE_MIN} \
    -p range_max:=${RANGE_MAX}

