cmake_minimum_required(VERSION 3.8)
project(rtsp_cam)

# Default to C++17
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(image_transport REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(compressed_image_transport REQUIRED)
find_package(theora_image_transport REQUIRED)

# Install Python modules
ament_python_install_package(${PROJECT_NAME})

# Install Python executables (conditionally based on what exists)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/scripts/rtsp_streamer_node.py")
  install(PROGRAMS
    scripts/rtsp_streamer_node.py
    DESTINATION lib/${PROJECT_NAME}
  )
endif()

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/scripts/rtsp_publisher_node.py")
  install(PROGRAMS
    scripts/rtsp_publisher_node.py
    DESTINATION lib/${PROJECT_NAME}
  )
endif()

# Install launch files
install(DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
  FILES_MATCHING PATTERN "*.launch.py"
)

# Install config files
install(DIRECTORY config/
  DESTINATION share/${PROJECT_NAME}/config
  FILES_MATCHING PATTERN "*.json" PATTERN "*.yaml" PATTERN "*.rviz"
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()