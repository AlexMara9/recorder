from enum import IntEnum
from std_msgs.msg import Int8
from rclpy.node import Node
import rclpy
import yaml


class AsState(IntEnum):
    IDLE = 0
    CHECKING = 1
    READY = 2
    DRIVE = 3
    FINISH = 4
    ERROR = 5

class TulNode(Node):
    def __init__(self):
        super().__init__('tul_node')
        
        # ====== params ======
        self.declare_parameter('config_path', '')
        config_path = self.get_parameter('config_path').get_parameter_value().string_value
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)['tul']
        self._state_topic: str = config['as_state_topic']
        self._modules_config: list[dict] = config.get('modules', [])
        self.get_logger().info(f"Loaded config: {config}")
        
        # ====== config ======
        self._as_subscriber = self.create_subscription(Int8, self._state_topic, self.state_callback, 1)

        # ====== var ======
        self._current_state = AsState.IDLE

    def state_callback(self, msg: Int8) -> None:
        try:
            new_state = AsState(msg.data)
        except ValueError:
            self.get_logger().warn(f"Unknown state value: {msg.data}")
            return
        
        if self._current_state == new_state:
            return    
        
        self._current_state = new_state
        self.get_logger().info(f"Received state: {self._current_state}")

        for module in self._modules_config:
            self.get_logger().info(f"Notifying module: {module['name']} of state change to {self._current_state}")
            try:
                module.on_state_change(self._current_state)
            except Exception as e:
                # self.get_logger().error(f"Error occurred while notifying module: {module['name']} - {e}")
                pass

    def destroy_node(self):
        for module in self._modules_config:
            try:
                module.shutdown()
            except Exception as e:
                # self.get_logger().error(f"Error occurred while shutting down module: {module['name']} - {e}")
                pass
        super().destroy_node()

def main():
    rclpy.init()
    node = TulNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
