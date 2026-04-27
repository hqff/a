#!/bin/bash
# Installation script for Multi-Camera Gimbal System
# Raspberry Pi 5 - Ubuntu

set -e  # Exit on error

echo "========================================"
echo "Multi-Camera Gimbal System Installation"
echo "========================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "WARNING: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "Please do not run this script as root (without sudo)"
   echo "The script will ask for sudo when needed"
   exit 1
fi

# Update system
echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-opencv \
    python3-numpy \
    python3-serial \
    python3-smbus \
    python3-rpi.gpio \
    python3-lgpio \
    python3-picamera2 \
    ffmpeg \
    v4l-utils \
    i2c-tools \
    git \
    cmake \
    build-essential

# Install Python packages
echo "Installing Python packages..."
pip3 install -r requirements.txt --break-system-packages

# Enable I2C and SPI
echo "Enabling I2C and SPI..."
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0

# Add user to required groups
echo "Adding user to video and i2c groups..."
sudo usermod -a -G video,i2c,spi,gpio $USER

# Create required directories
echo "Creating directories..."
mkdir -p logs
mkdir -p recordings
mkdir -p temp

# Set permissions
chmod +x src/main.py

# Create systemd service (optional)
echo "Creating systemd service..."
sudo tee /etc/systemd/system/gimbal-system.service > /dev/null <<EOF
[Unit]
Description=Multi-Camera Gimbal System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/src/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Arduino setup instructions
echo ""
echo "========================================"
echo "Arduino Setup Required"
echo "========================================"
echo "1. Open Arduino IDE"
echo "2. Install required libraries:"
echo "   - Adafruit PWM Servo Driver Library"
echo "   - AccelStepper"
echo "   - ArduinoJson"
echo "3. Upload arduino/gimbal_controller/gimbal_controller.ino to Arduino Mega"
echo ""

# Configuration
echo "========================================"
echo "Configuration"
echo "========================================"
echo "Please edit src/config.py to configure:"
echo "- Camera settings"
echo "- GPIO pins"
echo "- Motor calibration"
echo "- Network settings"
echo ""

# Completion
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Reboot the system: sudo reboot"
echo "2. After reboot, test the system: python3 src/main.py"
echo "3. Enable auto-start (optional): sudo systemctl enable gimbal-system"
echo ""
echo "Notes:"
echo "- You may need to log out and back in for group changes to take effect"
echo "- Check wiring before powering on the system"
echo "- Refer to docs/WIRING_DIAGRAMS.md for connection details"
echo ""
echo "Happy building!"
