//================================================ ADAPTIVE FILTER ========================================================
// Project: EspeleoRobô2
// Institution: UFMG & ITV
// Description: Common includes/defs for the adaptive_filter package (ROS 2 Jazzy).
// Original Date: 2021-12-29 — Ported to ROS 2 Jazzy.
// Member: Gilmar Pereira da Cruz Júnior  |  e-mail: gilmarpcruzjunior@gmail.com
//========================================================================================================================
#ifndef UTILITY_LIDAR_ODOMETRY_HPP_
#define UTILITY_LIDAR_ODOMETRY_HPP_

// ------------------------------- ROS 2 / rclcpp -------------------------------
#include <rclcpp/rclcpp.hpp>

// ------------------------------- Messages (ROS 2) -----------------------------
#include <sensor_msgs/msg/imu.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <std_msgs/msg/header.hpp>
#include <builtin_interfaces/msg/time.hpp>

// ------------------------------- TF2 (ROS 2) ---------------------------------
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Transform.h>
#include <tf2_ros/transform_broadcaster.h>
#include <tf2_ros/transform_listener.h>
#include <tf2_ros/buffer.h>

// ------------------------------- Eigen ---------------------------------------
#include <Eigen/Dense>
#include <Eigen/Geometry>

// ------------------------------- STL -----------------------------------------
#include <array>
#include <cmath>
#include <cstdint>
#include <deque>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <mutex>
#include <queue>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

namespace adaptive_filter {

// Prefer constexpr over macros in C++
inline constexpr double PI = 3.14159265358979323846;
inline constexpr double INF_D = std::numeric_limits<double>::infinity();

struct Bias {
  double x {};
  double y {};
  double z {};
};

} // namespace adaptive_filter

#endif // UTILITY_LIDAR_ODOMETRY_HPP_
