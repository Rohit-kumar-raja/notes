import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool


class Ros2ServerNode(Node):
    def __init__(self):
        super().__init__("service_servier")
        self.service_server_ = self.create_service(
            SetBool, "service_server", self.service_callback
        )
        self.get_logger().info("servie is started successfully")

    def service_callback(self, request: SetBool.Request, response: SetBool.Response):
        self.get_logger().info(str(request.data))
        response.success=False
        response.message="data succesfully set"
        return response


def main():
    rclpy.init()

    # try:
    node = Ros2ServerNode()
    rclpy.spin(node)
    # except KeyboardInterrupt:
    #     pass

    # except Exception as e:
    #     print("somgthing is errorced")
    # finally:
    rclpy.shutdown()
