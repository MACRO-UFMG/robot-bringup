#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry

from tf2_ros import TransformBroadcaster


class TfPublisher(Node):
    def __init__(self):
        super().__init__('tf_publisher')

        # broadcaster para todos os transforms
        self.broadcaster = TransformBroadcaster(self)

        # publisher de odometria re-publicada (opcional para Nav2)
        self.odom_publisher = self.create_publisher(
            Odometry,
            'fast_lio/odom',  # Nav2 normalmente espera /odom
            10
        )

        # subscribe à odometria do Pioneer
        self.create_subscription(
            Odometry,
            '/Odometry',  # tópico que você informou
            self.odom_callback,
            10
        )

        # publicador de LiDAR Livox a 20 Hz
        self.create_timer(0.05, self.publish_livox_tf)

        self.get_logger().info(
            "TF publisher rodando: odom->base_link & base_link->livox_frame"
        )

    def odom_callback(self, msg: Odometry):
        """
        Transforma odometria do Pioneer em odom->base_link
        e república a odometria com timestamp atualizado
        """
        # timestamp atual
        current_time = self.get_clock().now().to_msg()

        # Transform odom -> base_link
        t = TransformStamped()
        t.header.stamp = current_time
        t.header.frame_id = 'fast_lio/odom'
        t.child_frame_id = 'fast_lio/base_link'

        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        t.transform.rotation = msg.pose.pose.orientation

        self.broadcaster.sendTransform(t)

        # republika odometria para Nav2
        msg.header.stamp = current_time
        msg.header.frame_id = 'fast_lio/odom'
        self.odom_publisher.publish(msg)

    def publish_livox_tf(self):
        """
        Publica base_link -> livox_frame
        """
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'fast_lio/base_link'
        t.child_frame_id = 'livox_frame'

        # offset do LiDAR
        t.transform.translation.x = 0.2
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.15

        # rotação identidade
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        self.broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = TfPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
