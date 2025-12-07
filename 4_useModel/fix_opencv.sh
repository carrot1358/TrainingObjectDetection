#!/bin/bash

echo "[*] Starting OpenCV Fix for Raspberry Pi..."

# 1. Force uninstall ALL OpenCV versions (run multiple times to clear duplicates)
echo "[*] Removing existing OpenCV packages..."
pip uninstall opencv-python -y --break-system-packages
pip uninstall opencv-python -y --break-system-packages
pip uninstall opencv-python-headless -y --break-system-packages
pip uninstall opencv-python-headless -y --break-system-packages
pip uninstall opencv-contrib-python -y --break-system-packages
pip uninstall opencv-contrib-python -y --break-system-packages

# 2. Install system dependencies (required for the GUI version)
echo "[*] Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y libgl1-mesa-glx libgtk2.0-dev pkg-config libglib2.0-0

# 3. Install the CORRECT OpenCV version
echo "[*] Installing opencv-python..."
pip install "opencv-python>=4.8.0" --break-system-packages

echo "[*] Clean up complete. Please try running your program now."
