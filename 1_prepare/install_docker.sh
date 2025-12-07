#!/bin/bash
# =============================================================
# Docker & Docker Compose Installation Script for Raspberry Pi
# Tested on: Raspberry Pi OS (Debian-based)
# =============================================================

set -e

echo "=============================================="
echo " Docker Installation for Raspberry Pi"
echo "=============================================="

# Update system
echo "[1/6] Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
echo "[2/6] Installing dependencies..."
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
echo "[3/6] Adding Docker GPG key..."
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo "[4/6] Setting up Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
echo "[5/6] Installing Docker Engine..."
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add current user to docker group (no sudo needed for docker commands)
echo "[6/6] Adding user to docker group..."
sudo usermod -aG docker $USER

# Enable Docker to start on boot
sudo systemctl enable docker
sudo systemctl start docker

echo ""
echo "=============================================="
echo " Installation Complete!"
echo "=============================================="
echo ""
echo "Docker version:"
docker --version
echo ""
echo "Docker Compose version:"
docker compose version
echo ""
echo "=============================================="
echo " IMPORTANT: Please logout and login again"
echo " or run: newgrp docker"
echo " to use Docker without sudo"
echo "=============================================="
