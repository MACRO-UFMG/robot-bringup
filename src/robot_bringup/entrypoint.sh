#!/bin/bash
set -e

# Source ROS 2
source /opt/ros/jazzy/setup.bash

# Source workspace (se existir)
if [ -f "/home/ros/ros2_ws/install/setup.bash" ]; then
    source /home/ros/ros2_ws/install/setup.bash
fi

# Verifica se a variável NAMESPACE está definida
if [ -z "$NAMESPACE" ]; then
    echo "Erro: variável de ambiente NAMESPACE não definida."
    exit 1
fi

# Roda os dois nós dentro do mesmo namespace
python3 /home/ros/ros2_ws/src/scripts/dynamic_livox_tf.py --ros-args -r __ns:=$NAMESPACE &
ros2 launch espeleo_control2 test_obstacle_detection.xml
# ros2 run espeleo_control2 feedback_linearization.py --ros-args -r __ns:=$NAMESPACE -p const_vel:=$CONST_VEL -p const_omega:=$CONST_OMEGA