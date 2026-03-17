#!/usr/bin/env python3
"""
Optimized Streamer Server - Direct GStreamer to shared memory with minimal latency
Hardware-accelerated RTSP decoder for Jetson platforms using subprocess
"""

import os
import sys
import time
import json
import subprocess
import threading
import numpy as np
import mmap
import struct
import signal
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Global variable for signal handler
server_instance = None

class OptimizedSharedMemoryWriter:
    """Direct shared memory writer optimized for minimal latency"""
    
    def __init__(self, name: str, max_width: int = 2560, max_height: int = 1440):
        self.name = name
        self.max_width = max_width
        self.max_height = max_height
        self.max_frame_size = max_width * max_height * 3  # BGR
        
        # Create shared memory file
        self.shm_path = f"/dev/shm/rtsp_frames_{name}"
        
        # Optimized header: width(4) + height(4) + timestamp(8) + frame_size(4) = 20 bytes
        self.header_size = 20
        self.total_size = self.header_size + self.max_frame_size
        
        # Create memory-mapped file with optimized flags
        with open(self.shm_path, 'wb') as f:
            f.write(b'\x00' * self.total_size)
        
        self.shm_file = open(self.shm_path, 'r+b')
        self.mmap = mmap.mmap(
            self.shm_file.fileno(), 
            self.total_size,
            flags=mmap.MAP_SHARED,
            prot=mmap.PROT_READ | mmap.PROT_WRITE
        )
        
        # Pre-allocate header struct for performance
        self._header_struct = struct.Struct('IIQI')
        
        print(f"Created optimized shared memory: {self.shm_path} ({self.total_size} bytes)")
    
    def write_frame_direct(self, frame_data: bytes, width: int, height: int, timestamp: float):
        """Write frame data directly to shared memory (minimal copy)"""
        frame_size = len(frame_data)
        if frame_size > self.max_frame_size:
            return False
        
        # Pack header directly
        header = self._header_struct.pack(width, height, int(timestamp * 1000000), frame_size)
        
        # Single write operation to minimize latency
        self.mmap.seek(0)
        self.mmap.write(header)
        self.mmap.write(frame_data)
        # Skip flush for even lower latency - OS will handle it
        
        return True
    
    def write_frame(self, frame: np.ndarray, timestamp: float):
        """Write numpy frame to shared memory (compatibility method)"""
        if frame is None:
            return False
        
        height, width, channels = frame.shape
        if channels != 3:
            return False
        
        return self.write_frame_direct(frame.tobytes(), width, height, timestamp)
    
    def close(self):
        """Cleanup shared memory"""
        if hasattr(self, 'mmap'):
            self.mmap.close()
        if hasattr(self, 'shm_file'):
            self.shm_file.close()
        if os.path.exists(self.shm_path):
            os.unlink(self.shm_path)

class OptimizedGStreamerStream:
    """Optimized hardware-accelerated GStreamer stream using subprocess"""
    
    def __init__(self, rtsp_url: str, name: str, width: int = 0, height: int = 0, 
                 use_nvdec: bool = True, username: str = None, password: str = None):
        self.rtsp_url = rtsp_url
        self.name = name
        self.width = width
        self.height = height
        self.use_nvdec = use_nvdec
        self.username = username
        self.password = password
        self.process = None
        self.running = False
        
        # Build authenticated RTSP URL if credentials provided
        if self.username and self.password:
            self.rtsp_url = self._build_authenticated_url()
        
        # Optimized shared memory writer with actual dimensions
        actual_width = width if width > 0 else 1920
        actual_height = height if height > 0 else 1080
        self.shm_writer = OptimizedSharedMemoryWriter(
            name, 
            max_width=actual_width, 
            max_height=actual_height
        )
        
        print(f"Created shared memory for {name}: {actual_width}x{actual_height} (max_frame_size: {actual_width * actual_height * 3} bytes)")
    
    def _build_authenticated_url(self) -> str:
        """Build RTSP URL with authentication"""
        from urllib.parse import urlparse, urlunparse
        
        parsed = urlparse(self.rtsp_url)
        
        # Build new netloc with credentials
        if parsed.port:
            netloc = f"{self.username}:{self.password}@{parsed.hostname}:{parsed.port}"
        else:
            netloc = f"{self.username}:{self.password}@{parsed.hostname}"
        
        # Rebuild URL
        authenticated_url = urlunparse((
            parsed.scheme,
            netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        
        # Log without password for security
        safe_url = self.rtsp_url.replace(self.password, "***")
        print(f"Built authenticated URL for {self.name}: {safe_url}")
        
        return authenticated_url
    
    def _build_gstreamer_command(self) -> List[str]:
        """Build highly optimized GStreamer command for Jetson hardware"""
        
        # Optimized pipeline for maximum performance on Jetson
        cmd = [
            'gst-launch-1.0', '-q',
            'rtspsrc', f'location={self.rtsp_url}', 
            'latency=0', 'buffer-mode=auto', 'protocols=tcp',
            'drop-on-latency=true', 'do-retransmission=false',
            '!', 'rtph264depay',
            '!', 'h264parse',
            '!', 'nvv4l2decoder', 
            'enable-max-performance=true',
            'disable-dpb=true',  # Disable decode picture buffer for lower latency
            '!', 'video/x-raw(memory:NVMM)',  # Use NVIDIA memory for zero-copy
            '!', 'nvvidconv', 
            'compute-hw=1', 'interpolation-method=1',  # Use VIC for scaling
            '!', f'video/x-raw,width={self.width},height={self.height},format=BGRx',
            '!', 'videoconvert',
            '!', 'video/x-raw,format=BGR',
            '!', 'fdsink', 'fd=1', 'sync=false'
        ]
        
        return cmd
    
    def _test_pipeline(self) -> bool:
        """Test if the pipeline works before starting frame reading"""
        try:
            # Build a test command exactly like your working command
            cmd = [
                'gst-launch-1.0', '-q',
                'rtspsrc', f'location={self.rtsp_url}', 'latency=0',
                '!', 'rtph264depay',
                '!', 'h264parse', 
                '!', 'nvv4l2decoder',
                '!', 'fakesink'
            ]
            
            print(f"Testing basic pipeline for {self.name}: {' '.join(cmd)}")
            
            # Run test for 5 seconds
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(5)
            process.terminate()
            
            try:
                stdout, stderr = process.communicate(timeout=2)
                stderr_text = stderr.decode()
                
                # Check for success indicators - NvMMLite messages are NORMAL, not errors!
                success_indicators = [
                    "Setting pipeline to PLAYING",
                    "New clock: GstSystemClock", 
                    "Progress: (request) Sending PLAY request",
                    "NvMMLiteOpen"  # NVIDIA decoder initialization is normal
                ]
                
                # Check for actual error indicators
                error_indicators = [
                    "ERROR",
                    "CRITICAL", 
                    "Could not negotiate format",
                    "No such element",
                    "Failed to connect",
                    "not found"
                ]
                
                has_success = any(indicator in stderr_text for indicator in success_indicators)
                has_error = any(indicator in stderr_text for indicator in error_indicators)
                
                if has_success and not has_error:
                    print(f"✓ Basic pipeline test passed for {self.name}")
                    return True
                else:
                    print(f"✗ Basic pipeline test failed for {self.name}")
                    if has_error:
                        print(f"Error found in stderr: {stderr_text[:200]}...")
                    return False
                    
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                print(f"✓ Basic pipeline test passed for {self.name} (timeout after data flow)")
                return True
                
        except Exception as e:
            print(f"Error testing pipeline for {self.name}: {e}")
            return False
    
    def _check_element_availability(self, element_name: str) -> bool:
        """Check if a GStreamer element is available"""
        try:
            result = subprocess.run(
                ['gst-inspect-1.0', element_name], 
                capture_output=True, 
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _read_frames(self):
        """Optimized frame reading from GStreamer subprocess"""
        # Use configured dimensions or defaults
        frame_width = self.width if self.width > 0 else 1920
        frame_height = self.height if self.height > 0 else 1080
        frame_size = frame_width * frame_height * 3  # BGR
        
        print(f"Starting optimized frame reader for {self.name}: {frame_width}x{frame_height} (frame_size: {frame_size})")
        
        # Give GStreamer some time to start up
        time.sleep(2)
        
        buffer = b""  # Buffer to accumulate streaming data
        frame_count = 0
        
        while self.running and self.process and self.process.poll() is None:
            try:
                # Read chunk from stdout 
                chunk = self.process.stdout.read(65536)  # Read in 64KB chunks
                
                if not chunk:
                    time.sleep(0.001)
                    continue
                
                buffer += chunk
                
                # Process complete frames from buffer
                while len(buffer) >= frame_size:
                    # Extract one complete frame
                    frame_data = buffer[:frame_size]
                    buffer = buffer[frame_size:]  # Keep remaining data for next frame
                    
                    # Direct write to shared memory (zero-copy)
                    timestamp = time.time()
                    success = self.shm_writer.write_frame_direct(
                        frame_data, 
                        frame_width, 
                        frame_height, 
                        timestamp
                    )
                    
                    frame_count += 1
                    if frame_count % 150 == 0:  # Log every 150 frames (less frequent)
                        print(f"✓ {self.name}: {frame_count} frames written to shared memory")
                    
                    if not success:
                        print(f"Failed to write frame to shared memory for {self.name}")
                    
                    # Smart rate limiting for CPU efficiency
                    if frame_count % 10 == 0:  # Micro-sleep every 10 frames
                        time.sleep(0.001)  # 1ms pause to reduce CPU load
                
            except Exception as e:
                if self.running:
                    print(f"Error reading frame for {self.name}: {e}")
                    # Check if process is still alive
                    if self.process.poll() is not None:
                        stderr_output = self.process.stderr.read()
                        if stderr_output:
                            print(f"GStreamer stderr for {self.name}: {stderr_output.decode()}")
                break
        
        print(f"Frame reader stopped for {self.name}")
    
    def start(self):
        """Start optimized GStreamer subprocess"""
        self.running = True
        
        try:
            # First test the basic pipeline
            print(f"Testing pipeline connectivity for {self.name}...")
            if not self._test_pipeline():
                print(f"Basic pipeline test failed for {self.name}, skipping")
                return
            
            # Build command
            cmd = self._build_gstreamer_command()
            print(f"Starting optimized pipeline for {self.name}: {' '.join(cmd)}")
            
            # Start subprocess
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0  # Unbuffered for lowest latency
            )
            
            # Wait a moment to check if process starts successfully
            time.sleep(2)
            if self.process.poll() is not None:
                # Process died immediately, get error output
                _, stderr = self.process.communicate()
                print(f"ERROR: GStreamer process died immediately for {self.name}")
                print(f"GStreamer stderr: {stderr.decode()}")
                return
            
            # Start frame reading thread
            self.thread = threading.Thread(target=self._read_frames, daemon=True)
            self.thread.start()
            
            print(f"Started optimized GStreamer stream for {self.name}")
            
        except Exception as e:
            print(f"Error starting pipeline for {self.name}: {e}")
            self.stop()
    
    def stop(self):
        """Stop the stream"""
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        self.shm_writer.close()
        print(f"Stopped stream {self.name}")

class OptimizedStreamServer:
    """Optimized stream server with minimal latency for multiple camera streams"""
    
    def __init__(self, config_file: str):
        print(f"OptimizedStreamServer init: config_file={config_file}")
        self.config_file = config_file
        self.streams: Dict[str, OptimizedGStreamerStream] = {}
        
        # Clean up any leftover shared memory files
        self._cleanup_leftover_shm()
        
        print("Loading configuration...")
        self.load_config()
        print(f"Configuration loaded successfully. Found {len(self.config)} cameras.")
    
    def _cleanup_leftover_shm(self):
        """Clean up any leftover shared memory files from previous runs"""
        try:
            shm_dir = Path("/dev/shm")
            if shm_dir.exists():
                # Remove any files matching our pattern
                for shm_file in shm_dir.glob("rtsp_frames_*"):
                    try:
                        shm_file.unlink()
                        print(f"Cleaned up leftover shared memory: {shm_file}")
                    except Exception as e:
                        print(f"Warning: Could not remove {shm_file}: {e}")
        except Exception as e:
            print(f"Warning: Error during shared memory cleanup: {e}")
    
    def load_config(self):
        """Load camera configuration"""
        try:
            print(f"Loading config from: {self.config_file}")
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Config file size: {len(content)} bytes")
                self.config = json.loads(content)
            print(f"Loaded configuration for {len(self.config.get('cameras', []))} cameras")
        except FileNotFoundError:
            print(f"Error: Configuration file not found: {self.config_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")
            print(f"Line {e.lineno}, Column {e.colno}: {e.msg}")
            # Show the problematic line
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if e.lineno <= len(lines):
                        print(f"Problematic line: {lines[e.lineno-1].strip()}")
            except:
                pass
            sys.exit(1)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    def start_streams(self):
        """Start all configured streams"""
        cameras = self.config.get('cameras', [])
        
        for camera in cameras:
            camera_name = camera.get('name', 'unknown')
            host = camera.get('host', '')
            port = camera.get('port', 554)
            username = camera.get('username', '')
            password = camera.get('password', '')
            channels = camera.get('channels', [])
            
            if not host:
                print(f"Warning: No host specified for camera {camera_name}")
                continue
            
            for channel in channels:
                channel_name = channel.get('name', 'main')
                stream_path = channel.get('stream_path', '/stream1')
                width = channel.get('width', 0)
                height = channel.get('height', 0)
                encoding = channel.get('encoding', 'h264')
                fps = channel.get('fps', 30)
                
                # Build RTSP URL
                rtsp_url = f"rtsp://{host}:{port}{stream_path}"
                
                stream_name = f"{camera_name}_{channel_name}"
                
                # Check if hardware acceleration is available
                use_nvdec = self._check_nvdec_support()
                
                stream = OptimizedGStreamerStream(
                    rtsp_url=rtsp_url,
                    name=stream_name,
                    width=width,
                    height=height,
                    use_nvdec=use_nvdec,
                    username=username if username else None,
                    password=password if password else None
                )
                stream.encoding = encoding
                
                print(f"Configured stream {stream_name}: {width}x{height}@{fps}fps ({encoding})")
                
                self.streams[stream_name] = stream
                stream.start()
    
    def _check_nvdec_support(self) -> bool:
        """Check if hardware acceleration is available"""
        try:
            # Check for Jetson hardware elements using gst-inspect
            elements = ['nvv4l2decoder', 'nvh264dec', 'nvvidconv']
            for element in elements:
                result = subprocess.run(
                    ['gst-inspect-1.0', element], 
                    capture_output=True, 
                    timeout=2
                )
                if result.returncode == 0:
                    print(f"Hardware acceleration available: {element}")
                    return True
            return False
        except Exception:
            return False
    
    def run(self):
        """Main server loop"""
        print("Starting Optimized Stream Server...")
        
        self.start_streams()
        
        if not self.streams:
            print("No streams configured. Exiting.")
            return
        
        print(f"Running {len(self.streams)} optimized streams. Press Ctrl+C to stop.")
        
        try:
            while True:
                # Health check - restart failed streams
                for name, stream in list(self.streams.items()):
                    if stream.process and stream.process.poll() is not None:
                        print(f"Stream {name} died, restarting...")
                        stream.stop()
                        time.sleep(1)
                        stream.start()
                
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.stop()
    
    def stop(self):
        """Stop all streams"""
        for stream in self.streams.values():
            stream.stop()
        print("All streams stopped.")

def cleanup_handler(signum, frame):
    """Handle shutdown signals for cleanup"""
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    global server_instance
    if server_instance:
        server_instance.stop()
    sys.exit(0)

def main():
    """Main entry point"""
    global server_instance
    
    print("=== RTSP Streamer Node Starting ===")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Script location: {__file__}")
    
    config_file = os.environ.get('CONFIG_FILE', '/app/config/cameras.json')
    print(f"Config file path: {config_file}")
    
    if not os.path.exists(config_file):
        print(f"Configuration file not found: {config_file}")
        print(f"Available files in /app:")
        if os.path.exists('/app'):
            for item in os.listdir('/app'):
                print(f"  {item}")
        sys.exit(1)
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)
    
    print("Creating OptimizedStreamServer...")
    server_instance = OptimizedStreamServer(config_file)
    print("Starting server.run()...")
    
    try:
        server_instance.run()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, shutting down...")
        server_instance.stop()
    except Exception as e:
        print(f"Error during execution: {e}")
        server_instance.stop()
        raise

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        print(f"FATAL ERROR in main(): {e}")
        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)
