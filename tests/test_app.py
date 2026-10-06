"""Unit test for AvocadoApp GUI initialization without attribute collision."""

import unittest
from pathlib import Path
import sys

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    import customtkinter as ctk
    from avocado.ui.app import AvocadoApp, AppState
    GUI_AVAILABLE = True
except Exception:
    GUI_AVAILABLE = False


class TestAvocadoAppInit(unittest.TestCase):
    def test_app_initialization_and_state(self) -> None:
        if not GUI_AVAILABLE:
            self.skipTest("GUI or CustomTkinter not available")

        try:
            app = AvocadoApp()
            self.assertEqual(app.inspection_state, AppState.STANDBY)
            self.assertTrue(callable(app.state))  # Verifies Tkinter built-in self.state is preserved
            app.destroy()
        except Exception as e:
            if "no display name" in str(e).lower() or "cannot connect to x server" in str(e).lower():
                self.skipTest("Headless environment (no X display)")
            else:
                raise e


if __name__ == "__main__":
    unittest.main()
