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
        twist = Twist()
        speed = 1.2

        # Check turbo buttons safely
        if len(msg.buttons) > 7:
            if msg.buttons[6] and msg.buttons[7]:
                speed = 3.0
            elif msg.buttons[6] or msg.buttons[7]:
                speed = 2.0
        elif len(msg.buttons) > 5:
            if msg.buttons[4] or msg.buttons[5]:
                speed = 2.0

        linear_axis = float(msg.axes[1]) if len(msg.axes) > 1 else 0.0
        angular_axis = float(msg.axes[0]) if len(msg.axes) > 0 else 0.0

        twist.linear.x = speed * linear_axis
        twist.angular.z = 1.8 * angular_axis
        self.publisher_.publish(twist)


def main():
    rclpy.init()
    rclpy.spin(JoyViewer())


if __name__ == "__main__":
    main()
