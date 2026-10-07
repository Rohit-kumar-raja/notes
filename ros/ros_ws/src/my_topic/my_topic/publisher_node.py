import rclpy
from example_interfaces.msg import String
from rclpy.node import Node


class PublisherNode(Node):
    def __init__(self):
        super().__init__("publisher_node")
        self.publisher_ = self.create_publisher(String, "sensor_data_topic", 10)
        self.timer_ = self.create_timer(0.1, self.sent_message)

    def sent_message(self):
        msg = String()
        msg.data = "hello come from the Publisher node "
        self.publisher_.publish(msg)


def main():
    rclpy.init()
    try:
        node = PublisherNode()
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    except Exception as e:
        print("somthing is wrong " + str(e))

    finally:
        rclpy.shutdown()


