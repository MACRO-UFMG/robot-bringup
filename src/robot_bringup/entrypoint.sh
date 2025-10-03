#!/bin/bash
set -e

# Source ROS 2
source /opt/ros/jazzy/setup.bash

# Source workspace (se existir)
if [ -f "/home/ros/ros2_ws/install/setup.bash" ]; then
    source /home/ros/ros2_ws/install/setup.bash
fi

# Executa o launcher em segundo plano
ros2 launch tf_launcher static_tf.launch.py &

# Executa o script Python em segundo plano
python3 /home/ros/ros2_ws/src/scripts/dynamic_livox_tf.py &

# Aguarda todos os processos em segundo plano terminarem
wait