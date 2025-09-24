FROM livox_bringup:latest

# Define USERNAME variable
ARG USERNAME=ros
ENV USERNAME=${USERNAME}

# Set working directory
WORKDIR /home/${USERNAME}/ros2_ws

# Install additional FASTLIO2 dependencies
RUN apt-get update && \
    apt-get install -y \
        # Eigen3 for FastLIO
        libeigen3-dev \
        # Additional ROS2 packages for SLAM
        ros-jazzy-tf2-geometry-msgs \
        ros-jazzy-geometry-msgs \
        ros-jazzy-nav-msgs \
        ros-jazzy-visualization-msgs \
        ros-jazzy-rviz2 \
        # Build tools
        python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

# Copy FAST_LIO_ROS2 sources into the ROS2 workspace
WORKDIR /home/${USERNAME}/ros2_ws/src
COPY ./src/FAST_LIO_ROS2 ./FAST_LIO_ROS2

# Build FAST_LIO_ROS2 (depends on livox_ros_driver2)
RUN /bin/bash -c "cd /home/${USERNAME}/ros2_ws && \
    source /opt/ros/jazzy/setup.bash && \
    source install/setup.bash && \
    colcon build --packages-select FAST_LIO_ROS2 \
    --cmake-args \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS='-Wno-dev' \
    --no-warn-unused-cli"

# Build fast_lio package
RUN /bin/bash -c "cd /home/${USERNAME}/ros2_ws && \
    source /opt/ros/jazzy/setup.bash && \
    source install/setup.bash && \
    colcon build --packages-select fast_lio \
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