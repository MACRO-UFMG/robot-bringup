from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # TF de livox_frame -> body
     #   Node(
      #      package="tf2_ros",
       #     executable="static_transform_publisher",
        #    name="body_to_livox_tf",
         #   arguments=["0", "0", "0", "0", "0", "0", "body", "livox"]
       # ),

        # TF camera_link -> body
       # Node(
        #    package="tf2_ros",
       #     executable="static_transform_publisher",
       #     name="body_to_camera_tf",
      #      arguments=["0.2", "0.0", "0.1", "0", "0", "0", "body", "camera_link"]
     #   ),

    ])
