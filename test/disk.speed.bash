#!/bin/bash

# Usage
# curl -O https://raw.githubusercontent.com/mshlain/test/refs/heads/main/slowdisk.bash
# chmod +x ./slowdisk.bash
# sudo ./slowdisk.bash

# Oneliner
# curl -O https://raw.githubusercontent.com/mshlain/test/refs/heads/main/slowdisk.bash && chmod +x slowdisk.bash && sudo ./slowdisk.bash

# GOOD
# Time taken to copy: 4 seconds

# BAD
# Time taken to copy: 62 seconds

# Define directories
src="/opt/zerto/fio"
dst="/var/log/zerto/fio"
FILE_NAME="large_file"
FILE_PATH="$src/$FILE_NAME"

rm -rf "$dst"

# Ensure the directories exist
mkdir -p "$src"
mkdir -p "$dst"

# Generate a 10GB file in /folderA using FIO
echo "Generating a 1GB file in $src using dd..."
dd if=/dev/urandom of="$FILE_PATH" bs=1G count=1 status=progress

# Copy the file from /folderA to /folderB and measure the time
echo "Copying the file from $src to $dst..."
START_TIME=$(date +%s)
cp "$FILE_PATH" "$dst"
END_TIME=$(date +%s)

# Calculate and print the time taken
TIME_TAKEN=$((END_TIME - START_TIME))
echo "Time taken to copy: $TIME_TAKEN seconds"

if [ "$TIME_TAKEN" -gt 15 ]; then
    echo -e "\e[41mWARNING: Time taken exceeds 15 seconds!\e[0m"
fi

rm -rf "$dst"
rm -rf "$src"