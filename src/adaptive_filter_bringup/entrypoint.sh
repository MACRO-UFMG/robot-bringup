#!/bin/bash
set -e
set -o pipefail

export LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH:-}"

source /opt/ros/jazzy/setup.bash

USERNAME="${USERNAME:-ros}"
if [ -f "/home/${USERNAME}/ros2_ws/install/setup.bash" ]; then
  source "/home/${USERNAME}/ros2_ws/install/setup.bash"
fi

PKG_NAME="adaptive_odom_filter"
PARAMS_FILE="${PARAMS_FILE:-${CONFIG_FILE:-adaptive_filter_parameters.yaml}}"
NAMESPACE="${NAMESPACE:-}"
LAUNCH_FILE="${LAUNCH_FILE:-adaptive_odom_filter.launch.py}"

cleanup() {
  echo "🔌 Shutting down..."
  jobs -p | xargs -r kill -SIGINT
  wait || true
}
trap cleanup SIGINT SIGTERM

echo "🚀 Adaptive Odom Filter Ready!"
echo ""

PARAMS_PATH=""
if [ -f "${PARAMS_FILE}" ]; then
  PARAMS_PATH="${PARAMS_FILE}"
else
  PKG_PREFIX="$(ros2 pkg prefix "${PKG_NAME}" 2>/dev/null || true)"
  for p in \
    "/home/${USERNAME}/ros2_ws/src/${PKG_NAME}/config/${PARAMS_FILE}" \
    "/home/${USERNAME}/ros2_ws/install/${PKG_NAME}/share/${PKG_NAME}/config/${PARAMS_FILE}" \
    "${PKG_PREFIX}/share/${PKG_NAME}/config/${PARAMS_FILE}"
  do
    if [ -f "$p" ]; then
      PARAMS_PATH="$p"
      break
    fi
  done
fi

if [ -z "${PARAMS_PATH}" ]; then
  echo "⚠️  Params file not found: ${PARAMS_FILE}"
  echo ""
else
  echo "🧾 Using params file: ${PARAMS_PATH}"
  echo ""
fi

echo "📦 Package: ${PKG_NAME}"
echo "🚀 Launch file: ${LAUNCH_FILE}"
echo ""

if [ -n "${PARAMS_PATH}" ]; then
  ros2 launch "${PKG_NAME}" "${LAUNCH_FILE}" \
    params_file:="${PARAMS_PATH}" \
    namespace:="${NAMESPACE}" &
else
  ros2 launch "${PKG_NAME}" "${LAUNCH_FILE}" \
    namespace:="${NAMESPACE}" &
fi

wait -n