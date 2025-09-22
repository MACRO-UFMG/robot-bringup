FROM ros2_jazzy:latest

# Define USERNAME variable
ARG USERNAME=ros
ENV USERNAME=${USERNAME}

# Set working directory
WORKDIR /home/${USERNAME}/ros2_ws

# Install FASTLIO2 dependencies
RUN apt-get update && \
    apt-get install -y \
        # PCL and related packages
        libpcl-dev \
        ros-jazzy-pcl-* \
        # Eigen3
        libeigen3-dev \
        # Build tools
        python3-colcon-common-extensions \
        # Additional dependencies
        ros-jazzy-tf2-geometry-msgs \
        ros-jazzy-geometry-msgs \
        ros-jazzy-sensor-msgs \
        ros-jazzy-nav-msgs \
        ros-jazzy-std-msgs \
        ros-jazzy-visualization-msgs \
        # Livox dependencies
        ros-jazzy-livox-ros-driver2 \
    && rm -rf /var/lib/apt/lists/*

# Copy FAST_LIO_ROS2 sources into the ROS2 workspace
WORKDIR /home/${USERNAME}/ros2_ws/src
COPY ./src/FAST_LIO_ROS2 ./FAST_LIO_ROS2

# Install additional ROS2 dependencies
RUN rosdep update && \
    rosdep install --from-paths . --ignore-src -r -y

# Build FAST_LIO_ROS2 separately
RUN /bin/bash -c "cd /home/${USERNAME}/ros2_ws && \
    source /opt/ros/jazzy/setup.bash && \
    colcon build --packages-select FAST_LIO_ROS2 --cmake-args -DCMAKE_BUILD_TYPE=Release -Wno-dev"

# Build fast_lio package
RUN /bin/bash -c "cd /home/${USERNAME}/ros2_ws && \
    source /opt/ros/jazzy/setup.bash && \
    source install/setup.bash && \
    colcon build --packages-select fast_lio --cmake-args -DCMAKE_BUILD_TYPE=Release"

# Copy entrypoint
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# tini as entrypoint
ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]

# Default command
CMD ["/bin/bash"]