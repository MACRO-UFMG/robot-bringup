#!/bin/bash
set -e

# Source ROS 2
source /opt/ros/jazzy/setup.bash

# Source workspace
if [ -f "/home/ros/ros2_ws/install/setup.bash" ]; then
    source /home/ros/ros2_ws/install/setup.bash
fi

# Verificar se can0 já existe e está ativa
if ip link show can0 &> /dev/null; then
    
    # Tentar derrubar a interface existente primeiro
    sudo ip link set can0 down || true
    sudo ip link delete can0 || true
    
    # Pequena pausa para garantir que a interface foi removida
    sleep 1
fi

# Configurar nova interface CAN
sudo ip link set can0 up type can bitrate 500000

# Substitui o processo por ros2 launch
exec ros2 launch scout_base scout_mini_base.launch.py