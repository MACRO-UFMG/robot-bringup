#!/bin/bash

# Launch script for Scout Mini + Intel RealSense ROS 2 Jazzy service on Jetson Orin
# This script sets up the environment and launches the scout-mini service with RealSense support

set -e  # Exit on any error

# Default values
ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-7}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --domain-id)
            ROS_DOMAIN_ID="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --domain-id ID        Set ROS_DOMAIN_ID (default: 0)"
            echo "  --help,-h             Show this help message"
            echo ""
            echo "Alternative: Use docker-compose directly:"
            echo "  ROS_DOMAIN_ID=5 docker-compose up scout-mini"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🚀 Launching Scout Mini + Intel RealSense ROS 2 Jazzy service on Jetson Orin..."

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found in current directory"
    echo "Please run this script from the directory containing docker-compose.yml"
    exit 1
fi

# Jetson Orin setup - no X11 forwarding needed for headless operation
echo "🔧 Setting up for Jetson Orin hardware access..."
echo "📡 Using ROS_DOMAIN_ID: $ROS_DOMAIN_ID"

# Launch the scout-mini service with additional volumes and hardware access
echo "🐳 Starting scout-mini container with Jetson Orin hardware access..."
echo "📦 Scout Mini + Intel RealSense packages are pre-built in the image"
docker run -it --rm \
    --name scout-mini-runtime \
    --runtime nvidia \
    --network host \
    --ipc host \
    --privileged \
    -e NVIDIA_VISIBLE_DEVICES=all \
    -e NVIDIA_DRIVER_CAPABILITIES=all \
    -e ROS_DOMAIN_ID=$ROS_DOMAIN_ID \
    -e ROS_LOCALHOST_ONLY=0 \
    -v $(pwd)/../scout_ws/src:/home/ros/ros2_ws/src:rw \
    -v /dev:/dev:rw \
    -v /dev/shm:/dev/shm \
    scout-mini-ros2:latest \
    /bin/bash

echo "✅ Container stopped."
echo ""
echo "💡 Tip: You can also use docker-compose for easier management:"
echo "   ROS_DOMAIN_ID=$ROS_DOMAIN_ID docker-compose up scout-mini" 