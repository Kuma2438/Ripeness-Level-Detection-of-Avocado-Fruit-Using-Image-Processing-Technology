#!/usr/bin/env bash
# ==============================================================================
# Linux / Raspberry Pi 5 Desktop Installer for Avocado Ripeness Inspector
# ==============================================================================

set -e

echo "========================================================================="
echo "🥑 Avocado Ripeness & Variety Inspector - Linux / Pi 5 Setup"
echo "========================================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INSTALL_DIR="/opt/avocado-inspector"

echo "📦 1. Installing system prerequisites (OpenCV, Tkinter, V4L2)..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-tk \
    libgl1 \
    libglib2.0-0 \
    v4l-utils

echo "📹 2. Configuring USB webcam permissions..."
sudo usermod -a -G video "$USER"

echo "📂 3. Installing application files to $INSTALL_DIR..."
sudo mkdir -p "$INSTALL_DIR"
sudo cp -r "$PROJECT_ROOT/src" "$INSTALL_DIR/"
sudo cp -r "$PROJECT_ROOT/models" "$INSTALL_DIR/"
sudo cp -r "$PROJECT_ROOT/configs" "$INSTALL_DIR/"
sudo cp -r "$PROJECT_ROOT/scripts" "$INSTALL_DIR/"
sudo cp "$PROJECT_ROOT/requirements.txt" "$INSTALL_DIR/"
sudo cp "$PROJECT_ROOT/pyproject.toml" "$INSTALL_DIR/"

echo "🐍 4. Creating Python virtual environment in $INSTALL_DIR/.venv..."
sudo python3 -m venv "$INSTALL_DIR/.venv" --system-site-packages
sudo "$INSTALL_DIR/.venv/bin/pip" install --upgrade pip
sudo "$INSTALL_DIR/.venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
sudo "$INSTALL_DIR/.venv/bin/pip" install -e "$INSTALL_DIR"

# Set ownership to current user
sudo chown -R "$USER:$USER" "$INSTALL_DIR"

echo "🔗 5. Creating CLI shortcut /usr/local/bin/avocado-inspector..."
sudo tee /usr/local/bin/avocado-inspector > /dev/null << 'EOF'
#!/usr/bin/env bash
source /opt/avocado-inspector/.venv/bin/activate
exec python3 /opt/avocado-inspector/scripts/run_app.py "$@"
EOF
sudo chmod +x /usr/local/bin/avocado-inspector

echo "🖥️ 6. Creating Desktop & Applications Menu shortcuts..."
DESKTOP_ENTRY="[Desktop Entry]
Name=Avocado Ripeness Inspector
Comment=Dual USB Camera Ripeness & Variety Classifier
Exec=/usr/local/bin/avocado-inspector
Icon=camera-video
Terminal=false
Type=Application
Categories=Utility;Science;Education;
"

mkdir -p ~/.local/share/applications
echo "$DESKTOP_ENTRY" > ~/.local/share/applications/avocado-inspector.desktop

if [ -d "$HOME/Desktop" ]; then
    echo "$DESKTOP_ENTRY" > "$HOME/Desktop/Avocado-Inspector.desktop"
    chmod +x "$HOME/Desktop/Avocado-Inspector.desktop"
fi

echo ""
echo "========================================================================="
echo "✅ Installation Complete on Linux / Raspberry Pi 5!"
echo "👉 Launch from Application Menu, Desktop icon, or type: avocado-inspector"
echo "========================================================================="
