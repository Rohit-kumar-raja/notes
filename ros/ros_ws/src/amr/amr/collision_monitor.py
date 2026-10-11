import math

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String


class CollisionMonitor(Node):
    """Publishes AMR status on /collision_status: CLEAR, WARNING or HIT."""

    FRONT_HIT = 0.20  # m, from LiDAR
    FRONT_WARN = 0.55  # m
    REAR_HIT = 0.35  # m
    SIDE_HIT = 0.18  # m

    def __init__(self):
        super().__init__("collision_monitor")

        self.create_subscription(
            LaserScan, "/scan", self.scan_cb, qos_profile_sensor_data
        )
        self.create_subscription(Odometry, "/odom", self.odom_cb, 10)
        self.create_subscription(Twist, "/cmd_vel", self.cmd_vel_cb, 10)

        self.status_pub = self.create_publisher(String, "/collision_status", 10)

        self.actual_speed = 0.0
        self.cmd_speed = 0.0
        self.last_status = None

    def scan_cb(self, msg: LaserScan):
        front, left, right, rear = [], [], [], []

        angle = msg.angle_min
        for r in msg.ranges:
            if math.isfinite(r) and msg.range_min <= r <= msg.range_max:
                deg = math.degrees(angle)
                if -45.0 <= deg <= 45.0:
                    front.append(r)
                elif 45.0 < deg < 135.0:
                    left.append(r)
                elif -135.0 < deg < -45.0:
                    right.append(r)
                else:
                    rear.append(r)
            angle += msg.angle_increment

        inf = float("inf")
        d_front = min(front, default=inf)
        d_left = min(left, default=inf)
        d_right = min(right, default=inf)
        d_rear = min(rear, default=inf)

        # Motor stall: commanded to move but not moving, with obstacle ahead
        stall = (
            abs(self.cmd_speed) > 0.3
            and abs(self.actual_speed) < 0.05
            and d_front < self.FRONT_WARN
        )

        if (
            d_front <= self.FRONT_HIT
            or d_rear <= self.REAR_HIT
            or d_left <= self.SIDE_HIT
            or d_right <= self.SIDE_HIT
            or stall
        ):
            status = "HIT"
        elif d_front <= self.FRONT_WARN:
            status = "WARNING"
        else:
            status = "CLEAR"

        self.status_pub.publish(String(data=status))

        if status != self.last_status:
            self.get_logger().info(f"Status: {status}")
            self.last_status = status

    def odom_cb(self, msg: Odometry):
        self.actual_speed = float(msg.twist.twist.linear.x)

    def cmd_vel_cb(self, msg: Twist):
        self.cmd_speed = float(msg.linear.x)


def main(args=None):
    rclpy.init(args=args)
    node = CollisionMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
