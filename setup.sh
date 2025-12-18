#!/bin/bash
# MintWatcher Setup Script for Linux Mint/Cinnamon

set -e

echo "Setting up MintWatcher..."

# Check if running on Linux Mint
if ! grep -q "Linux Mint" /etc/os-release 2>/dev/null; then
    echo "Warning: This script is designed for Linux Mint. Proceeding anyway..."
fi

# Install system dependencies
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-gi python3-gi-cairo gir1.2-notify-0.7

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user -r requirements.txt

# Make the main script executable
chmod +x mintwatcher.py

# Create desktop entry (optional)
DESKTOP_FILE="$HOME/.local/share/applications/mintwatcher.desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=MintWatcher
Comment=Linux Mint System Monitor
Exec=$(pwd)/mintwatcher.py --start
Icon=preferences-system-monitoring
Terminal=false
Type=Application
Categories=System;Monitor;
EOF

echo "Setup complete!"
echo ""
echo "Usage:"
echo "  ./mintwatcher.py --help           Show all options"
echo "  ./mintwatcher.py --status         Check current status"
echo "  ./mintwatcher.py --start          Start monitoring (foreground)"
echo ""
echo "Configuration:"
echo "  Edit config.yaml to customize thresholds and settings"
echo ""