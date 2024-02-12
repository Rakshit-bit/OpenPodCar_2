import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    # Get the launch directory
    bringup_dir = get_package_share_directory('pod2_navigation')
    # nav2_params_path = os.path.join(
    #     get_package_share_directory('pod2_navigation'),
    #     'config/',
    #     'nav2_params.yaml')


    namespace = LaunchConfiguration('namespace')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    params_file = LaunchConfiguration('params_file')
    default_nav_to_pose_bt_xml = LaunchConfiguration('default_nav_to_pose_bt_xml')
    map_subscribe_transient_local = LaunchConfiguration('map_subscribe_transient_local')

    lifecycle_nodes = ['controller_server',
                       'planner_server',
                       'behavior_server',
                       'bt_navigator']

    # Map fully qualified names to relative ones so the node's namespace can be prepended.
    # In case of the transforms (tf), currently, there doesn't seem to be a better alternative
    # https://github.com/ros/geometry2/issues/32
    # https://github.com/ros/robot_state_publisher/pull/30
    # TODO(orduno) Substitute with `PushNodeRemapping`
    #              https://github.com/ros2/launch_ros/issues/56
    # remappings = [('/tf', 'tf'),
                #   ('/tf_static', 'tf_static')]

    # Create our own temporary YAML files that include substitutions
    param_substitutions = {
        'use_sim_time': use_sim_time,
        'autostart': autostart,
        # 'default_nav_to_pose_bt_xml': default_nav_to_pose_bt_xml,
        # 'map_subscribe_transient_local': map_subscribe_transient_local
        }

    configured_params = RewrittenYaml(
            source_file=params_file,
            root_key=namespace,
            param_rewrites=param_substitutions,
            convert_types=True)

    return LaunchDescription([
        # Set env var to print messages to stdout immediately
        SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1'),

        DeclareLaunchArgument(
            'namespace', default_value='',
            description='Top-level namespace'),

        DeclareLaunchArgument(
            'use_sim_time', default_value='false',
            description='Use simulation (Gazebo) clock if true'),

        DeclareLaunchArgument(
            'autostart', default_value='true',
            description='Automatically startup the nav2 stack'),

        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(bringup_dir, 'config', 'nav2_params.yaml'),
            description='Full path to the ROS2 parameters file to use'),

        # DeclareLaunchArgument(
        #     'default_nav_to_pose_bt_xml',
        #     default_value=os.path.join(bringup_dir, 'behavior_trees', 'default.xml'),
        #     description='Full path to the behavior tree xml file to use'),

        DeclareLaunchArgument(
            'map_subscribe_transient_local', default_value='true',
            description='Whether to set the map subscriber QoS to transient local'),

        Node(
            package='nav2_controller',
            executable='controller_server',
            prefix=['xterm -e gdb -ex run --args'],
            output='screen',
            parameters=[configured_params],
            # remappings=remappings
            ),

        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            prefix=['xterm -e gdb -ex run --args'],
            output='screen',
            parameters=[configured_params],
            # remappings=remappings
            ),

        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            prefix=['xterm -e gdb -ex run --args'],
            output='screen',
            parameters=[configured_params],
            # remappings=remappings
            ),

        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            prefix=['xterm -e gdb -ex run --args'],
            output='screen',
            parameters=[configured_params],
            # remappings=remappings
            ),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            prefix=['xterm -e gdb -ex run --args'],
            output='screen',
            parameters=[{'use_sim_time': use_sim_time},
                        {'autostart': autostart},
                        {'node_names': lifecycle_nodes}]),

       
    ])