#!/bin/bash

# Check if whiptail is installed
if ! command -v whiptail &> /dev/null
then
    echo "⚠️  whiptail is not installed. Install it with: sudo apt-get install whiptail"
    exit 1
fi

CONFIG_FILE="../config/selected_profiles.conf"

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

# Function to pad text for checkboxes
pad() {
    printf "%-41s" "$1"
}

# ----- Step 1: Choose robotic platform -----
PLATFORM=$(whiptail --title "Robot Platform" --checklist \
"Select the robotic platform:" 15 60 4 \
"pionner" "$(pad "Pioneer robot bringup")" OFF \
"scout"   "$(pad "Scout robot bringup")" OFF \
"espeleo" "$(pad "Espeleo robot bringup (Em desenvolvimento)")" OFF \
3>&1 1>&2 2>&3)

if [ $? -ne 0 ]; then
    echo "❌ Cancelled."
    exit 1
fi

# ----- Step 2: Choose sensors -----
SENSORS=$(whiptail --title "Sensors Configuration" --checklist \
"Select the sensors you want to enable (Space=toggle, Tab=select, Enter=confirm):" 20 60 10 \
"realsense2" "$(pad "Realsense Camera")" OFF \
"livox"     "$(pad "Livox LiDAR")" OFF \
"hokuyo"    "$(pad "Hokuyo LiDAR (Em desenvolvimento)")" OFF \
"other"     "$(pad "Other Sensors (Em desenvolvimento)")" OFF \
3>&1 1>&2 2>&3)

if [ $? -ne 0 ]; then
    echo "❌ Cancelled."
    exit 1
fi

# ----- Step 3: Choose additional packages -----
PACKAGES=$(whiptail --title "Additional Packages" --checklist \
"Select additional packages you want to enable:" 20 60 10 \
"nav2"         "$(pad "Navigation2 (Nav2)")" OFF \
"fastlio2"     "$(pad "FAST-LIO2 Mapping")" OFF \
"pointcloud_to_laserscan"     "$(pad "Convert point cloud to laserscan")" OFF \
"slam"         "$(pad "SLAM (Em desenvolvimento)")" OFF \
"localization" "$(pad "Localization (Em desenvolvimento) ")" OFF \
3>&1 1>&2 2>&3)

if [ $? -ne 0 ]; then
    echo "❌ Cancelled."
    exit 1
fi

# ----- Combine all selections -----
# Remove quotes and join
PROFILES=""
for choice in $PLATFORM $SENSORS $PACKAGES; do
    # Clean choice: remove quotes if any
    choice=$(echo "$choice" | tr -d '"')
    PROFILES="$PROFILES $choice"
done

# Trim leading space
PROFILES=$(echo $PROFILES)

# Save to config file
echo "$PROFILES" > "$CONFIG_FILE"
echo "✅ Configuration saved in $CONFIG_FILE: $PROFILES"