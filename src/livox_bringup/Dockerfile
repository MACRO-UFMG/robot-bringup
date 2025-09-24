FROM ros2_jazzy:latest
    
# Install required ROS build tools
RUN apt-get update && apt-get install -y \
    ros-jazzy-ament-cmake \
    ros-jazzy-ament-cmake-auto \
    && rm -rf /var/lib/apt/lists/*

# Copy rosaria2 sources into the ROS2 workspace
WORKDIR /home/ros/ros2_ws/src
COPY ./src/livox_ros_driver2 ./livox_ros_driver2
COPY ./src/Livox-SDK2 ./Livox-SDK2

# Build Livox-SDK2
WORKDIR /home/ros/ros2_ws/src/Livox-SDK2/build
RUN cmake .. && \
    make -j$(nproc) && \
    make install

# Build workspace
WORKDIR /home/ros/ros2_ws
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && colcon build --symlink-install"

# Copy entrypoint
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./config_template.json /tmp/config_template.json

# Set entrypoint
ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]

# Default command
CMD ["/bin/bash"]
