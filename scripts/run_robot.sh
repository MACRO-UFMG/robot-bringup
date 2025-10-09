#!/bin/bash

CONFIG_FILE="../config/selected_profiles.conf"
IMAGE_NAME="ros2_jazzy"
ROS_DOCKERFILE_PATH="../docker/ros_jazzy/Dockerfile"
PROJECT_NAME="robot_bringup"

# Lista de profiles padrão (usada se o arquivo de config não existir ou estiver vazio)
DEFAULT_PROFILES="ros_base"

# Verifica se a imagem Docker já existe
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    echo "📦 Image $IMAGE_NAME not found. Building..."
    docker build -t "$IMAGE_NAME" -f "$ROS_DOCKERFILE_PATH" ../docker || {
        echo "❌ Failed to build image $IMAGE_NAME"
        exit 1
    }
else
    echo "✅ Image $IMAGE_NAME already exists."
fi

# Lê os profiles do arquivo de configuração, se existir e não estiver vazio
if [ -f "$CONFIG_FILE" ] && [ -s "$CONFIG_FILE" ]; then
    PROFILES=$(cat "$CONFIG_FILE" | tr -d '\r\n' | tr -s ' ')
    echo "📋 Using profiles from config file: $PROFILES"
else
    echo "⚠️  No valid config file found or it's empty. Using default profiles: $DEFAULT_PROFILES"
    PROFILES="$DEFAULT_PROFILES"
fi

# Converte os profiles para a sintaxe do Docker Compose
DOCKER_PROFILES=""
for p in $PROFILES; do
    DOCKER_PROFILES="$DOCKER_PROFILES --profile $p"
done

echo "🚀 Starting robot with profiles: $PROFILES"
docker compose -f ../docker/docker-compose.yml $DOCKER_PROFILES --project-name "$PROJECT_NAME" up --build