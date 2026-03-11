#!/usr/bin/env python3
"""
Enhanced ROS Publisher with image_transport support
Reads frames from shared memory and publishes with multiple transport options
Compatible with ROS 1 Noetic - Optimized for efficiency
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

import rospy
from sensor_msgs.msg import Image, CameraInfo, CompressedImage
from std_msgs.msg import Header
import cv2
from cv_bridge import CvBridge

class SharedMemoryReader:
    """Optimized shared memory reader for frame data"""
    
    def __init__(self, name: str):
        self.name = name
        self.shm_path = f"/dev/shm/rtsp_frames_{name}"
        self.header_size = 20
        
        # Wait for shared memory file to be created
        max_wait = 30  # seconds
        wait_time = 0
        while not os.path.exists(self.shm_path) and wait_time < max_wait:
            rospy.loginfo(f"Waiting for shared memory: {self.shm_path}")
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
        
        rospy.loginfo(f"Connected to shared memory: {self.shm_path} ({file_size} bytes)")
    
    def read_frame(self) -> Optional[tuple]:
        """Read frame from shared memory. Returns (frame, timestamp) or None"""
        try:
            # Read header
            self.mmap.seek(0)
            header_data = self.mmap.read(self.header_size)
            if len(header_data) != self.header_size:
                rospy.logwarn_throttle(5, f"[{self.name}] Header read failed: got {len(header_data)}, expected {self.header_size}")
                return None
            
            width, height, timestamp_us, frame_size = self._header_struct.unpack(header_data)
            
            # Enhanced debug logging (throttled to avoid spam)
            file_size = os.path.getsize(self.shm_path) if os.path.exists(self.shm_path) else 0
            rospy.loginfo_throttle(10, f"[{self.name}] File size: {file_size} bytes, mmap size: {len(self.mmap)} bytes")
            rospy.loginfo_throttle(10, f"[{self.name}] Header: {width}x{height}, frame_size={frame_size}, timestamp={timestamp_us}")
            rospy.loginfo_throttle(10, f"[{self.name}] Raw header bytes: {header_data.hex()}")
            
            if width == 0 or height == 0 or frame_size == 0:
                rospy.logwarn_throttle(5, f"[{self.name}] Invalid header: width={width}, height={height}, frame_size={frame_size}")
                rospy.logwarn_throttle(5, f"[{self.name}] All header data is zeros - stream server not writing data!")
                return None
            
            # Validate frame size makes sense
            expected_size = width * height * 3
            if frame_size != expected_size:
                rospy.logwarn_throttle(5, f"[{self.name}] Frame size mismatch: got {frame_size}, expected {expected_size} ({width}x{height}x3)")
                return None
            
            # Read frame data
            frame_data = self.mmap.read(frame_size)
            if len(frame_data) != frame_size:
                rospy.logwarn_throttle(5, f"[{self.name}] Frame data read failed: got {len(frame_data)}, expected {frame_size}")
                return None
            
            # Convert to numpy array (zero-copy from memoryview)
            frame = np.frombuffer(frame_data, dtype=np.uint8)
            frame = frame.reshape((height, width, 3))
            
            timestamp = timestamp_us / 1000000.0  # Convert back to seconds
            
            # Success logging (throttled)
            rospy.loginfo_throttle(30, f"[{self.name}] Successfully read frame: {width}x{height}, timestamp={timestamp}")
            
            return frame, timestamp
            
        except Exception as e:
            rospy.logwarn_throttle(5, f"[{self.name}] Error reading frame: {e}")
            return None
    
    def close(self):
        """Cleanup"""
        if hasattr(self, 'mmap'):
            self.mmap.close()
        if hasattr(self, 'shm_file'):
            self.shm_file.close()

class EnhancedROSCameraPublisher:
    """Enhanced ROS publisher with image_transport support for multiple compression formats"""
    
    def __init__(self, stream_name: str, camera_config: dict):
        self.stream_name = stream_name
        self.config = camera_config
        
        # Get FPS from config, default to 30
        self.fps = camera_config.get('fps', 30)
        
        # Initialize CV Bridge for image conversion
        self.bridge = CvBridge()
        
        # Create ROS publishers for different transport types
        self.base_topic = f'/camera/{stream_name}'
        
        # Raw image publisher
        self.image_pub = rospy.Publisher(
            f'{self.base_topic}/image_raw',
            Image,
            queue_size=1
        )
        
        # Compressed image publisher (JPEG)
        self.compressed_pub = rospy.Publisher(
            f'{self.base_topic}/image_raw/compressed',
            CompressedImage,
            queue_size=1
        )
        
        # Camera info publisher
        self.camera_info_pub = rospy.Publisher(
            f'{self.base_topic}/camera_info',
            CameraInfo,
            queue_size=1
        )
        
        # Initialize shared memory reader
        self.shm_reader = SharedMemoryReader(stream_name)
        
        # Camera info message template
        self.camera_info_msg = self._create_camera_info()
        
        # Publisher thread
        self.running = False
        self.thread = None
        
        # Compression settings for efficiency
        self.jpeg_quality = rospy.get_param('~jpeg_quality', 80)  # 80% quality
        self.publish_raw = rospy.get_param('~publish_raw', True)
        self.publish_compressed = rospy.get_param('~publish_compressed', True)
        
        rospy.loginfo(f"Enhanced ROS publisher created for {stream_name} (FPS: {self.fps})")
        rospy.loginfo(f"JPEG Quality: {self.jpeg_quality}%, Raw: {self.publish_raw}, Compressed: {self.publish_compressed}")
    
    def _create_camera_info(self) -> CameraInfo:
        """Create camera info message with proper calibration"""
        camera_info = CameraInfo()
        
        # Set frame ID
        camera_info.header.frame_id = f"{self.stream_name}_optical_frame"
        
        # Set dimensions from config
        camera_info.width = self.config.get('width', 1920)
        camera_info.height = self.config.get('height', 1080)
        
        # Set distortion model
        camera_info.distortion_model = "plumb_bob"
        camera_info.D = [0.0, 0.0, 0.0, 0.0, 0.0]
        
        # Set camera matrix (calibrate for your specific camera)
        fx = camera_info.width * 0.8  # Typical focal length approximation
        fy = camera_info.height * 0.8
        cx = camera_info.width / 2.0
        cy = camera_info.height / 2.0
        
        camera_info.K = [
            fx, 0.0, cx,
            0.0, fy, cy,
            0.0, 0.0, 1.0
        ]
        
        # Set rectification matrix (identity for monocular)
        camera_info.R = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        
        # Set projection matrix
        camera_info.P = [
            fx, 0.0, cx, 0.0,
            0.0, fy, cy, 0.0,
            0.0, 0.0, 1.0, 0.0
        ]
        
        return camera_info
    
    def start(self):
        """Start publishing"""
        self.running = True
        self.thread = threading.Thread(target=self._publish_loop, daemon=True)
        self.thread.start()
        rospy.loginfo(f"Started enhanced ROS publisher for {self.stream_name}")
    
    def stop(self):
        """Stop publishing"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        self.shm_reader.close()
        rospy.loginfo(f"Stopped ROS publisher for {self.stream_name}")
    
    def _publish_loop(self):
        """Optimized publishing loop with multiple transport support"""
        rate = rospy.Rate(self.fps)  # Use configured FPS
        
        # JPEG compression parameters for cv2
        jpeg_params = [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]
        
        frame_count = 0
        while self.running and not rospy.is_shutdown():
            try:
                # Read frame from shared memory
                result = self.shm_reader.read_frame()
                if result is None:
                    rospy.logwarn_throttle(10, f"[{self.stream_name}] No frame data available from shared memory")
                    rate.sleep()
                    continue
                
                frame, timestamp = result
                frame_count += 1
                
                # Log publishing activity
                rospy.loginfo_throttle(30, f"[{self.stream_name}] Publishing frame #{frame_count}, shape: {frame.shape}")
                
                # Create ROS timestamp
                ros_time = rospy.Time.now()
                
                # Create header
                header = Header()
                header.stamp = ros_time
                header.frame_id = f"{self.stream_name}_optical_frame"
                
                # Publish raw image if enabled
                if self.publish_raw and self.image_pub.get_num_connections() > 0:
                    try:
                        image_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
                        image_msg.header = header
                        self.image_pub.publish(image_msg)
                    except Exception as e:
                        rospy.logwarn(f"Error publishing raw image for {self.stream_name}: {e}")
                
                # Publish compressed image if enabled and someone is listening
                if self.publish_compressed and self.compressed_pub.get_num_connections() > 0:
                    try:
                        # Compress image using OpenCV (efficient)
                        success, compressed_data = cv2.imencode('.jpg', frame, jpeg_params)
                        
                        if success:
                            compressed_msg = CompressedImage()
                            compressed_msg.header = header
                            compressed_msg.format = "jpeg"
                            compressed_msg.data = compressed_data.tobytes()
                            self.compressed_pub.publish(compressed_msg)
                    except Exception as e:
                        rospy.logwarn(f"Error publishing compressed image for {self.stream_name}: {e}")
                
                # Update and publish camera info
                if self.camera_info_pub.get_num_connections() > 0:
                    self.camera_info_msg.header = header
                    self.camera_info_msg.width = frame.shape[1]
                    self.camera_info_msg.height = frame.shape[0]
                    self.camera_info_pub.publish(self.camera_info_msg)
                
            except Exception as e:
                rospy.logerr(f"Error in publish loop for {self.stream_name}: {e}")
            
            rate.sleep()

class EnhancedROSPublisherNode:
    """Main ROS node managing multiple enhanced camera publishers"""
    
    def __init__(self):
        # Initialize ROS node
        rospy.init_node('rtsp_camera_publisher', anonymous=True)
        
        # Load configuration
        config_file = rospy.get_param('~config_file', '/app/config/cameras.json')
        self.config = self._load_config(config_file)
        
        # Create publishers for each stream
        self.publishers: Dict[str, EnhancedROSCameraPublisher] = {}
        self._create_publishers()
        
        rospy.loginfo(f"Enhanced ROS Camera Publisher initialized with {len(self.publishers)} streams")
        rospy.loginfo("Available topics:")
        for stream_name in self.publishers.keys():
            rospy.loginfo(f"  - /camera/{stream_name}/image_raw")
            rospy.loginfo(f"  - /camera/{stream_name}/image_raw/compressed")
            rospy.loginfo(f"  - /camera/{stream_name}/camera_info")
    
    def _load_config(self, config_file: str) -> dict:
        """Load camera configuration"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            rospy.logerr(f"Failed to load config: {e}")
            sys.exit(1)
    
    def _create_publishers(self):
        """Create ROS publishers for all configured streams"""
        cameras = self.config.get('cameras', [])
        
        for camera in cameras:
            camera_name = camera.get('name', 'unknown')
            channels = camera.get('channels', [])
            
            for channel in channels:
                channel_name = channel.get('name', 'main')
                stream_name = f"{camera_name}_{channel_name}"
                
                # Create enhanced publisher
                publisher = EnhancedROSCameraPublisher(stream_name, channel)
                self.publishers[stream_name] = publisher
                publisher.start()
    
    def run(self):
        """Main execution loop"""
        rospy.loginfo("Enhanced ROS Camera Publisher running...")
        rospy.loginfo("Use 'rosrun image_view image_view image:=/camera/camera1_main/image_raw' to view")
        rospy.loginfo("Use 'rosrun rviz rviz' and add Image display with topic /camera/camera1_main/image_raw")
        
        try:
            rospy.spin()
        except KeyboardInterrupt:
            rospy.loginfo("Shutting down Enhanced ROS Camera Publisher...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop all publishers"""
        for publisher in self.publishers.values():
            publisher.stop()
        rospy.loginfo("All enhanced publishers stopped")

def main():
    """Main entry point"""
    try:
        node = EnhancedROSPublisherNode()
        node.run()
    except Exception as e:
        rospy.logerr(f"Failed to start enhanced ROS publisher: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
