import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Joy, LaserScan


class JoyViewer(Node):
    FRONT_HIT = 0.50  # m
    FRONT_WARN = 0.55  # m
    REAR_HIT = 0.45  # m
    SIDE_HIT = 0.18  # m

    def __init__(self):
        super().__init__("joy_viewer")
        self.create_subscription(Joy, "/joy", self.cb, 10)
        self.publisher_ = self.create_publisher(Twist, "cmd_vel", 10)
        self.create_subscription(
            LaserScan, "/scan", self.scan_cb, qos_profile_sensor_data
        )

        inf = float("inf")
        self.d_front = inf
        self.d_rear = inf
        self.d_left = inf
        self.d_right = inf
        self.status = "CLEAR"

    def cb(self, msg: Joy):
        twist = Twist()
        speed = 1.2

        if len(msg.buttons) > 7:
            if msg.buttons[6] and msg.buttons[7]:
                speed = 3.0
            elif msg.buttons[6] or msg.buttons[7]:
                speed = 2.0
        elif len(msg.buttons) > 5 and (msg.buttons[4] or msg.buttons[5]):
            speed = 2.0

        linear_axis = float(msg.axes[1]) if len(msg.axes) > 1 else 0.0
        angular_axis = float(msg.axes[0]) if len(msg.axes) > 0 else 0.0

        lin = speed * linear_axis
        ang = 1.8 * angular_axis

        # Direction-aware gating: block only motion TOWARD the obstacle
        if lin > 0.0:
            if self.d_front <= self.FRONT_HIT:
                lin = 0.0
            elif self.d_front <= self.FRONT_WARN:
                lin = min(lin, 0.3)  # slow down in warning zone
        elif lin < 0.0:
            if self.d_rear <= self.REAR_HIT:
                lin = 0.0

        twist.linear.x = lin
        twist.angular.z = ang

        # Always publish (zero when blocked) so the robot actually stops
        # and so reverse/turn commands go through.
        self.publisher_.publish(twist)

    def scan_cb(self, msg: LaserScan):
        front, left, right, rear = [], [], [], []

        angle = msg.angle_min
        for r in msg.ranges:
            if math.isfinite(r) and msg.range_min <= r <= msg.range_max:
                deg = math.degrees(angle)
                # normalize to [-180, 180]
                deg = (deg + 180.0) % 360.0 - 180.0
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
        self.d_front = min(front, default=inf)
        self.d_left = min(left, default=inf)
        self.d_right = min(right, default=inf)
        self.d_rear = min(rear, default=inf)

        if (
            self.d_front <= self.FRONT_HIT
            or self.d_rear <= self.REAR_HIT
            or self.d_left <= self.SIDE_HIT
            or self.d_right <= self.SIDE_HIT
        ):
            self.status = "HIT"
        elif self.d_front <= self.FRONT_WARN:
            self.status = "WARNING"
        else:
            self.status = "CLEAR"


def main():
    rclpy.init()
    rclpy.spin(JoyViewer())


if __name__ == "__main__":
    main()