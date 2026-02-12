#!/bin/bash
set -e

# Resolve paths relative to this script (works from anywhere)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

CONFIG_FILE="${REPO_ROOT}/config/selected_profiles.conf"
IMAGE_NAME="ros2_jazzy"
ROS_DOCKERFILE_PATH="${REPO_ROOT}/docker/ros_jazzy/Dockerfile"
DOCKER_CONTEXT_DIR="${REPO_ROOT}/docker"
COMPOSE_FILE="${REPO_ROOT}/docker/docker-compose.yml"
PROJECT_NAME="robot_bringup"

DEFAULT_PROFILES="ros_base"

# Build base image if missing
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
  echo "📦 Image $IMAGE_NAME not found. Building..."
  docker build -t "$IMAGE_NAME" -f "$ROS_DOCKERFILE_PATH" "$DOCKER_CONTEXT_DIR" || {
    echo "❌ Failed to build image $IMAGE_NAME"
    exit 1
  }
else
  echo "✅ Image $IMAGE_NAME already exists."
fi

# Read profiles
if [ -f "$CONFIG_FILE" ] && [ -s "$CONFIG_FILE" ]; then
  PROFILES="$(tr -d '\r\n' < "$CONFIG_FILE" | tr -s ' ')"
  echo "📋 Using profiles from config file: $PROFILES"
else
  echo "⚠️  No valid config file found or it's empty. Using default profiles: $DEFAULT_PROFILES"
  PROFILES="$DEFAULT_PROFILES"
fi

# Compose profile args
DOCKER_PROFILES=()
for p in $PROFILES; do
  DOCKER_PROFILES+=(--profile "$p")
done

echo "🚀 Starting robot with profiles: $PROFILES"
docker compose -f "$COMPOSE_FILE" "${DOCKER_PROFILES[@]}" --project-name "$PROJECT_NAME" up --build
