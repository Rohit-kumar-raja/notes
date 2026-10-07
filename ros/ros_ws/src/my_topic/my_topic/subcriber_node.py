import rclpy
from example_interfaces.msg import String
from rclpy.node import Node


class SubscriberNode(Node):
    def __init__(self):
        super().__init__("publisher_node")
        self.subscription_ = self.create_subscription(
            String, "sensor_data_topic", self.sent_message, 10
        )

    def sent_message(self, data):
        self.get_logger().info(str(data))


def main():
    rclpy.init()
    try:
        node = SubscriberNode()
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    except Exception as e:
        print("somthing is wrong " + str(e))

    finally:
        rclpy.shutdown()
