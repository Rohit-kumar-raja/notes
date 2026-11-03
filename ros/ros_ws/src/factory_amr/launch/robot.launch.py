import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_amr = get_package_share_directory('factory_amr')
    models_dir = os.path.join(pkg_amr, 'models')
    default_world = os.path.join(pkg_amr, 'worlds', 'factory_world.sdf')
    default_urdf = os.path.join(pkg_amr, 'urdf', 'amr.urdf')

    # Read URDF description
    with open(default_urdf, 'r') as f:
        robot_desc = f.read()

    # Launch arguments
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Path to the SDF world file to load',
    )
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true',
    )
    rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='false',
        description='Whether to start RViz',
    )

    # Ensure Gazebo and SDFormat can find the custom amr_robot and factory models
    existing_gz_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    new_gz_path = f'{models_dir}:{existing_gz_path}' if existing_gz_path else models_dir
    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=new_gz_path,
    )

    existing_sdf_path = os.environ.get('SDF_PATH', '')
    new_sdf_path = f'{models_dir}:{existing_sdf_path}' if existing_sdf_path else models_dir
    set_sdf_path = SetEnvironmentVariable(
        name='SDF_PATH',
        value=new_sdf_path,
    )

    # Gazebo Sim runner
    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', LaunchConfiguration('world')],
        output='screen',
    )

    # ROS 2 <-> Gazebo Bridge for AMR Control, Sensors, Clock, and TF
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='amr_ros_gz_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen',
    )

    # Robot State Publisher (publishes transforms from URDF)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'robot_description': robot_desc,
        }],
    )

    # Joint State Publisher (publishes wheel joint states for complete TF tree)
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )

    # Optional basic RViz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        condition=IfCondition(LaunchConfiguration('use_rviz')),
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )

    return LaunchDescription([
        world_arg,
        use_sim_time_arg,
        rviz_arg,
        set_gz_resource_path,
        set_sdf_path,
        gz_sim,
        bridge,
        robot_state_publisher_node,
        joint_state_publisher_node,
        rviz_node,
    ])
