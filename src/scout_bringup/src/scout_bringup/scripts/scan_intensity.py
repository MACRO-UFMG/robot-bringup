#!/usr/bin/env python3
# filename: laserscan_add_intensity.py

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import copy

class IntensityAdder(Node):
    def __init__(self):
        super().__init__('scan_intensity_adder')

        # QoS best-effort to match typical sensor topics
        qos = rclpy.qos.QoSReliabilityPolicy.BEST_EFFORT
        profile = rclpy.qos.QoSProfile(depth=10,
                                       reliability=qos,
                                       durability=rclpy.qos.QoSDurabilityPolicy.VOLATILE)

        self.sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_cb,
            profile)

        self.pub = self.create_publisher(
            LaserScan,
            '/scan_with_intensity',
            profile)

    def scan_cb(self, msg: LaserScan):
        # deep-copy to avoid mutating the original message in the TF buffer
        new_msg = copy.deepcopy(msg)

        # Ensure intensities array matches ranges length
        n = len(new_msg.ranges)
        new_msg.intensities = [0.0] * n

        self.pub.publish(new_msg)

def main():
    rclpy.init()
    node = IntensityAdder()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
