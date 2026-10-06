import rclpy
from rclpy.node import Node


class TimerNode(Node):
    def __init__(self):
        super().__init__("timer_node")
        self.create_timer(0.0, self.timer_callback)

    def timer_callback(self):
        self.get_logger().info("timer is running")


def main():
    rclpy.init()
    node = TimerNode()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
