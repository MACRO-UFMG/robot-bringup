#!/bin/bash
set -e

# Check if whiptail is installed
if ! command -v whiptail &> /dev/null; then
  echo "⚠️  whiptail is not installed. Install it with: sudo apt-get install whiptail"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_FILE="${REPO_ROOT}/config/selected_profiles.conf"
mkdir -p "$(dirname "$CONFIG_FILE")"


export NEWT_COLORS='
root=,black
window=white,blue
border=white,blue
shadow=,black
title=brightyellow,blue
roottext=white,black
textbox=white,black
button=black,cyan
actbutton=white,red
listbox=white,black
actlistbox=brightyellow,red
checkbox=brightgreen,black
actcheckbox=brightgreen,red
'

pad() { printf "%-45s" "$1"; }

# ----- Step 0: Base stack (recommended always ON) -----
BASE=$(whiptail --title "Base Stack" --checklist \
"Base ROS stack (recommended):" 12 70 4 \
"ros_base" "$(pad "robot_bringup (base ROS + common deps)")" ON \
3>&1 1>&2 2>&3)

if [ $? -ne 0 ]; then
  echo "❌ Cancelled."
  exit 1
fi

# ----- Step 1: Choose robotic platform -----
PLATFORM=$(whiptail --title "Robot Platform" --checklist \
"Select the robotic platform:" 16 70 6 \
"pioneer" "$(pad "Pioneer robot bringup")" OFF \
"scout"   "$(pad "Scout robot bringup")" OFF \
"espeleo" "$(pad "Espeleo robot bringup (WIP)")" OFF \
3>&1 1>&2 2>&3)

if [ $? -ne 0 ]; then
  echo "❌ Cancelled."
  exit 1
fi

# ----- Step 2: Choose sensors -----
SENSORS=$(whiptail --title "Sensors Configuration" --checklist \
"Select sensors to enable (Space=toggle, Tab=select, Enter=confirm):" 18 70 8 \
"realsense2" "$(pad "RealSense camera bringup")" OFF \
"livox"      "$(pad "Livox LiDAR bringup")" OFF \
"hokuyo"     "$(pad "Hokuyo LiDAR (WIP / placeholder)")" OFF \
"other"      "$(pad "Other sensors (WIP / placeholder)")" OFF \
3>&1 1>&2 2>&3)

if [ $? -ne 0 ]; then
  echo "❌ Cancelled."
  exit 1
fi

# ----- Step 3: Choose additional bringups/packages -----
PACKAGES=$(whiptail --title "Additional Bringups / Packages" --checklist \
"Select additional components:" 22 70 12 \
"localization"            "$(pad "Localization bringup")" OFF \
"navigation"              "$(pad "Navigation bringup")" OFF \
"polaris"                 "$(pad "Polaris (navigation + planning package)")" OFF \
"fastlio2"                "$(pad "FAST-LIO2 bringup")" OFF \
"pointcloud_to_laserscan" "$(pad "pointcloud_to_laserscan bringup")" OFF \
"adaptive_filter"         "$(pad "adaptive_odom_filter bringup")" OFF \
"slam"                    "$(pad "SLAM (WIP / placeholder)")" OFF \
3>&1 1>&2 2>&3)

if [ $? -ne 0 ]; then
  echo "❌ Cancelled."
  exit 1
fi

# ----- Combine selections (deduplicate + clean quotes) -----
declare -A seen
profiles=()

add_choice() {
  local c="$1"
  c="$(echo "$c" | tr -d '"')"
  [ -z "$c" ] && return 0
  if [ -z "${seen[$c]+x}" ]; then
    seen["$c"]=1
    profiles+=("$c")
  fi
}

for choice in $BASE $PLATFORM $SENSORS $PACKAGES; do
  add_choice "$choice"
done

# Safety: ensure ros_base is included
if [ -z "${seen[ros_base]+x}" ]; then
  profiles=("ros_base" "${profiles[@]}")
fi

# Write config file (space-separated)
echo "${profiles[*]}" > "$CONFIG_FILE"
echo "✅ Configuration saved in $CONFIG_FILE:"
echo "   ${profiles[*]}"
