#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import numpy as np

from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2 as pc2

from livox_ros_driver2.msg import CustomMsg, CustomPoint


class PointCloudConverter(Node):
    def __init__(self):
        super().__init__('pointcloud_converter')
        # Publicador para CustomMsg
        self.pub = self.create_publisher(CustomMsg, '/livox/lidar_CustomMsg', 10)
        # Assinante do PointCloud2 original
        self.sub = self.create_subscription(
            PointCloud2,
            '/livox/lidar',
            self.callback,
            10
        )

    def callback(self, pointcloud_msg: PointCloud2):
        # Cria a mensagem CustomMsg
        custom_cloud = CustomMsg()
        custom_cloud.header = pointcloud_msg.header

        # Converte stamp para nanosegundos
        timebase = (
            pointcloud_msg.header.stamp.sec * 1_000_000_000
            + pointcloud_msg.header.stamp.nanosec
        )
        custom_cloud.timebase = timebase

        # Lê pontos diretamente sem conversão numpy (mais rápido)
        pontos = pc2.read_points(pointcloud_msg, skip_nans=True)

        # HYPER-OPTIMIZED: Pure Python with zero overhead
        custom_points = []
        append_point = custom_points.append  # Cache method lookup
        
        # Ultra-fast single pass processing
        for pt in pontos:
            # Skip zero points with fastest check
            if pt[0] == 0.0 and pt[1] == 0.0 and pt[2] == 0.0:
                continue
                
            # Create CustomPoint with minimal overhead    
            cp = CustomPoint()
            cp.offset_time = abs(int(pt[6] - timebase))  # Ensure positive
            cp.x = pt[0]
            cp.y = pt[1]
            cp.z = pt[2]
            cp.reflectivity = int(pt[3])
            cp.tag = int(pt[4])
            cp.line = int(pt[5])
            append_point(cp)

        # Finaliza mensagem
        custom_cloud.points = custom_points
        custom_cloud.point_num = len(custom_points)
        custom_cloud.lidar_id = 0  # ID de exemplo

        # Publica a mensagem convertida
        self.pub.publish(custom_cloud)


def main(args=None):
    rclpy.init(args=args)
    node = PointCloudConverter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

