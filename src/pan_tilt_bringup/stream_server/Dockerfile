# Stream Server - L4T 36+ with GStreamer hardware acceleration
FROM nvcr.io/nvidia/l4t-jetpack:r36.4.0

# Use packages already available in L4T (no pip install needed)
# L4T already includes: python3, numpy, gstreamer1.0-tools

# Create working directory
WORKDIR /app

# Copy stream server code and config
COPY scripts/rtsp_streamer_node.py /app/
COPY stream_server/entrypoint.sh /app/
COPY config/ /app/config/
# COPY test_imports.py /app/
RUN chmod +x /app/entrypoint.sh /app/rtsp_streamer_node.py

# Set environment for hardware acceleration
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=all
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python3", "-u", "rtsp_streamer_node.py"]
