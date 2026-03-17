FROM ros2_jazzy:latest

ARG USERNAME=ros
ENV USERNAME=${USERNAME}

WORKDIR /home/${USERNAME}/ros2_ws

RUN apt-get update && apt-get install -y \
    ros-jazzy-ament-cmake \
    ros-jazzy-ament-cmake-auto \
    && rm -rf /var/lib/apt/lists/*

# Copia entrypoint
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN mkdir -p src
COPY ./src/ ./src/

RUN . /opt/ros/jazzy/setup.sh && \
    colcon build --symlink-install

# tini como entrypoint
ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]

# Default command
CMD ["/bin/bash"]