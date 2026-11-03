import select
import sys
import termios
import tty

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node

USAGE = """
===================================================================
                  FACTORY AMR KEYBOARD TELEOP
===================================================================
Moving around:
        [w] or [Up]
   [a]     [s]     [d]       or   [Left]  [Down]  [Right]
         [Down]

  w / Up    : Forward
  s / Down  : Backward
  a / Left  : Turn Left
  d / Right : Turn Right
  q         : Forward + Left
  e         : Forward + Right
  z         : Backward + Left
  c         : Backward + Right
  SPACE / x : Force Stop (Zero velocity)

Speed tuning:
  + / =     : Increase speed by 10%
  - / _     : Decrease speed by 10%

Press Ctrl+C to exit.
===================================================================
"""


class AMRTeleop(Node):

    def __init__(self):
        super().__init__('amr_teleop')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.speed = 0.5  # m/s
        self.turn = 1.0   # rad/s
        self.x = 0.0
        self.th = 0.0

    def publish_twist(self, linear, angular):
        twist = Twist()
        twist.linear.x = float(linear)
        twist.angular.z = float(angular)
        self.publisher.publish(twist)

    def stop(self):
        self.publish_twist(0.0, 0.0)


def get_key(settings, timeout=0.1):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if rlist:
        key = sys.stdin.read(1)
        # Check for multi-byte escape sequences (arrow keys)
        if key == '\x1b':
            extra = sys.stdin.read(2)
            key += extra
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def main():
    settings = termios.tcgetattr(sys.stdin)
    rclpy.init()
    node = AMRTeleop()

    print(USAGE)

    speed = 0.5
    turn = 1.0
    x = 0.0
    th = 0.0

    key_bindings = {
        'w': (1.0, 0.0),
        '\x1b[A': (1.0, 0.0),   # Up Arrow
        's': (-1.0, 0.0),
        '\x1b[B': (-1.0, 0.0),  # Down Arrow
        'a': (0.0, 1.0),
        '\x1b[D': (0.0, 1.0),   # Left Arrow
        'd': (0.0, -1.0),
        '\x1b[C': (0.0, -1.0),  # Right Arrow
        'q': (1.0, 1.0),
        'e': (1.0, -1.0),
        'z': (-1.0, 1.0),
        'c': (-1.0, -1.0),
    }

    try:
        while rclpy.ok():
            key = get_key(settings, timeout=0.08)

            if key in key_bindings:
                target_x, target_th = key_bindings[key]
                x = target_x * speed
                th = target_th * turn
                node.publish_twist(x, th)
                print(f'\rMoving: linear={x:.2f} m/s, angular={th:.2f} rad/s    ', end='')
            elif key in (' ', 'x'):
                x = 0.0
                th = 0.0
                node.stop()
                print('\rSTOPPED: linear=0.00 m/s, angular=0.00 rad/s           ', end='')
            elif key in ('+', '='):
                speed = min(1.5, speed * 1.1)
                turn = min(3.0, turn * 1.1)
                print(f'\rSpeed up: linear={speed:.2f} m/s, angular={turn:.2f} rad/s', end='')
            elif key in ('-', '_'):
                speed = max(0.1, speed * 0.9)
                turn = max(0.2, turn * 0.9)
                print(f'\rSlow down: linear={speed:.2f} m/s, angular={turn:.2f} rad/s', end='')
            elif key == '\x03':  # Ctrl+C
                break

    except Exception as e:
        print(f'\nTeleop error: {e}')
    finally:
        node.stop()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()
        print('\nTeleop exited. Robot safely stopped.')


if __name__ == '__main__':
    main()
