#!/usr/bin/env bash
# Avocado Ripeness and Variety Detection System Launcher for Linux / Raspberry Pi 5

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

show_menu() {
    clear
    echo "========================================================================="
    echo "  AVOCADO RIPENESS & VARIETY DETECTION - RASPBERRY PI 5 / LINUX"
    echo "========================================================================="
    echo ""
    echo "  [1] Launch Desktop Inspection App (On-Demand Mode)"
    echo "  [2] Open Variety Trainer & Labeler Studio (GUI)"
    echo "  [3] Run Interactive Terminal CLI (Press Enter to inspect)"
    echo "  [4] Run Continuous Live Streaming CLI"
    echo "  [5] Build Standalone Executable Binary (PyInstaller)"
    echo "  [6] Run Automated Unit Tests (pytest)"
    echo "  [0] Exit"
    echo ""
    echo "========================================================================="
    read -rp "Enter choice (0-6): " choice
    case $choice in
        1) python3 scripts/run_app.py ;;
        2) python3 scripts/run_trainer.py ;;
        3) python3 scripts/run_cli.py --interactive ;;
        4) python3 scripts/run_cli.py --live ;;
        5) python3 scripts/build_standalone.py ;;
        6) python3 -m unittest discover -s tests -p "test_*.py" ;;
        0) exit 0 ;;
        *) echo "Invalid choice"; sleep 1; show_menu ;;
    esac
}

case "$1" in
    app|1) python3 scripts/run_app.py ;;
    trainer|2) python3 scripts/run_trainer.py ;;
    cli|3) python3 scripts/run_cli.py --interactive ;;
    live|4) python3 scripts/run_cli.py --live ;;
    build|5) python3 scripts/build_standalone.py ;;
    test|6) python3 -m unittest discover -s tests -p "test_*.py" ;;
    *) show_menu ;;
esac
