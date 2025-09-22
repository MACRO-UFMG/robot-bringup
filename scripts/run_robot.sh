#!/bin/bash

CONFIG_FILE="../config/selected_profiles.conf"
IMAGE_NAME="ros2_jazzy"
ROS_DOCKERFILE_PATH="../docker/ros_jazzy/Dockerfile"   # Adjust if needed
PROJECT_NAME="robot_bringup"

# Check if the Docker image already exists
if ! docker image inspect $IMAGE_NAME >/dev/null 2>&1; then
    echo "📦 Image $IMAGE_NAME not found. Building..."
    docker build -t $IMAGE_NAME -f $ROS_DOCKERFILE_PATH ../docker || {
        echo "❌ Failed to build image $IMAGE_NAME"
        exit 1
    }
else
    echo "✅ Image $IMAGE_NAME already exists."
fi

# Check if the configuration file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration file not found! Please run create_config.sh first."
    exit 1
fi

# Read saved profiles
PROFILES=$(cat "$CONFIG_FILE")

# Convert profiles to Docker Compose syntax
DOCKER_PROFILES=""
for p in $PROFILES; do
    DOCKER_PROFILES="$DOCKER_PROFILES --profile $p"
done

echo "🚀 Starting robot with profiles: $PROFILES"
docker compose -f ../docker/docker-compose.yml $DOCKER_PROFILES --project-name $PROJECT_NAME up --build
