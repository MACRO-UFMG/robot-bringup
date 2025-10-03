#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from rclpy.qos import QoSProfile, ReliabilityPolicy

class TfPublisher(Node):
    def __init__(self):
        super().__init__('tf_publisher')

        self.broadcaster = TransformBroadcaster(self)

        self.odom_pub = self.create_publisher(Odometry, '/robot/odom', 10)
        
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.create_subscription(LaserScan, '/scan', self.scan_callback, qos)
        self.scan_pub = self.create_publisher(LaserScan, '/livox/scan', qos)

        self.create_subscription(Odometry, '/Odometry', self.odom_callback, 10)
        self.create_timer(0.05, self.publish_livox_tf)

    def odom_callback(self, msg: Odometry):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'fast_lio/odom'
        t.child_frame_id = 'fast_lio/base_link'
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        t.transform.rotation = msg.pose.pose.orientation
        self.broadcaster.sendTransform(t)

        msg.header.stamp = t.header.stamp
        self.odom_pub.publish(msg)

    def scan_callback(self, msg: LaserScan):
        msg.header.frame_id = 'livox_frame'
        msg.header.stamp = self.get_clock().now().to_msg()
        self.scan_pub.publish(msg)

    def publish_livox_tf(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'fast_lio/base_link'
        t.child_frame_id = 'livox_frame'
        t.transform.translation.x = 0.2
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.15
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0
        self.broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = TfPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
