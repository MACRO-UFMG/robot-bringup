#!/usr/bin/env python3
"""
Enhanced ROS 2 Publisher with image_transport support
Reads frames from shared memory and publishes with multiple transport options
Compatible with ROS 2 Jazzy - Optimized for efficiency
"""

import os
import sys
import time
import json
import mmap
import struct
import numpy as np
import threading
from pathlib import Path
from typing import Dict, Optional

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image, CameraInfo, CompressedImage
from std_msgs.msg import Header
import cv2
from cv_bridge import CvBridge

class SharedMemoryReader:
    """Optimized shared memory reader for frame data"""
    
    def __init__(self, name: str, logger):
        self.name = name
        self.logger = logger
        self.shm_path = f"/dev/shm/rtsp_frames_{name}"
        self.header_size = 20
        
        # Wait for shared memory file to be created
        max_wait = 30  # seconds
        wait_time = 0
        while not os.path.exists(self.shm_path) and wait_time < max_wait:
            self.logger.info(f"Waiting for shared memory: {self.shm_path}")
            time.sleep(1)
            wait_time += 1
        
        if not os.path.exists(self.shm_path):
            raise FileNotFoundError(f"Shared memory not found: {self.shm_path}")
        
        # Open memory-mapped file with optimized access
        self.shm_file = open(self.shm_path, 'rb')
        file_size = os.path.getsize(self.shm_path)
        self.mmap = mmap.mmap(self.shm_file.fileno(), file_size, access=mmap.ACCESS_READ)
        
        # Pre-allocate header struct for performance
        self._header_struct = struct.Struct('IIQI')
        
        self.logger.info(f"Connected to shared memory: {self.shm_path} ({file_size} bytes)")
    
    def read_frame(self) -> Optional[np.ndarray]:
        """Read frame from shared memory with detailed logging"""
        try:
            # Read header efficiently
            self.mmap.seek(0)
            header_bytes = self.mmap.read(self.header_size)
            
            if len(header_bytes) != self.header_size:
                return None
            
            # Parse header
            width, height, timestamp, frame_size = self._header_struct.unpack(header_bytes)
            
            # Log detailed header information
            file_size = os.path.getsize(self.shm_path)
            mmap_size = len(self.mmap)
            raw_header_hex = header_bytes.hex()
            
            self.logger.info(f"[{self.name}] File size: {file_size} bytes, mmap size: {mmap_size} bytes")
            self.logger.info(f"[{self.name}] Header: {width}x{height}, frame_size={frame_size}, timestamp={timestamp}")
            self.logger.info(f"[{self.name}] Raw header bytes: {raw_header_hex}")
            
            # Validate header
            if width == 0 or height == 0 or frame_size == 0:
                if all(b == 0 for b in header_bytes):
                    self.logger.warn(f"[{self.name}] All header data is zeros - stream server not writing data!")
                else:
                    self.logger.warn(f"[{self.name}] Invalid header: width={width}, height={height}, frame_size={frame_size}")
                return None
            
            expected_frame_size = width * height * 3  # BGR
            if frame_size != expected_frame_size:
                self.logger.warn(f"[{self.name}] Frame size mismatch: got {frame_size}, expected {expected_frame_size}")
                return None
            
            # Check if we have enough data
            available_data = len(self.mmap) - self.header_size
            if available_data < frame_size:
                self.logger.warn(f"[{self.name}] Insufficient data: need {frame_size}, have {available_data}")
                return None
            
            # Read frame data efficiently
            frame_data = self.mmap.read(frame_size)
            if len(frame_data) != frame_size:
                self.logger.warn(f"[{self.name}] Incomplete frame read: got {len(frame_data)}, expected {frame_size}")
                return None
            
            # Convert to numpy array and reshape
            frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((height, width, 3))
            return frame
            
        except Exception as e:
            self.logger.error(f"[{self.name}] Error reading frame: {e}")
            return None
    
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'mmap'):
            self.mmap.close()
        if hasattr(self, 'shm_file'):
            self.shm_file.close()

class EnhancedROSCameraPublisher(Node):
    """Enhanced ROS 2 camera publisher with image_transport support"""
    
    def __init__(self, stream_name: str, config: dict, jpeg_quality: int = 80):
        super().__init__(f'rtsp_publisher_{stream_name}')
        
        self.stream_name = stream_name
        self.config = config
        self.jpeg_quality = jpeg_quality
        self.bridge = CvBridge()
        self.running = True
        
        # Create QoS profile for image topics
        image_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        # Create publishers
        topic_base = f"/camera/{stream_name}"
        
        # Raw image publisher
        self.image_pub = self.create_publisher(
            Image, 
            f"{topic_base}/image_raw", 
            image_qos
        )
        
        # Compressed image publisher
        self.compressed_pub = self.create_publisher(
            CompressedImage,
            f"{topic_base}/image_raw/compressed",
            image_qos
        )
        
        # Camera info publisher
        self.camera_info_pub = self.create_publisher(
            CameraInfo,
            f"{topic_base}/camera_info",
            image_qos
        )
        
        # Initialize shared memory reader
        self.shm_reader = SharedMemoryReader(stream_name, self.get_logger())
        
        # Create camera info message
        self.camera_info_msg = self._create_camera_info()
        
        # Start publishing thread
        self.publish_thread = threading.Thread(target=self._publish_loop, daemon=True)
        self.publish_thread.start()
        
        self.get_logger().info(f"Enhanced ROS publisher created for {stream_name} (FPS: {config.get('fps', 30)})")
        self.get_logger().info(f"JPEG Quality: {jpeg_quality}%, Raw: True, Compressed: True")
    
    def _create_camera_info(self) -> CameraInfo:
        """Create camera info message"""
        info = CameraInfo()
        info.width = self.config.get('width', 640)
        info.height = self.config.get('height', 480)
        
        # Simple camera model (you can enhance this with calibration data)
        info.distortion_model = "plumb_bob"
        info.d = [0.0, 0.0, 0.0, 0.0, 0.0]
        
        # Camera matrix (simple approximation)
        fx = fy = max(info.width, info.height)
        cx = info.width / 2.0
        cy = info.height / 2.0
        
        info.k = [fx, 0.0, cx,
                  0.0, fy, cy,
                  0.0, 0.0, 1.0]
        
        info.r = [1.0, 0.0, 0.0,
                  0.0, 1.0, 0.0,
                  0.0, 0.0, 1.0]
        
        info.p = [fx, 0.0, cx, 0.0,
                  0.0, fy, cy, 0.0,
                  0.0, 0.0, 1.0, 0.0]
        
        return info
    
    def _publish_loop(self):
        """Main publishing loop"""
        fps = self.config.get('fps', 30)
        sleep_time = 1.0 / fps
        frame_count = 0
        
        while self.running and rclpy.ok():
            try:
                # Read frame from shared memory
                frame = self.shm_reader.read_frame()
                
                if frame is not None:
                    # Create timestamp
                    now = self.get_clock().now()
                    
                    # Create header
                    header = Header()
                    header.stamp = now.to_msg()
                    header.frame_id = f"{self.stream_name}_optical_frame"
                    
                    # Publish raw image
                    try:
                        image_msg = self.bridge.cv2_to_imgmsg(frame, "bgr8")
                        image_msg.header = header
                        self.image_pub.publish(image_msg)
                    except Exception as e:
                        self.get_logger().error(f"Error publishing raw image: {e}")
                    
                    # Publish compressed image
                    try:
                        # Encode as JPEG
                        encode_params = [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]
                        success, encoded_image = cv2.imencode('.jpg', frame, encode_params)
                        
                        if success:
                            compressed_msg = CompressedImage()
                            compressed_msg.header = header
                            compressed_msg.format = "jpeg"
                            compressed_msg.data = encoded_image.tobytes()
                            self.compressed_pub.publish(compressed_msg)
                    except Exception as e:
                        self.get_logger().error(f"Error publishing compressed image: {e}")
                    
                    # Publish camera info
                    self.camera_info_msg.header = header
                    self.camera_info_pub.publish(self.camera_info_msg)
                    
                    frame_count += 1
                    if frame_count % (fps * 5) == 0:  # Log every 5 seconds
                        self.get_logger().info(f"[{self.stream_name}] Published {frame_count} frames, shape: {frame.shape}")
                
                time.sleep(sleep_time)
                
            except Exception as e:
                self.get_logger().error(f"Error in publish loop: {e}")
                time.sleep(1.0)
    
    def destroy_node(self):
        """Clean shutdown"""
        self.running = False
        if hasattr(self, 'publish_thread'):
            self.publish_thread.join(timeout=2.0)
        if hasattr(self, 'shm_reader'):
            self.shm_reader.close()
        super().destroy_node()

class EnhancedROSCameraSystem(Node):
    """Main ROS 2 system managing multiple camera publishers"""
    
    def __init__(self):
        super().__init__('rtsp_camera_system')
        
        # Get parameters
        self.declare_parameter('config_file', '/app/config/cameras.json')
        self.declare_parameter('jpeg_quality', 80)
        
        config_file = self.get_parameter('config_file').get_parameter_value().string_value
        jpeg_quality = self.get_parameter('jpeg_quality').get_parameter_value().integer_value
        
        self.publishers = {}
        
        # Load camera configuration
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except Exception as e:
            self.get_logger().error(f"Failed to load config: {e}")
            return
        
        # Create publishers for each camera stream
        for camera in config.get('cameras', []):
            camera_name = camera['name']
            
            for channel in camera.get('channels', []):
                stream_name = f"{camera_name}_{channel['name']}"
                
                try:
                    publisher = EnhancedROSCameraPublisher(
                        stream_name, 
                        channel, 
                        jpeg_quality
                    )
                    self.publishers[stream_name] = publisher
                    self.get_logger().info(f"Started enhanced ROS publisher for {stream_name}")
                    
                except Exception as e:
                    self.get_logger().error(f"Failed to create publisher for {stream_name}: {e}")
        
        self.get_logger().info(f"Enhanced ROS Camera Publisher initialized with {len(self.publishers)} streams")
        self.get_logger().info("Available topics:")
        for stream_name in self.publishers.keys():
            self.get_logger().info(f"- /camera/{stream_name}/image_raw")
            self.get_logger().info(f"- /camera/{stream_name}/image_raw/compressed")
            self.get_logger().info(f"- /camera/{stream_name}/camera_info")
        
        self.get_logger().info("Enhanced ROS Camera Publisher running...")
        self.get_logger().info("Use 'ros2 run image_view image_view --ros-args --remap image:=/camera/camera1_main/image_raw' to view")
        self.get_logger().info("Use 'rviz2' and add Image display with topic /camera/camera1_main/image_raw")
    

    @property
    def publishers(self):
        return self._publishers

    @publishers.setter
    def publishers(self, value):
        self._publishers = value

    def destroy_node(self):
        """Clean shutdown of all publishers"""
        for publisher in self.publishers.values():
            publisher.destroy_node()
        super().destroy_node()

def main(args=None):
    """Main entry point"""
    rclpy.init(args=args)
    
    try:
        node = EnhancedROSCameraSystem()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
