from time import sleep

import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool


class Ros2ServerNode(Node):
    def __init__(self):
        super().__init__("service_server")
        self.service_client_ = self.create_client(SetBool, "service_server")
        self.get_logger().info("servie is started successfully")

    def service_request(self, data: bool):

        if not self.service_client_.wait_for_service(1):
            self.get_logger().info("we are waiting for service up")

        request = SetBool.Request()
        request.data = True

        feture = self.service_client_.call_async(request)
        rclpy.spin_until_future_complete(self, feture)
        result = feture.result()

        self.get_logger().info(str(result))


def main():
    rclpy.init()

    # try:
    node = Ros2ServerNode()
    node.service_request(True)
    # except KeyboardInterrupt:
    #     pass

    # except Exception as e:
    #     print("somgthing is errorced")
    # finally:
    rclpy.shutdown()
