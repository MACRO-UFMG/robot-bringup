#!/bin/bash
set -e

# Inherit from livox_bringup entrypoint
# Configure library path (inherited from livox_bringup)
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Source ROS 2 environment
source /opt/ros/jazzy/setup.bash

# Source workspace setup
USERNAME=${USERNAME:-ros}
if [ -f "/home/${USERNAME}/ros2_ws/install/setup.bash" ]; then
    source /home/${USERNAME}/ros2_ws/install/setup.bash
fi

# Set default configuration file if not provided
CONFIG_FILE=${CONFIG_FILE:-"mid360.yaml"}

# Set python script path
PYTHON_SCRIPT_PATH="/home/${USERNAME}/ros2_ws/src/scripts/dynamic_livox_tf.py"

# Função para limpeza que será chamada ao sair
cleanup() {
    echo "🔌 Shutting down..."
    # Mata todos os processos filhos deste script
    kill -SIGINT $(jobs -p)
    wait
}

trap cleanup SIGINT SIGTERM

echo "🚀 FastLIO2 SLAM Ready!"
echo "📋 Available config files:"
ls -la /home/${USERNAME}/ros2_ws/src/FAST_LIO_ROS2/config/ || echo "No config directory found"
echo ""
echo "🎯 Starting FastLIO2 SLAM with config: ${CONFIG_FILE}"
echo ""
echo "🐍 Starting dynamic TF publisher from: ${PYTHON_SCRIPT_PATH}"
echo ""

# Launch FastLIO2 SLAM
ros2 launch fast_lio mapping.launch.py \
    config_file:=${CONFIG_FILE} \
    namespace:=$NAMESPACE &

# Executa o script Python em segundo plano
if [ -f "$PYTHON_SCRIPT_PATH" ]; then
    python3 "$PYTHON_SCRIPT_PATH" &
else
    echo "⚠️  Warning: Python script not found at ${PYTHON_SCRIPT_PATH}"
fi

# Espera por TODOS os processos em background terminarem.
# O script só continuará (e sairá) quando ambos os processos forem finalizados.
wait -n