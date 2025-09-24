FROM ros2_jazzy:latest
    
# Install required ROS build tools and system dependencies
RUN apt-get update && apt-get install -y \
    ros-jazzy-ament-cmake \
    ros-jazzy-ament-cmake-auto \
    libapr1-dev \
    libopenmpi-dev \
    libpcl-dev \
    libboost-all-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy rosaria2 sources into the ROS2 workspace
WORKDIR /home/ros/ros2_ws/src
COPY ./src/livox_ros_driver2 ./livox_ros_driver2
COPY ./src/Livox-SDK2 ./Livox-SDK2

# Build Livox-SDK2
WORKDIR /home/ros/ros2_ws/src/Livox-SDK2
RUN rm -rf build && mkdir build && \
    cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install && \
    ldconfig

# Build workspace
WORKDIR /home/ros/ros2_ws


# Verify Livox SDK installation and build livox_ros_driver2
RUN ls -la /usr/local/lib/liblivox_lidar_sdk* && \
    /bin/bash -c "cd /home/ros/ros2_ws && \
    source /opt/ros/jazzy/setup.bash && \
    export LD_LIBRARY_PATH=/usr/local/lib:\$LD_LIBRARY_PATH && \
    colcon build --packages-select livox_ros_driver2 \
    --cmake-args \
    -DROS_EDITION=ROS2 \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS='-Wno-dev' \
    --no-warn-unused-cli"

# Copy entrypoint
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./config_template.json /tmp/config_template.json

# Create a script to copy the generated config to the expected location
RUN echo '#!/bin/bash\n\
# Copy generated config to the location expected by the launch files\n\
if [ -f "/home/ros/ros2_ws/src/livox_ros_driver2/config/MID360_config.json" ]; then\n\
    cp "/home/ros/ros2_ws/src/livox_ros_driver2/config/MID360_config.json" "/home/ros/ros2_ws/install/livox_ros_driver2/share/livox_ros_driver2/config/MID360_config.json"\n\
    echo "✅ Config file copied to install directory"\n\
else\n\
    echo "❌ Generated config file not found!"\n\
fi\n\
exec "$@"' > /copy_config.sh && chmod +x /copy_config.sh

# Set entrypoint
ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]

# Default command
CMD ["/bin/bash"]
