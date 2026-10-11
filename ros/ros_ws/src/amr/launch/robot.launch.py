import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    # world file sits next to this launch file
    world = os.path.join(
        get_package_share_directory("turttlesim_gz"), "worlds", "turtle_world.sdf"
    )

    # start Gazebo with the world (-r = run immediately)
    gz_sim = ExecuteProcess(cmd=["gz", "sim", "-r", world], output="screen")

    joy_stick_node = Node(package="joy", executable="joy_node")
    node = Node(package="turttlesim_gz", executable="joystick_node")

    # bridge ROS 2 <-> Gazebo topics
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
            "/model/turtle/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry",
        ],
        output="screen",
    )

    return LaunchDescription([gz_sim,bridge, node, joy_stick_node, ])
