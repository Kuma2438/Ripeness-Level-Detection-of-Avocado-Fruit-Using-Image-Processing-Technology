#!/usr/bin/env python3
"""Run Avocado Ripeness & Variety Inspector GUI."""

import sys
from pathlib import Path

# Add src to pythonpath
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from avocado.ui.app import AvocadoApp


def main() -> None:
    app = AvocadoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
