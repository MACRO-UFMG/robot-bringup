#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformListener, Buffer, TransformBroadcaster
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException

import numpy as np
from transforms3d.affines import compose, decompose
from transforms3d.quaternions import quat2mat, mat2quat

class TfTransformerNode(Node):
    """
    Este nó escuta a transformação de 'world' para 'scout_mini/base_link',
    aplica uma transformação homogênea fixa e publica o resultado como
    uma nova transformação de 'world' para 'ScoutMini1/base_link'.
    """
    def __init__(self):
        super().__init__('pose_transform_node')

        # --- Parâmetros ---
        # A transformação que queremos obter é a pose do 'child_frame' em relação ao 'parent_frame'
        self.parent_frame = 'world'
        self.child_frame_to_listen = 'scout_mini/base_link'
        self.new_child_frame_to_publish = 'converted_scout_mini/base_link'
        
        self.homogeneous_matrix = np.array([
            [0.0, -1.0,  0.0, 66.5882],
            [1.0,  0.0,  0.0,-19.5770],
            [0.0,  0.0,  1.0,  0.0     ],
            [0.0,  0.0,  0.0,  1.0     ]
        ])

        # --- TF2 Listener e Broadcaster ---
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = TransformBroadcaster(self)

        # --- Timer para processamento ---
        self.timer = self.create_timer(0.1, self.on_timer)
        self.get_logger().info('Nó transformador de TF iniciado e pronto.')

    def on_timer(self):
        """
        Callback do timer. Tenta obter a transformação, processá-la e publicar a nova.
        """
        try:
            # 1. Obter a transformação 'world' -> 'scout_mini/base_link'
            # A API lookup_transform(target, source) obtém a transformação que
            # leva as coordenadas do frame 'source' para o frame 'target'.
            # Queremos a pose de 'scout_mini/base_link' em relação a 'world'.
            # target_frame = 'world' (o sistema de coordenadas de destino)
            # source_frame = 'scout_mini/base_link' (o sistema de coordenadas de origem)
            t_in = self.tf_buffer.lookup_transform(
                self.parent_frame,           # Target frame
                self.child_frame_to_listen,  # Source frame
                rclpy.time.Time()
            )

        except (LookupException, ConnectivityException, ExtrapolationException) as e:
            self.get_logger().warn(f'Ainda não foi possível obter a transformação de "{self.parent_frame}" para "{self.child_frame_to_listen}": {e}')
            return

        # 2. Converter a transformação recebida para uma matriz 4x4
        translation_in = t_in.transform.translation
        rotation_in = t_in.transform.rotation
        T_world_scout = compose(
            [translation_in.x, translation_in.y, translation_in.z],
            quat2mat([rotation_in.w, rotation_in.x, rotation_in.y, rotation_in.z]),
            [1.0, 1.0, 1.0]
        )

        # 3. Realizar a transformação homogênea
        T_world_new = self.homogeneous_matrix @ T_world_scout
        
        # 4. Decompor a nova matriz 4x4
        translation_out, rotation_matrix_out, _, _ = decompose(T_world_new)
        quat_out = mat2quat(rotation_matrix_out)

        # 5. Publicar o resultado em /tf
        t_out = TransformStamped()
        t_out.header.stamp = self.get_clock().now().to_msg()
        t_out.header.frame_id = self.parent_frame
        t_out.child_frame_id = self.new_child_frame_to_publish

        t_out.transform.translation.x = translation_out[0]
        t_out.transform.translation.y = translation_out[1]
        t_out.transform.translation.z = translation_out[2]

        t_out.transform.rotation.w = quat_out[0]
        t_out.transform.rotation.x = quat_out[1]
        t_out.transform.rotation.y = quat_out[2]
        t_out.transform.rotation.z = quat_out[3]

        self.tf_broadcaster.sendTransform(t_out)

def main(args=None):
    rclpy.init(args=args)
    node = TfTransformerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()