FROM ros2_jazzy:latest

# Set working directory
WORKDIR /home/ros/ros2_ws

# Instala pacotes do librealsense2
RUN apt-get update && \
    apt-get install -y ros-jazzy-librealsense2 ros-jazzy-librealsense2-* \
    && rm -rf /var/lib/apt/lists/*

# Build workspace ROS2
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && colcon build --symlink-install"

# Copia entrypoint
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# tini como entrypoint
ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]

# Default command
CMD ["/bin/bash"]
