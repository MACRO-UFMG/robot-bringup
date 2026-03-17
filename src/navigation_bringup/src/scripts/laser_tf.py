#!/usr/bin/env python3

import sys
import rclpy
from rclpy.executors import MultiThreadedExecutor
from launch_ros.substitutions import FindPackageShare
from rclpy.node import Node
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped

class StaticTFPublisher(Node):
    def __init__(self):
        super().__init__('body_to_laser')
        self.broadcaster = StaticTransformBroadcaster(self)

        # Defina a transformada
        static_transform = TransformStamped()

        static_transform.header.stamp = self.get_clock().now().to_msg()
        static_transform.header.frame_id = 'body'   # parent
        static_transform.child_frame_id = 'livox_frame'           # child

        static_transform.transform.translation.x = 0.0
        static_transform.transform.translation.y = 0.0
        static_transform.transform.translation.z = 0.0

        # yaw, pitch, roll = 0
        static_transform.transform.rotation.x = 0.0
        static_transform.transform.rotation.y = 0.0
        static_transform.transform.rotation.z = 0.0
        static_transform.transform.rotation.w = 1.0

        # Publica
        self.broadcaster.sendTransform(static_transform)
        self.get_logger().info('Publicado TF estático: body -> livox_frame')


def main(args=None):
    rclpy.init(args=args)
    node = StaticTFPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
