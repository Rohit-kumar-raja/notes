import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_amr = get_package_share_directory('factory_amr')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    models_dir = os.path.join(pkg_amr, 'models')
    default_world = os.path.join(pkg_amr, 'worlds', 'factory_world.sdf')
    default_urdf = os.path.join(pkg_amr, 'urdf', 'amr.urdf')
    default_map = os.path.join(pkg_amr, 'maps', 'factory_map.yaml')
    default_nav2_params = os.path.join(pkg_amr, 'config', 'nav2_params.yaml')
    default_rviz_config = os.path.join(pkg_amr, 'rviz', 'nav2.rviz')

    with open(default_urdf, 'r') as f:
        robot_desc = f.read()

    # Launch arguments
    map_arg = DeclareLaunchArgument(
        'map',
        default_value=default_map,
        description='Full path to the map YAML file to load',
    )
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
    params_file_arg = DeclareLaunchArgument(
        'params_file',
        default_value=default_nav2_params,
        description='Full path to the Nav2 parameters file',
    )
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=default_rviz_config,
        description='Full path to the RViz configuration file',
    )
    autostart_arg = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the Nav2 stack lifecycle nodes',
    )
    teleop_arg = DeclareLaunchArgument(
        'teleop',
        default_value='false',
        description='Whether to launch keyboard teleop in a separate terminal window',
    )

    # Gazebo resource paths
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

    # 1. Gazebo Sim
    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', LaunchConfiguration('world')],
        output='screen',
    )

    # 2. ROS 2 <-> Gazebo Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='amr_ros_gz_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/TwistStamped]gz.msgs.Twist',
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

    # 3. Robot State Publisher (URDF transforms)
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

    # 4. Joint State Publisher
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )

    # 5. Nav2 Bringup (Map Server + AMCL + Full Navigation Stack)
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'slam': 'False',
            'map': LaunchConfiguration('map'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'params_file': LaunchConfiguration('params_file'),
            'autostart': LaunchConfiguration('autostart'),
            'use_composition': 'False',
            'use_localization': 'True',
        }.items(),
    )

    # 6. RViz2 configured for Navigation and Localization
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_navigation',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )

    # 7. Optional Teleop Process in a new terminal window
    teleop_process = ExecuteProcess(
        cmd=['x-terminal-emulator', '-e', 'ros2', 'run', 'factory_amr', 'teleop'],
        condition=IfCondition(LaunchConfiguration('teleop')),
        output='screen',
    )

    return LaunchDescription([
        map_arg,
        world_arg,
        use_sim_time_arg,
        params_file_arg,
        rviz_config_arg,
        autostart_arg,
        teleop_arg,
        set_gz_resource_path,
        set_sdf_path,
        gz_sim,
        bridge,
        robot_state_publisher_node,
        joint_state_publisher_node,
        nav2_bringup_launch,
        rviz_node,
        teleop_process,
    ])
