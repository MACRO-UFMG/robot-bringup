#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import numpy as np
from scipy.spatial.transform import Rotation

class PoseTransformer(Node):
    """
    Nó ROS2 que assina a um tópico de PoseStamped, aplica uma transformação rígida
    e publica o resultado em outro tópico de PoseStamped.
    """
    def __init__(self):
        super().__init__('target_transform_node')

        # Definição da matriz de transformação rígida 4x4
        self.T = np.array([
            [0.0, -1.0,  0.0, 66.5882],
            [1.0,  0.0,  0.0,-19.5770],
            [0.0,  0.0,  1.0,  0.0     ],
            [0.0,  0.0,  0.0,  1.0     ]
        ])

        self.T_inv = np.linalg.inv(self.T)

        # Extrai a matriz de rotação (R) e o vetor de translação (p)
        self.R = self.T_inv[0:3, 0:3]
        self.p = self.T_inv[0:3, 3]

        # Converte a matriz de rotação para um objeto Rotation da biblioteca scipy
        # para facilitar as operações de rotação.
        self.transform_rotation = Rotation.from_matrix(self.R)

        # Cria o subscriber para o tópico /target_pose
        self.subscription = self.create_subscription(
            PoseStamped,
            '/target_pose',
            self.pose_callback,
            10)
        self.get_logger().info('Nó "pose_transformer_node" iniciado.')
        self.get_logger().info('Aguardando mensagens no tópico "/target_pose"...')

        # Cria o publisher para o tópico /converted_target_pose
        self.publisher = self.create_publisher(
            PoseStamped,
            '/converted_target_pose',
            10)

    def pose_callback(self, msg: PoseStamped):
        """
        Callback executado sempre que uma mensagem é recebida em /target_pose.
        """
        self.get_logger().info(f'Mensagem recebida em "/target_pose". Realizando transformação.')

        # --- 1. Extrair Posição e Orientação da mensagem recebida ---
        
        # Posição de entrada como um vetor numpy
        pos_in = np.array([
            msg.pose.position.x,
            msg.pose.position.y,
            msg.pose.position.z
        ])

        # Orientação de entrada (quaternião) como um objeto Rotation
        quat_in = Rotation.from_quat([
            msg.pose.orientation.x,
            msg.pose.orientation.y,
            msg.pose.orientation.z,
            msg.pose.orientation.w
        ])

        # --- 2. Aplicar a Transformação Rígida ---
        
        # A nova orientação é o resultado da multiplicação da rotação da transformação
        # pela rotação original. A ordem é importante: T * P_in
        quat_out = self.transform_rotation * quat_in

        # O novo vetor de posição é calculado como: p_out = R * p_in + p
        # Onde R é a rotação da transformação e p é a translação.
        pos_out = self.transform_rotation.apply(pos_in) + self.p
        
        # --- 3. Criar e Publicar a Nova Mensagem ---

        # Cria uma nova mensagem PoseStamped para publicar
        new_pose_msg = PoseStamped()

        # Copia o cabeçalho da mensagem original (timestamp e frame_id)
        new_pose_msg.header = msg.header
        # Opcional: Se a transformação muda o frame de referência, você deve
        # atualizar o `frame_id` aqui. Ex: new_pose_msg.header.frame_id = 'novo_frame'

        # Preenche a nova posição
        new_pose_msg.pose.position.x = pos_out[0]
        new_pose_msg.pose.position.y = pos_out[1]
        new_pose_msg.pose.position.z = pos_out[2]

        # Preenche a nova orientação (convertendo o objeto Rotation de volta para quaternião)
        quat_out_xyzw = quat_out.as_quat()
        new_pose_msg.pose.orientation.x = quat_out_xyzw[0]
        new_pose_msg.pose.orientation.y = quat_out_xyzw[1]
        new_pose_msg.pose.orientation.z = quat_out_xyzw[2]
        new_pose_msg.pose.orientation.w = quat_out_xyzw[3]

        # Publica a mensagem transformada
        self.publisher.publish(new_pose_msg)
        self.get_logger().info('Pose transformada publicada em "/converted_target_pose".')


def main(args=None):
    rclpy.init(args=args)
    pose_transformer_node = PoseTransformer()
    rclpy.spin(pose_transformer_node)
    
    # Destroi o nó explicitamente
    # (opcional - o garbage collector cuidaria disso, mas é uma boa prática)
    pose_transformer_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()