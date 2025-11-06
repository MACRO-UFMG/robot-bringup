FROM ros2_jazzy:latest

# Instala dependências de documentação e build
RUN apt-get update && apt-get install -y \
    doxygen \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Cria workspace ROS2
WORKDIR /home/ros/ros2_ws/src

# Copia os pacotes ROS2
COPY ./src/polaris_navigation ./polaris_navigation

# Build workspace ROS2
WORKDIR /home/ros/ros2_ws
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && colcon build"

# Copia entrypoint
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]

# Default command
CMD ["/bin/bash"]
