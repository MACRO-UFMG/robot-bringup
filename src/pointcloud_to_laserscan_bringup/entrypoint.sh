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
INPUT_CLOUD_TOPIC=${INPUT_CLOUD_TOPIC:-"/cloud_registered"}
OUTPUT_SCAN_TOPIC=${OUTPUT_SCAN_TOPIC:-"/scan"}
TARGET_FRAME=${TARGET_FRAME:-""}
MIN_HEIGHT=${MIN_HEIGHT:-"-2.0"}
MAX_HEIGHT=${MAX_HEIGHT:-"2.0"}
ANGLE_MIN=${ANGLE_MIN:-"-3.14159"}
ANGLE_MAX=${ANGLE_MAX:-"3.14159"}
ANGLE_INCREMENT=${ANGLE_INCREMENT:-"0.017453"}
RANGE_MIN=${RANGE_MIN:-"0.1"}
RANGE_MAX=${RANGE_MAX:-"100.0"}

echo "🔄 PointCloud to LaserScan Converter Ready!"
echo "📡 Input cloud topic: ${INPUT_CLOUD_TOPIC}"
echo "📡 Output scan topic: ${OUTPUT_SCAN_TOPIC}"
echo "📏 Height range: [${MIN_HEIGHT}, ${MAX_HEIGHT}]"
echo "📐 Angle range: [${ANGLE_MIN}, ${ANGLE_MAX}]"
echo "📏 Range: [${RANGE_MIN}, ${RANGE_MAX}]"
echo ""

# Launch pointcloud_to_laserscan node
exec ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node \
    --ros-args \
    -r cloud_in:=${INPUT_CLOUD_TOPIC} \
    -r scan:=${OUTPUT_SCAN_TOPIC} \
    -p min_height:=${MIN_HEIGHT} \
    -p max_height:=${MAX_HEIGHT} \
    -p angle_min:=${ANGLE_MIN} \
    -p angle_max:=${ANGLE_MAX} \
    -p angle_increment:=${ANGLE_INCREMENT} \
    -p range_min:=${RANGE_MIN} \
    -p range_max:=${RANGE_MAX} \
    $([ -n "${TARGET_FRAME}" ] && echo "-p target_frame:=${TARGET_FRAME}" || echo "")
