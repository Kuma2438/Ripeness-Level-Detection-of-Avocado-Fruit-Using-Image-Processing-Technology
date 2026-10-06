#!/usr/bin/env python3
"""Run Avocado Variety Trainer & Labeler Studio."""

import sys
from pathlib import Path
import customtkinter as ctk

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from avocado.ui.trainer_gui import TrainerLabelerStudio


def main() -> None:
    root = ctk.CTk()
    root.withdraw()
    trainer = TrainerLabelerStudio(parent=root)
    trainer.protocol("WM_DELETE_WINDOW", lambda: (trainer.on_closing(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
