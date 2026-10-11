"""Custom speedometer gauge widget for displaying avocado ripeness percentages and inactive status."""

import math
from typing import Optional
import tkinter as tk


class GaugeWidget(tk.Canvas):
    """Tkinter Canvas-based speedometer gauge for ripeness visualization and status indication."""

    def __init__(self, parent: tk.Widget, width: int = 300, height: int = 210, bg: str = "#1a1a1a", **kwargs) -> None:
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height * 0.72
        self.radius = min(width, height) * 0.40

        self.current_score: Optional[float] = None
        self.target_score: Optional[float] = None
        self.is_active = False

        self.draw_gauge()

    def draw_gauge(self) -> None:
        """Draws static gauge track, colored zones, and tick marks."""
        self.delete("all")

        cx, cy, r = self.center_x, self.center_y, self.radius
        bbox = (cx - r, cy - r, cx + r, cy + r)

        track_w = max(12, int(r * 0.22))
        self.create_arc(bbox, start=0, extent=180, outline="#333333", width=track_w + 4, style="arc")
        self.create_arc(bbox, start=120, extent=60, outline="#2ecc71", width=track_w, style="arc")
        self.create_arc(bbox, start=60, extent=60, outline="#f39c12", width=track_w, style="arc")
        self.create_arc(bbox, start=0, extent=60, outline="#e74c3c", width=track_w, style="arc")

        ticks = [
            (180, "0%", "#2ecc71"),
            (120, "33%", "#f1c40f"),
            (60, "66%", "#e74c3c"),
            (0, "100%", "#e74c3c"),
        ]

        font_size = max(7, int(r * 0.11))
        for angle, text, _color in ticks:
            rad = math.radians(angle)
            tx1 = cx + (r - 8) * math.cos(rad)
            ty1 = cy - (r - 8) * math.sin(rad)
            tx2 = cx + (r + 4) * math.cos(rad)
            ty2 = cy - (r + 4) * math.sin(rad)
            self.create_line(tx1, ty1, tx2, ty2, fill="#777777", width=2)

            lx = cx + (r + 14) * math.cos(rad)
            ly = cy - (r + 14) * math.sin(rad)
            self.create_text(lx, ly, text=text, fill="#aaaaaa", font=("Helvetica", font_size, "bold"))

        if self.is_active and self.current_score is not None:
            self.draw_needle(self.current_score)
        else:
            self.draw_inactive("--%", "STANDBY / WAITING", "#888888")

    def draw_needle(self, score: float) -> None:
        """Updates and redraws indicator needle and numerical status."""
        self.delete("needle")
        self.delete("text_val")

        cx, cy, r = self.center_x, self.center_y, self.radius
        score_clamped = max(0.0, min(100.0, score))
        angle_deg = 180.0 - (score_clamped / 100.0) * 180.0
        rad = math.radians(angle_deg)

        nx = cx + (r - 8) * math.cos(rad)
        ny = cy - (r - 8) * math.sin(rad)

        base_r = max(4, int(r * 0.08))
        perp_rad = rad + math.pi / 2
        bx1 = cx + base_r * math.cos(perp_rad)
        by1 = cy - base_r * math.sin(perp_rad)
        bx2 = cx - base_r * math.cos(perp_rad)
        by2 = cy + base_r * math.sin(perp_rad)

        if score_clamped < 33.3:
            needle_color = "#2ecc71"
            status_str = "UNRIPE (ดิบ)"
        elif score_clamped < 66.6:
            needle_color = "#f39c12"
            status_str = "MID-RIPE (กึ่งสุก)"
        else:
            needle_color = "#e74c3c"
            status_str = "RIPE (สุก)"

        main_font_size = max(13, int(r * 0.28))
        sub_font_size = max(8, int(r * 0.14))

        self.create_polygon([bx1, by1, nx, ny, bx2, by2], fill=needle_color, outline="#ffffff", width=1, tags="needle")
        self.create_oval(cx - base_r - 2, cy - base_r - 2, cx + base_r + 2, cy + base_r + 2, fill="#222222", outline="#ffffff", width=2, tags="needle")
        self.create_text(cx, cy + int(r * 0.28), text=f"{score_clamped:.1f}%", fill=needle_color, font=("Helvetica", main_font_size, "bold"), tags="text_val")
        self.create_text(cx, cy + int(r * 0.50), text=status_str, fill="#ffffff", font=("Helvetica", sub_font_size, "bold"), tags="text_val")

    def draw_inactive(self, pct_str: str, status_str: str, color: str = "#888888") -> None:
        """Draws parked inactive state (no false 0% reading)."""
        self.delete("needle")
        self.delete("text_val")

        cx, cy, r = self.center_x, self.center_y, self.radius
        base_r = max(4, int(r * 0.08))

        # Park needle pointing straight down at rest
        self.create_oval(cx - base_r, cy - base_r, cx + base_r, cy + base_r, fill="#333333", outline="#666666", width=2, tags="needle")

        main_font_size = max(13, int(r * 0.28))
        sub_font_size = max(8, int(r * 0.13))

        self.create_text(cx, cy + int(r * 0.28), text=pct_str, fill=color, font=("Helvetica", main_font_size, "bold"), tags="text_val")
        self.create_text(cx, cy + int(r * 0.50), text=status_str, fill="#aaaaaa", font=("Helvetica", sub_font_size, "bold"), tags="text_val")

    def set_score(self, target_score: Optional[float]) -> None:
        """Sets gauge score. If None, puts gauge into inactive state."""
        if target_score is None:
            self.set_inactive("--%", "NO AVOCADO (ไม่พบอะโวคาโด)", "#888888")
            return

        self.is_active = True
        self.target_score = target_score
        if self.current_score is None:
            self.current_score = target_score

        diff = self.target_score - self.current_score
        if abs(diff) > 0.5:
            self.current_score += diff * 0.35
        else:
            self.current_score = self.target_score

        self.draw_needle(self.current_score)

    def set_inactive(self, pct_str: str = "--%", status_str: str = "NO AVOCADO", color: str = "#888888") -> None:
        """Forces gauge into an inactive or rejected state."""
        self.is_active = False
        self.current_score = None
        self.target_score = None
        self.draw_inactive(pct_str, status_str, color)
