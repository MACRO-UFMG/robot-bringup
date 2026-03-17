cmake_minimum_required(VERSION 3.8)
project(adaptive_odom_filter)

# Compiler flags
set(CMAKE_CXX_STANDARD 17)
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic -O3)
endif()

# -------------------- Dependencies --------------------
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(rtabmap_msgs REQUIRED)
find_package(Eigen3 REQUIRED)

# -------------------- Include dirs --------------------
# Put headers under: include/adaptive_odom_filter/...
# e.g., include/adaptive_odom_filter/ekf_adaptive_tools.h
include_directories(
  include
  ${EIGEN3_INCLUDE_DIRS}
)

# -------------------- Library (tools) --------------------
add_library(adaptive_odom_filter SHARED
  src/ekf_adaptive_tools.cpp
)

ament_target_dependencies(adaptive_odom_filter
  rclcpp nav_msgs sensor_msgs std_msgs geometry_msgs
  tf2 tf2_ros tf2_geometry_msgs rtabmap_msgs
)

target_include_directories(adaptive_odom_filter PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

# -------------------- Executables --------------------
# 1) Keep ROS1-style name for backwards compatibility
add_executable(EKFAdaptiveFilter
  src/EKFAdaptiveFilter.cpp
)
target_link_libraries(EKFAdaptiveFilter adaptive_odom_filter)
ament_target_dependencies(EKFAdaptiveFilter
  rclcpp nav_msgs sensor_msgs std_msgs geometry_msgs
  tf2 tf2_ros tf2_geometry_msgs rtabmap_msgs
)

# 2) Optional alias executable (matches the launch I gave earlier)
add_executable(adaptive_odom_filter_node
  src/EKFAdaptiveFilter.cpp
)
target_link_libraries(adaptive_odom_filter_node adaptive_odom_filter)
ament_target_dependencies(adaptive_odom_filter_node
  rclcpp nav_msgs sensor_msgs std_msgs geometry_msgs
  tf2 tf2_ros tf2_geometry_msgs rtabmap_msgs
)

# -------------------- Python script (installed as a runtime) --------------------
# Ensure scripts/multi_fake_odom_imu_rates.py is executable (chmod +x) and has a shebang
install(PROGRAMS
  scripts/fake_odometry_path.py
  DESTINATION lib/${PROJECT_NAME}
)

# -------------------- Install headers / launch / config --------------------
install(DIRECTORY include/
  DESTINATION include
)

install(TARGETS
  adaptive_odom_filter
  EKFAdaptiveFilter
  adaptive_odom_filter_node
  EXPORT export_${PROJECT_NAME}
  RUNTIME DESTINATION lib/${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)
install(DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

# -------------------- ament exports --------------------
ament_export_targets(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)
ament_export_dependencies(
  rclcpp nav_msgs sensor_msgs std_msgs geometry_msgs
  tf2 tf2_ros tf2_geometry_msgs rtabmap_msgs
)
ament_export_include_directories(include)

ament_package()
