#!/bin/bash
set -e

echo "=== ROS 2 Publisher Starting ==="

# Source ROS 2 environment and workspace
source /opt/ros/jazzy/setup.bash
source /colcon_ws/install/setup.bash

# Check ROS 2 environment
echo "ROS_DISTRO: ${ROS_DISTRO}"
echo "ROS_DOMAIN_ID: ${ROS_DOMAIN_ID:-0}"
echo "AMENT_PREFIX_PATH: ${AMENT_PREFIX_PATH}"

# Set working directory to colcon workspace
cd /colcon_ws

# Execute main command
exec "$@"
