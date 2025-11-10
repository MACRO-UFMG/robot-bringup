import rclpy
from rclpy.node import Node

def main():
    rclpy.init()
    # Namespace fixo aqui
    node = Node('meu_no', namespace='robot1')
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
