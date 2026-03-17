#!/usr/bin/env python3
# file: multi_fake_odom_imu_rates.py

import threading
from typing import List

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Point, Quaternion


def diag6(vx, vy, vz, vroll, vpitch, vyaw) -> List[float]:
    cov = [0.0] * 36
    cov[0] = vx      # x
    cov[7] = vy      # y
    cov[14] = vz     # z
    cov[21] = vroll  # roll
    cov[28] = vpitch # pitch
    cov[35] = vyaw   # yaw
    return cov


def diag3(a, b, c) -> List[float]:
    cov = [0.0] * 9
    cov[0] = a
    cov[4] = b
    cov[8] = c
    return cov


class MultiFakeSources(Node):
    def __init__(self):
        super().__init__('multi_fake_odom_imu_rates')

        # ---------- Params (ROS 2: declare, then read) ----------
        # Path/state evolution (1 step per "state_update_hz")
        self.declare_parameter('num_points', 60)
        self.declare_parameter('dx', 1.0)  # +1 m each second
        self.declare_parameter('start', [0.0, 0.0, 0.0])
        self.declare_parameter('state_update_hz', 1.0)  # leave at 1.0 to match +1 m/s

        # Frames & topics
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('imu_frame', 'imu_link')

        self.declare_parameter('camera_odom_topic', '/camera/odom')  # visual odom
        self.declare_parameter('wheel_odom_topic', '/wheel/odom')
        self.declare_parameter('lidar_odom_topic', '/lidar/odom')
        self.declare_parameter('imu_topic', '/imu/data')

        # Requested publication rates
        self.declare_parameter('camera_rate_hz', 10.0)  # visual
        self.declare_parameter('wheel_rate_hz', 20.0)
        self.declare_parameter('lidar_rate_hz', 10.0)
        self.declare_parameter('imu_rate_hz', 200.0)

        # Covariances
        self.declare_parameter('pose_var_xyz', 0.01)   # m^2
        self.declare_parameter('pose_var_rpy', 0.10)   # rad^2
        self.declare_parameter('twist_var_xyz', 0.10)  # (m/s)^2
        self.declare_parameter('twist_var_rpy', 0.20)  # (rad/s)^2

        self.declare_parameter('imu_var_orient', 0.05)
        self.declare_parameter('imu_var_gyro', 0.01)
        self.declare_parameter('imu_var_accel', 0.10)

        # Read parameters
        gp = lambda n: self.get_parameter(n).value
        self.num_points = int(gp('num_points'))
        self.dx_per_step = float(gp('dx'))
        self.start_xyz = list(gp('start'))
        self.update_hz = float(gp('state_update_hz'))

        self.odom_frame = str(gp('odom_frame'))
        self.base_frame = str(gp('base_frame'))
        self.imu_frame = str(gp('imu_frame'))

        self.cam_topic = str(gp('camera_odom_topic'))
        self.wheel_topic = str(gp('wheel_odom_topic'))
        self.lidar_topic = str(gp('lidar_odom_topic'))
        self.imu_topic = str(gp('imu_topic'))

        self.cam_rate_hz = float(gp('camera_rate_hz'))
        self.wheel_rate_hz = float(gp('wheel_rate_hz'))
        self.lidar_rate_hz = float(gp('lidar_rate_hz'))
        self.imu_rate_hz = float(gp('imu_rate_hz'))

        pose_var_xyz = float(gp('pose_var_xyz'))
        pose_var_rpy = float(gp('pose_var_rpy'))
        twist_var_xyz = float(gp('twist_var_xyz'))
        twist_var_rpy = float(gp('twist_var_rpy'))

        self.pose_cov = diag6(pose_var_xyz, pose_var_xyz, pose_var_xyz,
                              pose_var_rpy, pose_var_rpy, pose_var_rpy)
        self.twist_cov = diag6(twist_var_xyz, twist_var_xyz, twist_var_xyz,
                               twist_var_rpy, twist_var_rpy, twist_var_rpy)

        self.imu_orient_var = float(gp('imu_var_orient'))
        self.imu_gyro_var   = float(gp('imu_var_gyro'))
        self.imu_accel_var  = float(gp('imu_var_accel'))

        # Build guide points (+dx per step)
        self.points = [
            Point(x=self.start_xyz[0] + i * self.dx_per_step,
                  y=self.start_xyz[1],
                  z=self.start_xyz[2])
            for i in range(self.num_points)
        ]
        self.i = 0
        self.lock = threading.Lock()

        # Constant orientation and nominal velocity (matching +dx/s)
        self.q_identity = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        self.v = self.dx_per_step * self.update_hz  # with 1 Hz & dx=1 → 1 m/s

        # Publishers (depth=queue size)
        self.cam_pub   = self.create_publisher(Odometry, self.cam_topic, 1)
        self.wheel_pub = self.create_publisher(Odometry, self.wheel_topic, 1)
        self.lidar_pub = self.create_publisher(Odometry, self.lidar_topic, 1)
        self.imu_pub   = self.create_publisher(Imu,      self.imu_topic, 10)

        # Timers: one that advances state; others publish at their own rates
        # (ROS 2 timers do NOT pass an event arg)
        self.create_timer(1.0 / self.update_hz, self._tick_state)
        self.create_timer(1.0 / self.cam_rate_hz,   self._pub_camera)
        self.create_timer(1.0 / self.wheel_rate_hz, self._pub_wheel)
        self.create_timer(1.0 / self.lidar_rate_hz, self._pub_lidar)
        self.create_timer(1.0 / self.imu_rate_hz,   self._pub_imu)

        self.get_logger().info(
            f"multi_fake_odom_imu_rates started: cam {self.cam_rate_hz} Hz, "
            f"wheel {self.wheel_rate_hz} Hz, lidar {self.lidar_rate_hz} Hz, imu {self.imu_rate_hz} Hz"
        )

    # ---- State evolution: +1 index per tick ----
    def _tick_state(self):
        with self.lock:
            self.i = (self.i + 1) % len(self.points)

    # ---- Compose Odometry/IMU messages from current state ----
    def _make_odom(self) -> Odometry:
        with self.lock:
            pt = self.points[self.i]
        now = self.get_clock().now().to_msg()

        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame

        odom.pose.pose.position = pt
        odom.pose.pose.orientation = self.q_identity
        odom.pose.covariance = self.pose_cov

        odom.twist.twist.linear.x = self.v
        odom.twist.twist.linear.y = 0.0
        odom.twist.twist.linear.z = 0.0
        odom.twist.twist.angular.x = 0.0
        odom.twist.twist.angular.y = 0.0
        odom.twist.twist.angular.z = 0.0
        odom.twist.covariance = self.twist_cov
        return odom

    def _make_imu(self) -> Imu:
        now = self.get_clock().now().to_msg()
        imu = Imu()
        imu.header.stamp = now
        imu.header.frame_id = self.imu_frame

        imu.orientation = self.q_identity
        imu.angular_velocity.x = 0.0
        imu.angular_velocity.y = 0.0
        imu.angular_velocity.z = 0.0
        imu.linear_acceleration.x = 0.0
        imu.linear_acceleration.y = 0.0
        imu.linear_acceleration.z = 0.0

        imu.orientation_covariance = diag3(self.imu_orient_var,
                                           self.imu_orient_var,
                                           self.imu_orient_var)
        imu.angular_velocity_covariance = diag3(self.imu_gyro_var,
                                                self.imu_gyro_var,
                                                self.imu_gyro_var)
        imu.linear_acceleration_covariance = diag3(self.imu_accel_var,
                                                   self.imu_accel_var,
                                                   self.imu_accel_var)
        return imu

    # ---- Publisher callbacks at requested rates ----
    def _pub_camera(self):
        self.cam_pub.publish(self._make_odom())

    def _pub_wheel(self):
        self.wheel_pub.publish(self._make_odom())

    def _pub_lidar(self):
        self.lidar_pub.publish(self._make_odom())

    def _pub_imu(self):
        self.imu_pub.publish(self._make_imu())


def main(args=None):
    rclpy.init(args=args)
    node = MultiFakeSources()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
