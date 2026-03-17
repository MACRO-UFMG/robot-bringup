FROM ros2_jazzy:latest

# Instala dependências de documentação e build
RUN apt-get update && apt-get install -y \
    doxygen \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Cria workspace ROS2
WORKDIR /home/ros/ros2_ws/src

# Copia os pacotes ROS2
COPY ./src/ugv_sdk ./ugv_sdk
COPY ./src/scout_ros2 ./scout_ros2
COPY ./src/scout-bringup/scout_bringup ./scout_bringup

# Build ugv_sdk as a ROS 2 package first
RUN /bin/bash -c "cd /home/ros/ros2_ws && \
    source /opt/ros/jazzy/setup.bash && \
    colcon build --packages-select ugv_sdk --cmake-args -DCMAKE_BUILD_TYPE=Release"

# Build Scout packages 
RUN /bin/bash -c "cd /home/ros/ros2_ws && \
    source /opt/ros/jazzy/setup.bash && \
    source install/setup.bash && \
    colcon build --packages-select scout_msgs scout_description scout_bringup --cmake-args -DCMAKE_BUILD_TYPE=Release"

RUN /bin/bash -c "cd /home/ros/ros2_ws && \
    source /opt/ros/jazzy/setup.bash && \
    source install/setup.bash && \
    colcon build --packages-select scout_base --cmake-args -DCMAKE_BUILD_TYPE=Release "

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
