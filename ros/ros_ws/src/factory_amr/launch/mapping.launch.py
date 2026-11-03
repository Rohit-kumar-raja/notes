import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_amr = get_package_share_directory('factory_amr')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    default_params = os.path.join(pkg_amr, 'config', 'slam_toolbox_params.yaml')
    default_nav2_params = os.path.join(pkg_amr, 'config', 'nav2_params.yaml')
    default_rviz_config = os.path.join(pkg_amr, 'rviz', 'slam.rviz')

    # Launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true',
    )
    declare_slam_params = DeclareLaunchArgument(
        'params_file',
        default_value=default_params,
        description='Full path to the slam_toolbox parameters file',
    )
    declare_rviz_config = DeclareLaunchArgument(
        'rviz_config',
        default_value=default_rviz_config,
        description='Full path to the RViz configuration file',
    )
    declare_start_sim = DeclareLaunchArgument(
        'start_sim',
        default_value='true',
        description='Whether to launch Gazebo simulation and robot bridge',
    )
    declare_use_nav = DeclareLaunchArgument(
        'use_nav',
        default_value='true',
        description='Whether to launch Nav2 navigation stack during mapping',
    )

    # 1. Include robot launch (Gazebo + Bridges + Robot State Publisher)
    robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_amr, 'launch', 'robot.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('start_sim')),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'use_rviz': 'false',
        }.items(),
    )

    # 2. SLAM Toolbox Online Async Node
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

    # 3. Nav2 Navigation Stack (Planner, Controller, Recovery) for goal-directed mapping
    navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('use_nav')),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'params_file': default_nav2_params,
            'autostart': 'true',
            'use_composition': 'false',
        }.items(),
    )

    # 4. RViz2 visualization configured for SLAM and full control
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_mapping',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_slam_params,
        declare_rviz_config,
        declare_start_sim,
        declare_use_nav,
        robot_launch,
        slam_toolbox_node,
        navigation_launch,
        rviz_node,
    ])
