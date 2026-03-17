# FASTLIO2 Bringup

This module provides FAST-LIO2 (Fast Direct LiDAR-inertial Odometry) integration for the robot bringup system.

## Overview

FAST-LIO2 is a state-of-the-art LiDAR-inertial odometry algorithm that provides real-time accurate pose estimation using LiDAR and IMU data. This module uses the [MACRO-UFMG/FAST_LIO_ROS2](https://github.com/MACRO-UFMG/FAST_LIO_ROS2) repository as a submodule.

## Structure

```
fastlio2_bringup/
├── Dockerfile          # Docker configuration for FAST-LIO2
├── entrypoint.sh       # Container entry point script
├── README.md          # This file
└── src/
    └── FAST_LIO_ROS2/ # Git submodule containing FAST-LIO2 source code
```

## Features

- Real-time LiDAR-inertial odometry
- Support for multiple LiDAR types (Livox, Velodyne, Ouster)
- ARM-based platform support
- PCD map saving capabilities
- External IMU support

## Configuration

The module can be configured through environment variables:

- `CONFIG_FILE`: YAML configuration file for FAST-LIO2 (default: "avia.yaml")

Available configuration files in the FAST-LIO2 package:
- `avia.yaml`: For Livox Avia LiDAR
- `horizon.yaml`: For Livox Horizon LiDAR
- `mid360.yaml`: For Livox MID-360 LiDAR
- `velodyne.yaml`: For Velodyne LiDARs
- `ouster.yaml`: For Ouster LiDARs

## Usage

1. Select "fastlio2" in the Additional Packages section when running `create_stack.sh`
2. The module will automatically launch the FAST-LIO2 mapping node
3. Make sure your LiDAR and IMU are properly synchronized

## Submodule Management

To update the FAST-LIO2 submodule:

```bash
cd src/fastlio2_bringup/src/FAST_LIO_ROS2
git pull origin main
cd ../../../../
git add src/fastlio2_bringup/src/FAST_LIO_ROS2
git commit -m "Update FAST_LIO_ROS2 submodule"
```

## Dependencies

- ROS2 Jazzy
- PCL (Point Cloud Library)
- Eigen3
- Livox ROS Driver 2 (for Livox LiDARs)

## Topics

### Subscribed Topics
- `/livox/lidar` (livox_ros_driver2/msg/CustomMsg): LiDAR point cloud data
- `/imu/data` (sensor_msgs/msg/Imu): IMU data

### Published Topics
- `/cloud_registered` (sensor_msgs/msg/PointCloud2): Registered point cloud
- `/Odometry` (nav_msgs/msg/Odometry): Estimated odometry
- `/path` (nav_msgs/msg/Path): Estimated trajectory

## Important Notes

- Ensure LiDAR and IMU are properly synchronized
- The extrinsic parameters between LiDAR and IMU should be calibrated
- For best performance, use hardware time synchronization when possible
- The submodule is pinned to commit `e2ef910cc42861dd6e4e000e8d27e52c9796796f` for stability