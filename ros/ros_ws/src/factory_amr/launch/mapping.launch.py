import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_amr = get_package_share_directory('factory_amr')
    models_dir = os.path.join(pkg_amr, 'models')
    default_world = os.path.join(pkg_amr, 'worlds', 'factory_world.sdf')
    default_urdf = os.path.join(pkg_amr, 'urdf', 'amr.urdf')
    default_slam_params = os.path.join(pkg_amr, 'config', 'slam_toolbox_params.yaml')
    default_rviz_config = os.path.join(pkg_amr, 'rviz', 'slam.rviz')

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
    params_file_arg = DeclareLaunchArgument(
        'params_file',
        default_value=default_slam_params,
        description='Full path to the slam_toolbox parameters file',
    )
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=default_rviz_config,
        description='Full path to the RViz configuration file',
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

    # 5. SLAM Toolbox (Online Async)
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            LaunchConfiguration('params_file'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
    )

    # 6. RViz2 configured for SLAM mapping
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_mapping',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )

    return LaunchDescription([
        world_arg,
        use_sim_time_arg,
        params_file_arg,
        rviz_config_arg,
        set_gz_resource_path,
        set_sdf_path,
        gz_sim,
        bridge,
        robot_state_publisher_node,
        joint_state_publisher_node,
        slam_toolbox_node,
        rviz_node,
    ])
