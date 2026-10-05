#!/usr/bin/env bash
# ==============================================================================
# Raspberry Pi 5 Standalone Setup Script for Avocado Ripeness Detection
# ==============================================================================

set -e

echo "🥑 Starting Avocado Ripeness Detection Setup for Raspberry Pi 5..."

# 1. Update package lists and install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-tk \
    libgl1 \
    libglib2.0-0 \
    v4l-utils \
    libatlas-base-dev \
    libjpeg-dev \
    zlib1g-dev

# 2. Add user to video group for USB webcam access without sudo
echo "📹 Configuring USB video permissions..."
sudo usermod -a -G video "$USER"

# 3. Create virtual environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

if [ ! -d ".venv" ]; then
    echo "🐍 Creating Python virtual environment in .venv..."
    python3 -m venv .venv --system-site-packages
fi

# 4. Activate venv & install python dependencies
echo "📥 Installing Python packages..."
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -e .

echo "✅ Setup complete!"
echo ""
echo "🚀 To launch the Desktop Inspection Dashboard:"
echo "   ./run.sh"
echo ""
echo "🖥️ To run headless live camera evaluation on Pi 5:"
echo "   source .venv/bin/activate"
echo "   python scripts/run_cli.py --live"
echo ""
