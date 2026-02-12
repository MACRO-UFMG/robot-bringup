#!/bin/bash
set -e
set -o pipefail

# Safe even if LD_LIBRARY_PATH is unset
export LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH:-}"

# Source ROS 2 environment (DON'T use `set -u` with ROS setup scripts)
source /opt/ros/jazzy/setup.bash

# Source workspace overlay (if built)
USERNAME="${USERNAME:-ros}"
if [ -f "/home/${USERNAME}/ros2_ws/install/setup.bash" ]; then
  source "/home/${USERNAME}/ros2_ws/install/setup.bash"
fi

PKG_NAME="adaptive_odom_filter"

# Accept either PARAMS_FILE or CONFIG_FILE (your compose uses CONFIG_FILE)
PARAMS_FILE="${PARAMS_FILE:-${CONFIG_FILE:-adaptive_filter_parameters.yaml}}"
NAMESPACE="${NAMESPACE:-}"
EXECUTABLE="${EXECUTABLE:-}"

cleanup() {
  echo "🔌 Shutting down..."
  jobs -p | xargs -r kill -SIGINT
  wait || true
}
trap cleanup SIGINT SIGTERM

echo "🚀 Adaptive Odom Filter Ready!"
echo ""

# Try to locate params file (supports absolute path or filename)
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
  echo "    (Set CONFIG_FILE or PARAMS_FILE to an absolute path, or install it into share/${PKG_NAME}/config)"
  echo ""
else
  echo "🧾 Using params file: ${PARAMS_PATH}"
  echo ""
fi

# Auto-detect executable if not provided
if [ -z "${EXECUTABLE}" ]; then
  EXECUTABLE="$(ros2 pkg executables "${PKG_NAME}" 2>/dev/null | awk 'NR==1{print $2}')"
fi

if [ -z "${EXECUTABLE}" ]; then
  echo "❌ Could not detect an executable for '${PKG_NAME}'."
  echo "   Try: ros2 pkg executables adaptive_odom_filter"
  echo "   Then set EXECUTABLE=<name> in compose."
  exit 1
fi

# Namespace remap only if set
NS_ARGS=""
if [ -n "${NAMESPACE}" ]; then
  [[ "${NAMESPACE}" != /* ]] && NAMESPACE="/${NAMESPACE}"
  NS_ARGS="--ros-args -r __ns:=${NAMESPACE}"
fi

echo "🎯 Running: ros2 run ${PKG_NAME} ${EXECUTABLE}"
echo ""

# Run filter
if [ -n "${PARAMS_PATH}" ]; then
  ros2 run "${PKG_NAME}" "${EXECUTABLE}" ${NS_ARGS} --ros-args --params-file "${PARAMS_PATH}" &
else
  ros2 run "${PKG_NAME}" "${EXECUTABLE}" ${NS_ARGS} &
fi

wait -n
