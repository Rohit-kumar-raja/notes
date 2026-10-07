import random

import rclpy
from example_interfaces.msg import Int64
from rclpy.node import Node


class SentSensorNode(Node):
    def __init__(self):
        super().__init__("sensor_sender_node")
        self._publisher = self.create_publisher(Int64, "sensor_data", 10)
        self.create_timer(0.1, self.data_publisher)

    def data_publisher(self):
        msg = Int64()
        msg.data = random.randint(1, 100)
        self._publisher.publish(msg)


def main():
    rclpy.init()
    try:
        node = SentSensorNode()
        rclpy.spin(node)
    except Exception as e:
        node.get_logger().error(str(e))

    finally:
        rclpy.shutdown()
