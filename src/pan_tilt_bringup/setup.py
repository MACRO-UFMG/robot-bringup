from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'rtsp_cam'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your-email@example.com',
    description='High-performance RTSP camera streamer with hardware acceleration for Jetson platforms',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'rtsp_publisher_node = rtsp_cam.rtsp_publisher_node:main',
        ],
    },
)
