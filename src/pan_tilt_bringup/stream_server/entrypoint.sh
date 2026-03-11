#!/bin/bash
set -e

echo "=== Stream Server Starting ==="

# Check for NVIDIA hardware
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA runtime detected"
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader || echo "Warning: nvidia-smi failed"
else
    echo "Warning: NVIDIA runtime not available"
fi

# Check GStreamer hardware elements
echo "Checking GStreamer hardware elements..."
if gst-inspect-1.0 nvv4l2decoder &>/dev/null; then
    echo "✓ nvv4l2decoder available (Jetson hardware decoder)"
else
    echo "✗ nvv4l2decoder not found"
fi

if gst-inspect-1.0 nvh264dec &>/dev/null; then
    echo "✓ nvh264dec available"
else
    echo "✗ nvh264dec not found"
fi

if gst-inspect-1.0 nvvidconv &>/dev/null; then
    echo "✓ nvvidconv available (hardware video converter)"
else
    echo "✗ nvvidconv not found"
fi

# Check shared memory directory
mkdir -p /dev/shm
echo "Shared memory directory: /dev/shm"

# Check if config file exists
if [ -f "/app/config/cameras.json" ]; then
    echo "✓ Config file found: /app/config/cameras.json"
else
    echo "✗ Config file missing: /app/config/cameras.json"
fi

echo "Starting main application..."

# Debug: Show what command will be executed
echo "Command to execute: $@"
echo "First argument: $1"
echo "All arguments: $*"

# Test if Python script exists and is executable
if [ -f "/app/rtsp_streamer_node.py" ]; then
    echo "✓ Python script found: /app/rtsp_streamer_node.py"
    echo "File permissions:"
    ls -la /app/rtsp_streamer_node.py
else
    echo "✗ Python script NOT found: /app/rtsp_streamer_node.py"
fi

# Test Python directly
echo "Testing Python:"
python3 --version
which python3

# Execute main command with error handling and output
echo "Executing: $@"

# Set Python unbuffered output
export PYTHONUNBUFFERED=1

# Try to run the command and capture any errors
if ! "$@"; then
    echo "ERROR: Command failed with exit code $?"
    echo "Trying to run with explicit error output..."
    python3 -u rtsp_streamer_node.py 2>&1 || {
        echo "Python script failed. Checking for syntax errors..."
        python3 -m py_compile rtsp_streamer_node.py
        echo "Trying to import the module..."
        python3 -c "import rtsp_streamer_node" 2>&1
    }
    exit 1
fi
