#!/bin/bash

# Diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Mensagem informativa no host (antes de entrar no container)
echo "ℹ️  As bags estarão disponíveis na pasta: $SCRIPT_DIR/shared"
echo "💡 Dica: para gravar uma bag dentro do container, use:"
echo "    ros2 bag record -a -o /shared/minha_gravacao"

docker run -it \
  --network=host \
  --privileged \
  --ipc=host \
  --device=/dev:/dev \
  --env-file "$SCRIPT_DIR/../config/.env" \
  -v "$SCRIPT_DIR/shared:/shared" \
  ros2_jazzy \
  bash -c "
    source /opt/ros/jazzy/setup.bash &&
    cd /shared &&
    echo '' &&
    echo '✅ Ambiente ROS 2 (Jazzy) configurado. Você está na pasta /shared.' &&
    echo '✅ Qualquer bag salva aqui será acessível no host após o container terminar.' &&
    exec bash
  "
