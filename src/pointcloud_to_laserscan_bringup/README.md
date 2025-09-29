# PointCloud to LaserScan Bringup

This service converts 3D PointCloud2 messages to 2D LaserScan messages, useful for navigation and obstacle avoidance with systems that expect 2D laser scan data.

## Overview

The `pointcloud_to_laserscan_bringup` service provides a ROS2 node that subscribes to a PointCloud2 topic (typically from FastLIO2 or Livox) and publishes a LaserScan message. This is particularly useful when you want to use 3D LiDAR data with navigation stacks that expect 2D laser scans.

## Dependencies

This service builds on top of:
- `fastlio2_bringup` (which includes `livox_bringup`)
- ROS2 Jazzy
- sensor_msgs, laser_geometry, tf2 packages

## Configuration

The service can be configured through environment variables in the docker-compose.yml:

| Environment Variable | Default Value | Description |
|---------------------|---------------|-------------|
| `INPUT_CLOUD_TOPIC` | `/cloud_registered` | Input PointCloud2 topic (typically from FastLIO2) |
| `OUTPUT_SCAN_TOPIC` | `/scan` | Output LaserScan topic |
| `TARGET_FRAME` | (empty) | Target frame for transformation (optional) |
| `MIN_HEIGHT` | `-2.0` | Minimum height in meters to sample from the point cloud |
| `MAX_HEIGHT` | `2.0` | Maximum height in meters to sample from the point cloud |
| `ANGLE_MIN` | `-3.14159` | Minimum scan angle in radians (-π) |
| `ANGLE_MAX` | `3.14159` | Maximum scan angle in radians (π) |
| `ANGLE_INCREMENT` | `0.017453` | Angular resolution in radians (~1 degree) |
| `RANGE_MIN` | `0.1` | Minimum range in meters |
| `RANGE_MAX` | `100.0` | Maximum range in meters |

## Usage

### Build the service

```bash
docker compose build pointcloud_to_laserscan_bringup
```

### Run the service

```bash
docker compose --profile pointcloud_to_laserscan up pointcloud_to_laserscan_bringup
```

### Run with custom parameters

You can override the default parameters by setting environment variables:

```bash
INPUT_CLOUD_TOPIC=/livox/lidar OUTPUT_SCAN_TOPIC=/front_scan MIN_HEIGHT=-0.5 MAX_HEIGHT=1.0 \
docker compose --profile pointcloud_to_laserscan up pointcloud_to_laserscan_bringup
```

### Run with FastLIO2

To use this service with FastLIO2 for SLAM + navigation:

```bash
# Terminal 1: Start Livox driver
docker compose --profile livox up livox_bringup

# Terminal 2: Start FastLIO2 SLAM
docker compose --profile fastlio2 up fastlio2_bringup

# Terminal 3: Convert point cloud to laser scan
docker compose --profile pointcloud_to_laserscan up pointcloud_to_laserscan_bringup
```

### Interactive mode

To run in interactive mode for debugging or manual testing:

```bash
docker compose --profile pointcloud_to_laserscan run --rm pointcloud_to_laserscan_bringup /bin/bash
```

Once inside the container, you can manually run the node with custom parameters:

```bash
ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node \
    --ros-args \
    -r cloud_in:=/cloud_registered \
    -r scan:=/scan \
    -p min_height:=-1.0 \
    -p max_height:=1.0
```

## Topics

### Subscribed Topics
- `cloud_in` (default: `/cloud_registered`) - Input PointCloud2 message

### Published Topics
- `scan` (default: `/scan`) - Output LaserScan message

## Integration with Navigation Stack

This service is designed to work seamlessly with navigation stacks like Nav2. The output `/scan` topic can be directly consumed by:
- Costmap layers
- AMCL for localization
- Obstacle detection systems
- Any system expecting 2D laser scan data

## Source Repository

The pointcloud_to_laserscan package is from: [MACRO-UFMG/pointcloud_to_laserscan](https://github.com/MACRO-UFMG/pointcloud_to_laserscan/tree/652b2e4e6e835dd92e958ad00c21d38b3c64ece5)

## License

This package is licensed under the BSD-3-Clause license.
