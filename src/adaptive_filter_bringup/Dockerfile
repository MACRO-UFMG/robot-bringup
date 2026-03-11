# ---- Base image (adjust if your stack uses another base) ----
# Example: FROM ros:jazzy-ros-base
# Keep whatever base you already use in your bringup images.
FROM ros:jazzy-ros-base

ARG DEBIAN_FRONTEND=noninteractive
ARG USERNAME=ros

ENV USERNAME=${USERNAME}
ENV ROS_DISTRO=jazzy

# Use bash for RUN so "source" works naturally
SHELL ["/bin/bash", "-c"]

# ---- Create user + workspace skeleton (consistent with other bringups) ----
RUN apt-get update && apt-get install -y --no-install-recommends \
      sudo \
      tini \
      ca-certificates \
      python3 \
      python3-pip \
      python3-colcon-common-extensions \
      build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && mkdir -p /home/${USERNAME}/ros2_ws/src \
    && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}

# ---- Install adaptive_odom_filter runtime deps ----
RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-jazzy-rtabmap-msgs \
      ros-jazzy-imu-tools \
      ros-jazzy-tf2-geometry-msgs \
      ros-jazzy-geometry-msgs \
      ros-jazzy-nav-msgs \
      ros-jazzy-visualization-msgs \
      ros-jazzy-rviz2 \
    && rm -rf /var/lib/apt/lists/*

# ---- Copy sources ----
WORKDIR /home/${USERNAME}/ros2_ws/src
COPY ./src/adaptive_odom_filter ./adaptive_odom_filter

# ---- Build (as the user, but using sourced ROS env) ----
WORKDIR /home/${USERNAME}/ros2_ws
RUN chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/ros2_ws

USER ${USERNAME}
RUN source /opt/ros/${ROS_DISTRO}/setup.bash && \
    colcon build --packages-select adaptive_odom_filter \
      --cmake-args \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_CXX_FLAGS='-Wno-dev' \
      --no-warn-unused-cli

# ---- Entrypoint ----
USER root
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown ${USERNAME}:${USERNAME} /entrypoint.sh

ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]
CMD ["/bin/bash"]
