from setuptools import setup
import os
from glob import glob

package_name = 'nav2_namespace_bringup'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        # Index do pacote
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        # Manifesto do pacote
        ('share/' + package_name, ['package.xml']),

        # Pasta de launch files
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ros',
    maintainer_email='ros@example.com',
    description='Bringup do Nav2 com namespace',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)
