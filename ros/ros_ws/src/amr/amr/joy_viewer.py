import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Joy, LaserScan
from std_msgs.msg import String


class JoyViewer(Node):
    FRONT_HIT = 0.20  # m, from LiDAR
    FRONT_WARN = 0.55  # m
    REAR_HIT = 0.35  # m
    SIDE_HIT = 0.18  # m
    status = ""

    def __init__(self):
        super().__init__("joy_viewer")
        self.create_subscription(Joy, "/joy", self.cb, 10)
        self.publisher_ = self.create_publisher(Twist, "cmd_vel", 10)

        self.create_subscription(
            LaserScan, "/scan", self.scan_cb, qos_profile_sensor_data
        )
        self.actual_speed = 0.0
        self.cmd_speed = 0.0

    def collision_status(self, msg: String):
        self.last_status = msg.data

    def cb(self, msg: Joy):
        twist = Twist()
        speed = 1.2

        # Check turbo buttons safely
        if len(msg.buttons) > 7:
            if msg.buttons[6] and msg.buttons[7]:
                speed = 3.0
            elif msg.buttons[6] or msg.buttons[7]:
                speed = 2.0
        elif len(msg.buttons) > 5 and (msg.buttons[4] or msg.buttons[5]):
            speed = 2.0

        linear_axis = float(msg.axes[1]) if len(msg.axes) > 1 else 0.0
        angular_axis = float(msg.axes[0]) if len(msg.axes) > 0 else 0.0

        twist.linear.x = speed * linear_axis
        twist.angular.z = 1.8 * angular_axis
        
        if self.status!="HIT":
            self.publisher_.publish(twist)

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
            self.status = "HIT"
        elif d_front <= self.FRONT_WARN:
            self.status = "WARNING"
        else:
            self.status = "CLEAR"

        # self.get_logger().info(f"Status: {self.status}")


def main():
    rclpy.init()
    rclpy.spin(JoyViewer())


if __name__ == "__main__":
    main()
