#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry

from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster


class FixedFramePublisher(Node):
    def __init__(self):
        super().__init__('fixed_frame_publisher')

        # 1) Static broadcaster for fixed frames
        self.static_broadcaster = StaticTransformBroadcaster(self)
        # 2) Dynamic broadcaster for odom → base_link
        self.tf_broadcaster = TransformBroadcaster(self)

        # 3) Subscribe to Odometry messages
    #    self.create_subscription(
    #        Odometry,
    #        'odom',               # topic name; adjust if yours is '/odom'
    #        self.odom_callback,
    #        10
    #    )

        # 4) Timer for publishing static transforms at 1 Hz
    #    self.timer = self.create_timer(1.0, self.publish_transforms)
        self.get_logger().info("Fixed frame & odom TF publisher started")

    def publish_transforms(self):
        """Publish the two fixed (static) transforms once per timer event."""
        transforms = []

        # Transform: base_footprint → base_link (10 cm up)
        #t1 = TransformStamped()
        #t1.header.stamp = self.get_clock().now().to_msg()
        #t1.header.frame_id = 'base_footprint'
        #t1.child_frame_id = 'base_link'
        #t1.transform.translation.x = 0.0
        #t1.transform.translation.y = 0.0
        #t1.transform.translation.z = 0.1
        #t1.transform.rotation.x = 0.0
        #t1.transform.rotation.y = 0.0
        #t1.transform.rotation.z = 0.0
        #t1.transform.rotation.w = 1.0
        #transforms.append(t1)

        # Transform: base_link → laser_link (20 cm forward, 15 cm up)
        t2 = TransformStamped()
        t2.header.stamp = self.get_clock().now().to_msg()
        t2.header.frame_id = 'body'
        t2.child_frame_id = 'livox_frame'
        t2.transform.translation.x = 0.2
        t2.transform.translation.y = 0.0
        t2.transform.translation.z = 0.15
        t2.transform.rotation.x = 0.0
        t2.transform.rotation.y = 0.0
        t2.transform.rotation.z = 0.0
        t2.transform.rotation.w = 1.0
        transforms.append(t2)

        # Send the static transforms
        self.static_broadcaster.sendTransform(transforms)

    #def odom_callback(self, msg: Odometry):
    #    """Receive odometry and broadcast odom → base_link."""
    #    t = TransformStamped()

        # Use the odom message's timestamp
    #    t.header.stamp = msg.header.stamp
    #    t.header.frame_id = 'odom'
    #    t.child_frame_id = 'base_link'

        # Position
    #    t.transform.translation.x = msg.pose.pose.position.x
    #    t.transform.translation.y = msg.pose.pose.position.y
    #   t.transform.translation.z = msg.pose.pose.position.z

        # Orientation (quaternion)
    #    t.transform.rotation = msg.pose.pose.orientation

        # Publish the dynamic transform
    #    self.tf_broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = FixedFramePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

