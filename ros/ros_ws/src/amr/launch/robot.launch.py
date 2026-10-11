import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_amr = get_package_share_directory("amr")
    models_dir = os.path.join(pkg_amr, "models")
    default_world = os.path.join(pkg_amr, "worlds", "factory_world.sdf")
    rviz_config = os.path.join(pkg_amr, "rviz", "amr_view.rviz")

    # Launch arguments
    world_arg = DeclareLaunchArgument(
        "world",
        default_value=default_world,
        description="Path to the SDF world file to load",
    )
    rviz_arg = DeclareLaunchArgument(
        "use_rviz",
        default_value="false",
        description="Whether to start RViz2 for sensor visualization",
    )
    joy_arg = DeclareLaunchArgument(
        "use_joystick",
        default_value="true",
        description="Whether to start joystick teleoperation nodes",
    )

    # Ensure Gazebo and SDFormat can find the custom amr_robot and factory models
    existing_gz_path = os.environ.get("GZ_SIM_RESOURCE_PATH", "")
    new_gz_path = f"{models_dir}:{existing_gz_path}" if existing_gz_path else models_dir
    set_gz_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=new_gz_path,
    )

    existing_sdf_path = os.environ.get("SDF_PATH", "")
    new_sdf_path = f"{models_dir}:{existing_sdf_path}" if existing_sdf_path else models_dir
    set_sdf_path = SetEnvironmentVariable(
        name="SDF_PATH",
        value=new_sdf_path,
    )

    # Gazebo Sim runner
    gz_sim = ExecuteProcess(
        cmd=["gz", "sim", "-r", LaunchConfiguration("world")],
        output="screen",
    )

    # ROS 2 <-> Gazebo Bridge for AMR Control and Sensors
    # 1. /cmd_vel -> Robot drive command (ROS 2 -> Gazebo)
    # 2. /odom    <- Robot wheel odometry (Gazebo -> ROS 2)
    # 3. /scan    <- 2D LiDAR scan data (Gazebo -> ROS 2)
    # 4. /camera/image_raw  <- Forward Camera RGB stream (Gazebo -> ROS 2)
    # 5. /camera/camera_info <- Camera calibration info (Gazebo -> ROS 2)
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="amr_ros_gz_bridge",
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image",
            "/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
        ],
        output="screen",
    )

    # Joystick Nodes
    joy_node = Node(
        package="joy",
        executable="joy_node",
        name="joy_node",
        condition=IfCondition(LaunchConfiguration("use_joystick")),
        output="screen",
    )

    joy_viewer_node = Node(
        package="amr",
        executable="joy_viewer",
        name="joy_viewer",
        condition=IfCondition(LaunchConfiguration("use_joystick")),
        output="screen",
    )

    # RViz2 Node
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config],
        condition=IfCondition(LaunchConfiguration("use_rviz")),
        output="screen",
    )

    return LaunchDescription([
        world_arg,
        rviz_arg,
        joy_arg,
        set_gz_resource_path,
        set_sdf_path,
        gz_sim,
        bridge,
        joy_node,
        joy_viewer_node,
        rviz_node,
    ])
