FROM fastlio2_bringup:latest

# Define USERNAME variable
ARG USERNAME=ros
ENV USERNAME=${USERNAME}

# Set working directory
WORKDIR /home/${USERNAME}/ros2_ws

# Install additional pointcloud_to_laserscan dependencies
RUN apt-get update && \
    apt-get install -y \
        # ROS2 packages for pointcloud to laserscan conversion
        ros-jazzy-sensor-msgs \
        ros-jazzy-laser-geometry \
        ros-jazzy-tf2 \
        ros-jazzy-tf2-ros \
        ros-jazzy-tf2-sensor-msgs \
        # Build tools
        python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

# Copy pointcloud_to_laserscan sources into the ROS2 workspace
WORKDIR /home/${USERNAME}/ros2_ws/src
COPY ./src/pointcloud_to_laserscan ./pointcloud_to_laserscan

# Build pointcloud_to_laserscan package
RUN /bin/bash -c "cd /home/${USERNAME}/ros2_ws && \
    source /opt/ros/jazzy/setup.bash && \
    source install/setup.bash && \
    colcon build --packages-select pointcloud_to_laserscan \
    --cmake-args \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS='-Wno-dev' \
    --no-warn-unused-cli"

# Copy entrypoint
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# tini as entrypoint
ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]

# Default command
CMD ["/bin/bash"]
