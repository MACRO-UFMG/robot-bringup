FROM ros2_jazzy:latest

# Define USERNAME variable
ARG USERNAME=ros
ENV USERNAME=${USERNAME}

# Set working directory
WORKDIR /home/${USERNAME}/ros2_ws

# Install FASTLIO2 + Nav2 dependencies
RUN apt-get update && \
    apt-get install -y \
    ros-jazzy-slam-toolbox \
        # Nav2 core + bringup
        ros-jazzy-navigation2 \
        ros-jazzy-nav2-bringup \
        # PCL 
        ros-jazzy-pcl-conversions \
        ros-jazzy-pcl-msgs \
        # Build tools
        python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

# Copy FAST_LIO_ROS2 sources into the ROS2 workspace
WORKDIR /home/${USERNAME}/ros2_ws


RUN rosdep update && \
    rosdep install --from-paths . --ignore-src -r -y

COPY ./src/ ./src/

RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && colcon build --symlink-install"

# Copy entrypoint
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# tini as entrypoint
ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]

# Default command
CMD ["/bin/bash"]