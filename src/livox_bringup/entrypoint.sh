#!/bin/bash
# src/livox_bringup/entrypoint.sh

set -e

# Caminhos
TEMPLATE="/tmp/config_template.json"
OUTPUT="/home/ros/ros2_ws/src/livox_ros_driver2/config/MID360_config.json"

# Verifica variáveis
if [ -z "$LIVOX_LIDAR_IP" ] || [ -z "$HOST_IP" ]; then
  echo "ERRO: LIVOX_LIDAR_IP e HOST_IP devem estar definidos!"
  echo "LIVOX_LIDAR_IP = $LIVOX_LIDAR_IP"
  echo "HOST_IP = $HOST_IP"
  exit 1
fi

# Copia template para dentro do container (já copiado pelo Dockerfile)
cp "$TEMPLATE" "$OUTPUT"

# Substitui placeholders
sed -i "s/HOST_IP_PLACEHOLDER/$HOST_IP/g" "$OUTPUT"
sed -i "s/LIDAR_IP_PLACEHOLDER/$LIVOX_LIDAR_IP/g" "$OUTPUT"

echo "✅ Arquivo de configuração gerado em $OUTPUT:"
# cat "$OUTPUT"

# Source ROS
source /opt/ros/jazzy/setup.bash
source /home/ros/ros2_ws/install/setup.bash

# Executa o comando passado (ex: /bin/bash)
exec "$@"