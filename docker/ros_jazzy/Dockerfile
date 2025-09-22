FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    tini \
    curl \
    gnupg2 \
    lsb-release \
    software-properties-common \
    sudo \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Add ROS 2 apt repository
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Add Gazebo apt repository
RUN curl -sSL https://packages.osrfoundation.org/gazebo.gpg -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

# Install ROS 2 Jazzy and Gazebo Harmonic
RUN apt-get update && apt-get install -y \
    ros-jazzy-desktop-full \
    ros-jazzy-ros-gz \
    gz-harmonic \
    && rm -rf /var/lib/apt/lists/*

# Install development tools and dependencies for Scout Mini + RealSense
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3-colcon-common-extensions \
    python3-pip \
    python3-rosdep \
    python3-vcstool \
    python3-venv \
    libasio-dev \
    libserial-dev \
    dkms \
    python3-tqdm \
    python3-requests \
    ros-jazzy-joint-state-publisher \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-xacro \
    ros-jazzy-tf2-ros \
    ros-jazzy-tf2-geometry-msgs \
    ros-jazzy-geometry-msgs \
    ros-jazzy-sensor-msgs \
    ros-jazzy-nav-msgs \
    ros-jazzy-std-msgs \
    ros-jazzy-launch-testing-ament-cmake \
    # Intel RealSense dependencies
    libudev-dev \
    pkg-config \
    libgtk-3-dev \
    libusb-1.0-0-dev \
    libglfw3-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    ros-jazzy-cv-bridge \
    ros-jazzy-image-transport \
    ros-jazzy-tf2 \
    ros-jazzy-tf2-eigen \
    ros-jazzy-diagnostic-updater \
    ros-jazzy-angles \
    # Pre-built RealSense ROS packages
    ros-jazzy-librealsense2 \
    ros-jazzy-realsense2-camera \
    ros-jazzy-realsense2-camera-msgs \
    ros-jazzy-realsense2-description \
    # Additional RealSense dependencies
    libssl-dev \
    # Mocap OptiTrack dependencies
    libboost-all-dev \
    libxml2-dev \
    # MPI for PCL/VTK support
    libopenmpi-dev \
    # CAN interface tools
    iproute2 \
    can-utils \
    # ROS2 message generation dependencies
    ros-jazzy-rosidl-default-generators \
    ros-jazzy-rosidl-default-runtime \
    ros-jazzy-rosidl-runtime-cpp \
    ros-jazzy-rmw-fastrtps-cpp \
    ros-jazzy-fastrtps \
    # PCL dependencies for livox_ros_driver2
    ros-jazzy-pcl-conversions \
    libpcl-dev \
    # Additional dependencies
    ros-jazzy-ament-cmake-auto \
    # FAST_LIO_ROS2 dependencies
    libeigen3-dev \
    ros-jazzy-visualization-msgs \
    ros-jazzy-message-filters \
    # APR library for livox_ros_driver2
    libapr1-dev \
    && rm -rf /var/lib/apt/lists/*

# Install additional Python packages
RUN pip3 install transforms3d --break-system-packages

# Initialize rosdep
RUN rosdep init && rosdep update

# Set up environment variables
ENV ROS_DISTRO=jazzy
ENV GZ_VERSION=harmonic

# Create a non-root user (matching Jetson user coro)
ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=1000

# Create the user and group
RUN groupadd -f -g $USER_GID $USERNAME 2>/dev/null || true && \
    useradd -m -u $USER_UID -g $USER_GID -s /bin/bash $USERNAME 2>/dev/null || useradd -m -g $USER_GID -s /bin/bash $USERNAME && \
    echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

# Set up workspace and bashrc as root
RUN mkdir -p /home/$USERNAME/ros2_ws/src && \
    echo "source /opt/ros/jazzy/setup.bash" >> /home/$USERNAME/.bashrc && \
    echo "source /home/$USERNAME/ros2_ws/install/setup.bash" >> /home/$USERNAME/.bashrc && \
    echo "alias encan='echo \"coro\" | sudo -S ip link set can0 up type can bitrate 500000'" >> /home/$USERNAME/.bashrc && \
    chown -R $USERNAME:$USERNAME /home/$USERNAME
