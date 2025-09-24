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
RUN cd /home/ros/ros2_ws/src/Livox-SDK2 && \
    rm -rf build && mkdir build && \
    cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install

# Build workspace
WORKDIR /home/ros/ros2_ws
# RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && colcon build --symlink-install"
# Setup livox_ros_driver2 for ROS2 Jazzy first
RUN /bin/bash -c "cd /home/ros/ros2_ws/src/livox_ros_driver2 && \
    rm -f package.xml && \
    ln -s package_ROS2.xml package.xml && \
    cp -rf launch_ROS2/ launch/"

# Build livox_ros_driver2_msgs first (custom messages only)
RUN /bin/bash -c "cd /home/ros/ros2_ws && \
    source /opt/ros/jazzy/setup.bash && \
    source install/setup.bash && \
    colcon build --packages-select livox_ros_driver2_msgs --cmake-args -DCMAKE_BUILD_TYPE=Release"

# Build livox_ros_driver2 (depends on livox_ros_driver2_msgs)
RUN /bin/bash -c "cd /home/ros/ros2_ws && \
    source /opt/ros/jazzy/setup.bash && \
    source install/setup.bash && \
    colcon build --packages-select livox_ros_driver2 --cmake-args -DROS_EDITION=ROS2 -DROS_DISTRO=jazzy -DCMAKE_BUILD_TYPE=Release"

# Copy entrypoint
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./config_template.json /tmp/config_template.json

# Set entrypoint
ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]

# Default command
CMD ["/bin/bash"]
