import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_amr = get_package_share_directory("amr")
    pkg_nav2_bringup = get_package_share_directory("nav2_bringup")

    default_map_file = os.path.join(pkg_amr, "maps", "factory_map.yaml")
    default_nav2_params = os.path.join(pkg_amr, "config", "nav2_params.yaml")
    default_rviz_config = os.path.join(pkg_amr, "rviz", "nav2.rviz")

    # Launch arguments
    declare_map = DeclareLaunchArgument(
        "map",
        default_value=default_map_file,
        description="Full path to the map YAML file to load",
    )
    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation (Gazebo) clock if true",
    )
    declare_params_file = DeclareLaunchArgument(
        "params_file",
        default_value=default_nav2_params,
        description="Full path to the Nav2 parameters file",
    )
    declare_rviz_config = DeclareLaunchArgument(
        "rviz_config",
        default_value=default_rviz_config,
        description="Full path to the RViz configuration file",
    )
    declare_start_sim = DeclareLaunchArgument(
        "start_sim",
        default_value="true",
        description="Whether to launch Gazebo simulation and robot bridge",
    )
    declare_navigation = DeclareLaunchArgument(
        "navigation",
        default_value="true",
        description="Whether to launch full Nav2 navigation stack with localization",
    )
    declare_autostart = DeclareLaunchArgument(
        "autostart",
        default_value="true",
        description="Automatically startup the Nav2 stack lifecycle nodes",
    )

    # 1. Include robot launch (Gazebo + Bridges + Robot State Publisher)
    robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_amr, "launch", "robot.launch.py")
        ),
        condition=IfCondition(LaunchConfiguration("start_sim")),
        launch_arguments={
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "use_rviz": "false",
        }.items(),
    )

    # 2. Nav2 Localization (Map Server + AMCL)
    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, "launch", "localization_launch.py")
        ),
        launch_arguments={
            "map": LaunchConfiguration("map"),
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "params_file": LaunchConfiguration("params_file"),
            "autostart": LaunchConfiguration("autostart"),
            "use_composition": "false",
        }.items(),
    )

    # 3. Nav2 Navigation Stack (Planner, Controller, Recoveries)
    navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, "launch", "navigation_launch.py")
        ),
        condition=IfCondition(LaunchConfiguration("navigation")),
        launch_arguments={
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "params_file": LaunchConfiguration("params_file"),
            "autostart": LaunchConfiguration("autostart"),
            "use_composition": "false",
        }.items(),
    )

    # 4. RViz2 visualization with Navigation 2 panels and tools
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2_navigation",
        output="screen",
        arguments=["-d", LaunchConfiguration("rviz_config")],
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
    )

    return LaunchDescription([
        declare_map,
        declare_use_sim_time,
        declare_params_file,
        declare_rviz_config,
        declare_start_sim,
        declare_navigation,
        declare_autostart,
        robot_launch,
        localization_launch,
        navigation_launch,
        rviz_node,
    ])
