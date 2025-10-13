import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import Twist
from geometry_msgs.msg import TransformStamped
from geometry_msgs.msg import PoseStamped
from scipy.spatial.transform import Rotation as R
import math
import numpy as np

class ScoutSim2RealNode(Node):
    def __init__(self, robot_name="scoutMini1"):
        super().__init__(f"{robot_name}_sim2real_node")
        self.robot_name = robot_name

        self.subscription = self.create_subscription(
            TFMessage, "/tf", self.tf_callback, 10
        )

        self.create_subscription(PoseStamped, "/converted_target_pose", self.target_callback, 10)

        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)

        self.target_x = None  # example goal x position
        self.target_y = None  # example goal y position
        self.target_yaw = None  # example goal yaw angle

        self.align_goal_position = True  # Flag to check if robot is aligned with goal
        self.navigate_goal_position = False  # Flag to check if robot has arrived at goal position
        self.align_goal_orientation = False  # Flag to check if robot is aligned with goal3
        self.waiting_for_target = False  # Flag to check if we are waiting for target pose

        # Controller gains
        self.k_linear = 0.2
        self.k_angular = 0.5

        self.TOLERANCE = 1e-1

        self.get_logger().info("TF listener to cmd_vel publisher initialized")

    def target_callback(self, msg: PoseStamped):
        frame_id = msg.header.frame_id
        robot_name = frame_id.partition("/")[0]
        if robot_name == self.robot_name:
            self.target_x = msg.pose.position.x
            self.target_y = msg.pose.position.y
            self.target_yaw = self.yaw_from_quaternion(msg.pose.orientation)
        self.get_logger().info(
            f"Target position set to: ({self.target_x}, {self.target_y}) with yaw {self.target_yaw}"
        )

    def yaw_from_quaternion(self, quaternion):
        """Convert quaternion to yaw angle."""
        r = R.from_quat([quaternion.x, quaternion.y, quaternion.z, quaternion.w])
        return r.as_euler("xyz")[2]

    def tf_callback(self, msg: TFMessage):
        if self.target_x is None or self.target_y is None:
            # self.get_logger().warn("Target position not set, waiting for target pose.")
            return
        for transform in msg.transforms:
            robot_name = transform.child_frame_id.partition("/")[0]
            # Look for transform from 'odom' to 'scoutMini1'
            if transform.header.frame_id == "world" and robot_name == "scout_mini":
                x = transform.transform.translation.x
                y = transform.transform.translation.y
                yaw = self.yaw_from_quaternion(transform.transform.rotation)

                # Compute simple vector to goal
                dx = self.target_x - x
                dy = self.target_y - y

                twist = Twist()

                if self.align_goal_position == True:
                    u_align = self.align_with_goal(
                        self.target_x, self.target_y, x, y, yaw, 0.3, 0.1
                    )
                    self.get_logger().info(f"Aligning with goal with twist: {u_align}")
                    v_linear, Wz = u_align
                    twist.linear.x = v_linear
                    twist.angular.z = Wz

                elif self.navigate_goal_position == True:

                    if np.linalg.norm((dx, dy)) < self.TOLERANCE:
                        self.publisher.publish(twist)
                        self.get_logger().info(
                            f"Arrived at target: ({x:.2f}, {y:.2f})"
                        )
                        self.navigate_goal_position = False
                        self.align_goal_orientation = True

                        return

                    u_twist = self.twist_feedback_linearization(
                        x,
                        y,
                        yaw,
                        self.target_x,
                        self.target_y,
                        0.0,
                        0.0,
                        self.k_linear,
                        d=0.6,
                    )
                    u_twist = u_twist.flatten().tolist()
                    self.get_logger().info(f"Feedback linearization twist: {u_twist}")
                    twist.linear.x = np.clip(u_twist[0], -0.2, 0.2)
                    twist.angular.z = np.clip(u_twist[1], -0.5, 0.5)

                elif self.align_goal_orientation == True:
                    # Align with goal orientation
                    theta_m = yaw
                    theta_ref = self.target_yaw

                    theta_error = self.normalize_angle(theta_ref - theta_m)
                    if abs(theta_error) < 0.1:
                        # If within error tolerance to align
                        self.align_goal_orientation = False
                        self.waiting_for_target = True
                        twist.linear.x = 0.0
                        twist.angular.z = 0.0
                    else:
                        # Apply feedback linearization to align with goal orientation
                        twist.linear.x = 0.0
                        twist.angular.z = np.clip(
                            self.k_angular * theta_error, -0.5, 0.5
                        )
                elif self.waiting_for_target:

                    if np.linalg.norm((dx, dy)) < self.TOLERANCE:
                        self.publisher.publish(twist)
                        self.get_logger().info(
                            f"Waiting for target at: ({x:.2f}, {y:.2f})"
                        )
                    else:
                        # If we are waiting for a target pose, we stop the robot
                        self.get_logger().info(
                            f"Received target pose at: ({self.target_x:.2f}, {self.target_y:.2f})"
                        )
                        self.waiting_for_target = False
                        self.align_goal_position = True

                    # If we are waiting for a target pose, stop the robot
                    twist.linear.x = 0.0
                    twist.angular.z = 0.0

                self.publisher.publish(twist)
                self.get_logger().info(
                    f"Going to target: ({self.target_x:.2f}, {self.target_y:.2f})"
                )
                self.get_logger().info(
                    f"Current position: ({x:.2f}, {y:.2f}) -> Publishing: linear.x={twist.linear.x:.2f}, angular.z={twist.angular.z:.2f}"
                )

    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def align_with_goal(self, xd, yd, xm, ym, theta_m, kp, desired_error) -> tuple:
        """Return the twist to apply to robot such that it aligns with the
        desired position (xd, yd) given the measured position (xm, ym), and
        the measured orientation about the z-axis (theta_m).

        Args:
            xd (float): the desired x position.
            yd (float): the desire'd y position.
            xm (float): the measured x position.
            ym (float): the measured y position.
            theta_m (float): the measured orientation about the z-axis.
            desired_error (float): the desired alignment error to reach.
        """
        # Get current alignment angle
        delta_x = xd - xm
        delta_y = yd - ym
        theta_ref = np.arctan2(delta_y, delta_x)

        # The linear velocity is zero, since we are aligning
        V = 0.0

        # The angular velocity is the difference to align
        Wz = kp*(theta_ref - theta_m)

        # Store twist
        twist = (V, Wz)

        if abs(theta_ref - theta_m) < desired_error:
            # If within error tolerance to align
            self.align_goal_position = False
            self.navigate_goal_position = True

        return twist

    def twist_feedback_linearization(
        self, x, y, yaw, xd, yd, dot_x, dot_y, gain, d=0.1
    ):
        """Return the twist of the robot using feedback linearization.

        Args:
            x (float): the current x position.
            y (float): the current y position.
            yaw (float): the current yaw of the robot.
            xd (float): the desired x position.
            yd (float): the desired y position.
            dot_x (float): the desired x velocity.
            dot_y (float): the desired y velocity.
            gain (float): the feedback linearization gain.
            d (float, optional): the distance from the robot center to a point on the robot. Defaults to 0.1.

        Returns:
            np array: the robot twist.
        """

        # Transform linear and angular velocity (twist) to
        # x- and y- velocities
        T = np.array(
            [[math.cos(yaw), (-d) * math.sin(yaw)], [math.sin(yaw), d * math.cos(yaw)]]
        )

        # Use the inverse to get the opposite: get twist from linear and angular velocities
        T_inv = np.linalg.inv(T)

        # Control inputs are the x- and y- desired velocities to goal configuration
        u = np.array([[dot_x + gain * (xd - x)], [dot_y + gain * (yd - y)]])

        # Transform from x- and y-velocities to twist
        twist = np.matmul(T_inv, u)

        return twist


def main(args=None):
    rclpy.init(args=args)
    node = ScoutSim2RealNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
