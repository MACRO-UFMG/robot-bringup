#!/bin/bash

# Scout Mini ROS 2 Jazzy entrypoint script for Jetson Orin

# Set Python to unbuffered mode
export PYTHONUNBUFFERED=1

# Source ROS2 setup
source /opt/ros/jazzy/setup.bash

# Source workspace setup if it exists (Scout Mini packages)
if [ -f "/home/ros/ros2_ws/install/setup.bash" ]; then
    echo "Sourcing Scout Mini workspace..."
    source /home/ros/ros2_ws/install/setup.bash
fi

# Set default ROS_DOMAIN_ID if not provided
export ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-0}
export ROS_LOCALHOST_ONLY=${ROS_LOCALHOST_ONLY:-0}

# Check and setup CAN interface if needed
echo "🔌 Checking CAN interface..."
if ! ip link show can0 &>/dev/null; then
    echo "📡 CAN interface not found, creating can0..."
    sudo ip link add dev can0 type can
fi

if ! ip link show can0 | grep -q "UP"; then
    echo "⚡ Setting up can0 interface..."
    sudo ip link set can0 up type can bitrate 500000
    echo "✅ CAN interface can0 configured and enabled"
else
    echo "✅ CAN interface can0 is already up"
fi

# Print environment info
echo "🤖 Scout Mini ROS 2 Jazzy Environment Ready!"
echo "📡 ROS_DOMAIN_ID: $ROS_DOMAIN_ID"
echo "🔗 ROS_LOCALHOST_ONLY: $ROS_LOCALHOST_ONLY"
echo "📁 Workspace: /home/ros/ros2_ws"
echo "🚗 Scout Mini robot packages ready"
echo "📸 Intel RealSense source available (build manually if needed)"
echo "🛠️  To build RealSense: colcon build --packages-select realsense2_camera"

# Execute the command passed to the container
exec "$@" 