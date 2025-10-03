#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
<<<<<<< HEAD
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from rclpy.qos import QoSProfile, ReliabilityPolicy
=======

from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry

from tf2_ros import TransformBroadcaster

>>>>>>> 10609bd (scout_bringup)

class TfPublisher(Node):
    def __init__(self):
        super().__init__('tf_publisher')

<<<<<<< HEAD
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
=======
        # single broadcaster for all dynamic transforms
        self.broadcaster = TransformBroadcaster(self)
        
        # <<< INÍCIO DA MODIFICAÇÃO >>>
        # create a publisher for the re-stamped odometry
        self.odom_publisher = self.create_publisher(
            Odometry,
            '/scout/odom',          # new topic name
            10
        )
        # <<< FIM DA MODIFICAÇÃO >>>

        # subscribe to your odometry source
        self.create_subscription(
            Odometry,
            '/Odometry',          # use your actual topic name
            self.odom_callback,
            10
        )

        # publish the LiDAR offset at 20 Hz
        self.create_timer(0.05, self.publish_livox_tf)

        self.get_logger().info(
            "TF publisher running: publishing odom→base_link & base_link→livox_frame"
        )

    def odom_callback(self, msg: Odometry):
        """
        Broadcast odom → base_link from each incoming Odometry
        and republish the odometry with an updated timestamp.
        """
        # <<< INÍCIO DA MODIFICAÇÃO >>>
        # Get the current time once to ensure consistency
        current_time = self.get_clock().now().to_msg()
        # <<< FIM DA MODIFICAÇÃO >>>

        # debug log so you can verify it's firing
        self.get_logger().debug(
            f"Got Odometry @ {msg.header.stamp.sec}.{msg.header.stamp.nanosec}"
        )

        t = TransformStamped()
        #t.header.stamp = current_time # Use current time
        t.header.frame_id = 'fast_lio/odom'
        t.child_frame_id = 'fast_lio/base_link'

        # pass through position
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z

        # pass through orientation
        t.transform.rotation = msg.pose.pose.orientation

        self.broadcaster.sendTransform(t)
        
        # <<< INÍCIO DA MODIFICAÇÃO >>>
        # Update the timestamp of the original odometry message
        msg.header.stamp = current_time
        
        # Publish the message on the new topic
        self.odom_publisher.publish(msg)
        # <<< FIM DA MODIFICAÇÃO >>>


    # def odom_callback(self, msg: Odometry):
    #     """Broadcast odom → base_link from each incoming Odometry."""
    #     # debug log so you can verify it's firing
    #     self.get_logger().debug(
    #         f"Got Odometry @ {msg.header.stamp.sec}.{msg.header.stamp.nanosec}"
    #     )

    #     t = TransformStamped()
    #     t.header.stamp = msg.header.stamp
    #     t.header.frame_id = 'body'
    #     t.child_frame_id = 'livox_frame'

    #     # your LiDAR offset relative to the robot base
    #     t.transform.translation.x = 0.2
    #     t.transform.translation.y = 0.0
    #     t.transform.translation.z = 0.15

    #     # identity rotation
    #     t.transform.rotation.x = 0.0
    #     t.transform.rotation.y = 0.0
    #     t.transform.rotation.z = 0.0
    #     t.transform.rotation.w = 1.0 

    #     self.broadcaster.sendTransform(t)

    def publish_livox_tf(self):
        """Broadcast base_link → livox_frame at a fixed, static offset."""
>>>>>>> 10609bd (scout_bringup)
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'fast_lio/base_link'
        t.child_frame_id = 'livox_frame'
<<<<<<< HEAD
        t.transform.translation.x = 0.2
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.15
=======

        # your LiDAR offset relative to the robot base
        t.transform.translation.x = 0.2
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.15

        # identity rotation
>>>>>>> 10609bd (scout_bringup)
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0
<<<<<<< HEAD
        self.broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = TfPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
=======

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

>>>>>>> 10609bd (scout_bringup)

if __name__ == '__main__':
    main()
