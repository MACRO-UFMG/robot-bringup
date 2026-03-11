# ROS Publisher - Ubuntu 24.04 with ROS 2 Jazzy
FROM ubuntu:24.04

ARG ROS_DISTRO=jazzy

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=${ROS_DISTRO}
ENV PYTHONUNBUFFERED=1

# Instalar dependências do sistema e ROS (camada pesada, raramente muda)
RUN apt-get update && apt-get install -y \
    curl gnupg2 lsb-release python3-pip software-properties-common \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null

RUN apt-get update && apt-get install -y \
    ros-jazzy-ros-base \
    ros-jazzy-rclpy \
    ros-jazzy-std-msgs \
    ros-jazzy-sensor-msgs \
    ros-jazzy-geometry-msgs \
    ros-jazzy-image-transport \
    ros-jazzy-cv-bridge \
    ros-jazzy-compressed-image-transport \
    ros-jazzy-theora-image-transport \
    ros-jazzy-image-view \
    ros-jazzy-tf2-ros \
    ros-jazzy-rviz2 \
    ros-jazzy-rqt \
    ros-jazzy-rqt-image-view \
    python3-rosdep \
    python3-opencv \
    python3-requests \
    python3-numpy \
    python3-colcon-common-extensions \
    x11-apps mesa-utils libgl1 \
    && rm -rf /var/lib/apt/lists/*

RUN rosdep init && rosdep update || echo "rosdep already initialized"

WORKDIR /colcon_ws
RUN mkdir -p src

COPY package.xml CMakeLists.txt /colcon_ws/src/rtsp_cam/

# 👉 Agora copie TODO o código
COPY scripts/ /colcon_ws/src/rtsp_cam/scripts/
COPY config/ /colcon_ws/src/rtsp_cam/config/
COPY launch/ /colcon_ws/src/rtsp_cam/launch/
COPY rtsp_cam/ /colcon_ws/src/rtsp_cam/rtsp_cam/
COPY ros_publisher/entrypoint.sh /colcon_ws/

RUN chmod +x /colcon_ws/entrypoint.sh

# 👉 Build do seu pacote (camada leve, rebuild rápido)
RUN cd /colcon_ws && \
    /bin/bash -c "source /opt/ros/jazzy/setup.bash && colcon build --packages-select rtsp_cam"

# Source setup
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
RUN echo "source /colcon_ws/install/setup.bash" >> ~/.bashrc

WORKDIR /colcon_ws
ENTRYPOINT ["/colcon_ws/entrypoint.sh"]
CMD ["ros2", "launch", "rtsp_cam", "rtsp_camera.launch.py"]