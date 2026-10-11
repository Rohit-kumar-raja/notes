import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import Joy


class JoyViewer(Node):
    def __init__(self):
        super().__init__("joy_viewer")
        self.create_subscription(Joy, "/joy", self.cb, 10)
        self.publisher_ = self.create_publisher(Twist, "cmd_vel", 10)

    def cb(self, msg: Joy):
        self.get_logger().info(f"msg {msg.buttons}")
        twist = Twist()
        speed = 1.2

        if msg.buttons[6] or msg.buttons[7]:
            speed = 4.0
        if msg.buttons[6] and msg.buttons[7]:
            speed = 8.0

        twist.linear.x = speed * float(
            msg.axes[1]
        )  # left stick up/down -> forward/back
        twist.angular.z = msg.axes[0]  # left stick left/right -> turn
        self.publisher_.publish(twist)


def main():
    rclpy.init()
    rclpy.spin(JoyViewer())


if __name__ == "__main__":
    main()
