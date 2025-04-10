#!/bin/bash

# Create a temporary directory and navigate to it
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR" || exit 1

# Download the latest version of VS Code .deb package
echo "Downloading latest VS Code .deb package..."
wget -q https://code.visualstudio.com/sha/download?build=stable\&os=linux-deb-x64 -O vscode.deb

# Install required dependencies
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y apt-transport-https

# Install VS Code
echo "Installing VS Code..."
sudo dpkg -i vscode.deb
if [ $? -ne 0 ]; then
    echo "Fixing dependencies..."
    sudo apt-get install -f -y
fi

# Clean up
cd - || exit 1
rm -rf "$TMP_DIR"

# Verify installation
if command -v code &> /dev/null; then
    echo "VS Code CLI installation successful!"
    code --version
else
    echo "VS Code CLI installation failed!"
    exit 1
fi