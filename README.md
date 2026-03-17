# Robot Bringup

A comprehensive ROS2-based robot bringup system for autonomous navigation and mapping using Livox LiDAR sensors.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Robot](#running-the-robot)
- [Available Services](#available-services)
- [Scripts](#scripts)
- [Deprecated Commands](#deprecated-commands)

## 🔧 Prerequisites

- **OS**: Ubuntu 22.04 or later
- **ROS2**: Jazzy distribution
- **Docker**: Latest version with Docker Compose
- **Hardware**: 
  - Livox MID360 LiDAR sensor
  - RealSense camera (optional)
  - Your robot (Scout / Pioneer / Espeleo)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd robot-bringup
```

### 2. Initialize Git Submodules

This project uses several git submodules for external dependencies:

```bash
# Download all submodules
git submodule update --init --recursive
```

**Submodules included:**
- `src/fastlio2_bringup/src/FAST_LIO_ROS2` - Fast LIO SLAM algorithm
- `src/livox_bringup/src/Livox-SDK2` - Livox LiDAR SDK
- `src/livox_bringup/src/livox_ros_driver2` - Livox ROS2 driver
- `src/pionner_bringup/src/AriaCoda` - Pioneer robot interface
- `src/pionner_bringup/src/rosaria2` - Pioneer ROS2 driver
- `src/scout_bringup/src/scout_ros2` - Scout ROS2 driver
- `src/scout_bringup/src/ugv_sdk` - Scout SDK and communication library
- `src/scout_bringup/src/scout-bringup` - Scout launch and configuration files


**Troubleshooting: Empty Submodule Folders**

When cloning the repository and running the submodule initialization command (`git submodule update --init --recursive`), you might encounter a situation where some package folders appear completely empty (containing only the `.git` file).

**How to solve**

#### 1. Identify and fix the "culprit" submodule
Check the terminal output from the `git submodule update` command. The last printed fatal error will indicate which submodule crashed the process. 

Usually, the fix involves entering the broken submodule folder, pulling a valid reference, and updating the main repository:

```bash
# Enter the broken submodule
cd src/path/to/broken_submodule

# Fetch the latest info and checkout the correct branch (e.g., main or master)
git fetch
git checkout main
git pull origin main

# Go back to the workspace root and update the reference in the parent repository
cd ~/robot-bringup
git add src/path/to/broken_submodule
git commit -m "fix: update submodule reference"
```
#### 2. Resume initialization

With the main error fixed, run the command again. It should now bypass the corrected package and populate the folders that were previously empty:
```bash

git submodule update --init --recursive
```
#### 3. Forcing restoration (If the folder remains empty)

If the main repository is already pointing to the correct commit (check with git submodule status), but the local folder is still empty due to a synchronization failure, you can force Git to physically restore the files:
```bash

# Enter the empty submodule folder
cd src/path/to/empty_package

# Fetch information from the remote
git fetch

# Force restoration to the specific branch or commit required by the parent repository
git reset --hard origin/master 
# or
git reset --hard <commit-hash>
```

After the reset --hard, the package files (such as CMakeLists.txt and package.xml) should appear in the folder.


### 3. Build Docker Images

```bash
cd docker
docker-compose build
```

## ⚙️ Configuration

### Environment Variables

Edit `config/.env` to configure your setup:

```bash
# ROS Configuration
ROS_DOMAIN_ID=11
ROS_IP=192.168.3.1
HOST_IP=192.168.3.1
ROS_HOSTNAME=192.168.3.1

# Livox LiDAR Configuration
LIVOX_LIDAR_IP=192.168.3.142

# ROS Discovery
ROS_AUTOMATIC_DISCOVERY_RANGE=SYSTEM_DEFAULT
```

**Important**: Update `LIVOX_LIDAR_IP` with your actual Livox sensor IP address.

## 🤖 Running the Robot

### Quick Start

```bash
cd docker

# Run Livox LiDAR driver with RViz
docker-compose --profile livox up

# Run your robot interface
docker-compose --profile pioneer / scout / espeleo up

# Run RealSense camera
docker-compose --profile realsense2 up

# Run FastLIO2 SLAM
docker-compose --profile fastlio2 up

# Run Nav2 navigation
docker-compose --profile nav2 up
```

### Individual Services

You can run individual services based on your needs:

```bash
# LiDAR only
docker-compose --profile livox up

# Robot control only  
docker-compose --profile pioneer / scout / espeleo up

# SLAM only
docker-compose --profile fastlio2 up

# Navigation only
docker-compose --profile nav2 up
```

## 🛠️ Available Services

| Service | Profile | Description |
|---------|---------|-------------|
| `livox_bringup` | `livox` | Livox MID360 LiDAR driver with RViz |
| `pionner_bringup` | `pionner` | Pioneer robot interface |
| `scout_bringup` | `scout` | Scout robot interface |
| `realsense2_camera_bringup` | `realsense2` | RealSense camera driver |
| `fastlio2_bringup` | `fastlio2` | FastLIO2 SLAM algorithm |
| `nav2_bringup` | `nav2` | Nav2 navigation stack |

## 📜 Scripts

### Helper Scripts

```bash
# Create ROS2 workspace stack
./scripts/create_stack.sh

# Run robot with all services
./scripts/run_robot.sh
```

### Manual ROS2 Commands

If you prefer to run commands manually inside containers:

```bash
# Enter Livox container
docker exec -it <livox_container> bash
ros2 launch livox_ros_driver2 rviz_MID360_launch.py

# Enter Pioneer container  
docker exec -it <your_robot_container> bash
ros2 launch <package> <your_launch>.launch.py

# Enter FastLIO container
docker exec -it <fastlio_container> bash
ros2 launch fast_lio mapping.launch.py
```

## 🔄 Development

### Rebuilding Services

```bash
# Rebuild specific service
docker-compose build livox_bringup

# Rebuild all services
docker-compose build
```

### Debugging

```bash
# Run in interactive mode
docker-compose --profile livox run livox_bringup bash

# View logs
docker-compose --profile livox logs -f
```

## 📚 Deprecated Commands

The following commands are from the legacy scout-mini system and are kept for reference:

```bash
# Legacy scout-mini commands (deprecated)
ros2 launch scout_bringup start_scout.launch.py 

python3 scout_ws/src/scout-mini/scout-bringup/scout_bringup/scripts/dynamic_livox_tf.py 

python3 scout_ws/src/scout-mini/scout-bringup/scout_bringup/scripts/pcl2_cmsg.py

ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node

python3 scout_ws/src/scout-mini/scout-bringup/scout_bringup/scripts/scan_intensity.py 

ros2 launch fast_lio mapping.launch.py

ros2 launch slam_toolbox online_async_launch.py use_sim_time:=false params_file:=$HOME/scout_ws/src/scout-mini/scout-bringup/scout_bringup/config/slam_toolbox.yaml

rosrun nav2_map_server map_saver_cli -f ~/maps/coro --ros-args -p map_subscribe_transient:=true

ros2 launch nav2_bringup bringup_launch.py params_file:=$HOME/scout_ws/src/scout-mini/scout-bringup/scout_bringup/config/nav2.yaml map:=$HOME/maps/coro.yaml

ros2 launch nav2_bringup localization_launch.py params_file:=$HOME/scout_ws/src/scout-mini/scout-bringup/scout_bringup/config/nav2_skymu.yaml map:=$HOME/maps/coro.yaml
```

## 📞 Support

For issues and questions, please refer to the project documentation or contact the development team.

---

**Note**: This system is designed for Petrobras OP-1319 project requirements and may need adjustments for different hardware configurations.
