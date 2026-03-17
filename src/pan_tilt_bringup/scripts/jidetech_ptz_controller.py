#!/usr/bin/env python3
"""
Jidetech PTZ Controller Node

This script runs the PTZ control node for Jidetech IP cameras.
It provides pan, tilt, and zoom control via ONVIF or HTTP interfaces.
"""

import sys
import argparse
import rclpy
from rclpy.executors import MultiThreadedExecutor

from ptz_controller import JidetechPTZNode


def main(args=None):
    """Main function for the PTZ controller node."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Jidetech PTZ Controller Node')
    parser.add_argument('--ros-args', nargs='*', help='ROS arguments')
    parser.add_argument('--log-level', default='info', 
                       choices=['debug', 'info', 'warn', 'error'],
                       help='Log level')
    
    # Parse known args (ROS 2 will handle unknown args)
    args, unknown = parser.parse_known_args()
    
    # Initialize ROS 2
    rclpy.init(args=unknown)
    
    try:
        # Create PTZ controller node
        ptz_node = JidetechPTZNode()
        
        # Create executor
        executor = MultiThreadedExecutor()
        executor.add_node(ptz_node)
        
        # Spin the node
        executor.spin()
        
    except KeyboardInterrupt:
        print("PTZ controller node interrupted by user")
    except Exception as e:
        print(f"Error in PTZ controller node: {str(e)}")
    finally:
        # Cleanup
        if 'ptz_node' in locals():
            ptz_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main() 