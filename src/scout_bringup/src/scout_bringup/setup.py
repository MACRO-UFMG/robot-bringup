from setuptools import find_packages, setup
import os

package_name = 'scout_bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(
        # include=[],
        exclude=['test']
        ),
    data_files=[
        (os.path.join('share', 'ament_index', 'resource_index', 'packages'),
            [os.path.join('resource', package_name)]),
        (os.path.join('share', package_name), ['package.xml']),
        (os.path.join('share', package_name, 'launch'), 
            [
                os.path.join('launch', 'start_scout.launch.py'),
                os.path.join('launch', 'rmf_demo.launch.py')
                ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'target_transform = scout_bringup.target_transform:main',
            'pose_transform = scout_bringup.pose_transform:main',
        ],
    },
)
