FROM ros2_jazzy:latest

RUN apt-get update && apt-get install -y \
    doxygen \
    graphviz \
    && rm -rf /var/lib/apt/lists/*
    
# Set working dir for third-party libraries
WORKDIR /opt

# Copy AriaCoda sources (assume ./src/AriaCoda exists next to Dockerfile)
COPY ./src/AriaCoda ./aria
WORKDIR /opt/aria
RUN make -j$(nproc) && make install

# Copy rosaria2 sources into the ROS2 workspace
WORKDIR /home/ros/ros2_ws/src
COPY ./src/rosaria2 ./rosaria2

# Install required ROS build tools
RUN apt-get update && apt-get install -y \
    ros-jazzy-ament-cmake \
    ros-jazzy-ament-cmake-auto \
    && rm -rf /var/lib/apt/lists/*

# Build workspace
WORKDIR /home/ros/ros2_ws
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && colcon build --symlink-install"

# Copy entrypoint
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["/bin/bash"]
