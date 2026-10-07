import rclpy
from example_interfaces.msg import Bool, Int64
from rclpy.node import Node


class SentSensorNode(Node):
    def __init__(self):
        super().__init__("sensor_reciever_node")
        self._subscription = self.create_subscription(
            Int64, "sensor_data", self.data_reciever, 10
        )
        self._publisher = self.create_publisher(Bool, "is_machine_on", 10)

    def data_reciever(self, msg: Int64):
        self.get_logger().info(f"current data {msg.data}")
        is_machine_on = Bool()
        if msg.data >= 0:
            is_machine_on.data = True
        else:
            is_machine_on.data = False
        self._publisher.publish(is_machine_on)


def main():
    rclpy.init()
    try:
        node = SentSensorNode()
        rclpy.spin(node)
    except Exception as e:
        node.get_logger().error(str(e))

    finally:
        rclpy.shutdown()
