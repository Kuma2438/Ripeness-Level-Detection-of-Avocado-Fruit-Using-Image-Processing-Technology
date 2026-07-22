import tkinter as tk
import math

class GaugeWidget(tk.Canvas):
    def __init__(self, parent, width=300, height=220, bg="#1a1a1a", **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height * 0.72
        self.radius = min(width, height) * 0.42
        
        self.current_score = 0.0
        self.target_score = 0.0
        
        self.draw_gauge()

    def draw_gauge(self):
        self.delete("all")
        
        # Arc colors
        # Angles in tkinter arc: 0 is East, 90 is North, 180 is West
        # Gauge range: 180 (Left - 0%) to 0 (Right - 100%)
        
        cx, cy, r = self.center_x, self.center_y, self.radius
        bbox = (cx - r, cy - r, cx + r, cy + r)
        
        # Background arc track
        self.create_arc(bbox, start=0, extent=180, outline="#333333", width=24, style="arc")
        
        # Zone Arcs
        # Unripe (0 - 33.3%): start=120, extent=60
        self.create_arc(bbox, start=120, extent=60, outline="#2ecc71", width=20, style="arc")
        # Mid-ripe (33.3 - 66.6%): start=60, extent=60
        self.create_arc(bbox, start=60, extent=60, outline="#f39c12", width=20, style="arc")
        # Ripe (66.6 - 100%): start=0, extent=60
        self.create_arc(bbox, start=0, extent=60, outline="#e74c3c", width=20, style="arc")
        
        # Ticks and Labels
        ticks = [
            (180, "0%", "#2ecc71"),
            (150, "Unripe", "#2ecc71"),
            (120, "33%", "#f1c40f"),
            (90, "Mid-ripe", "#f39c12"),
            (60, "66%", "#e74c3c"),
            (30, "Ripe", "#e74c3c"),
            (0, "100%", "#e74c3c")
        ]
        
        for angle, text, color in ticks:
            rad = math.radians(angle)
            # Inner tick
            tx1 = cx + (r - 12) * math.cos(rad)
            ty1 = cy - (r - 12) * math.sin(rad)
            tx2 = cx + (r + 4) * math.cos(rad)
            ty2 = cy - (r + 4) * math.sin(rad)
            self.create_line(tx1, ty1, tx2, ty2, fill="#777777", width=2)
            
            # Label
            lx = cx + (r + 20) * math.cos(rad)
            ly = cy - (r + 20) * math.sin(rad)
            if "%" in text:
                self.create_text(lx, ly, text=text, fill="#aaaaaa", font=("Helvetica", 9, "bold"))

        # Draw Needle
        self.draw_needle(self.current_score)

    def draw_needle(self, score):
        # Delete old needle
        self.delete("needle")
        self.delete("text_val")
        
        cx, cy, r = self.center_x, self.center_y, self.radius
        
        # Convert score (0 - 100) to angle (180 - 0)
        score_clamped = max(0.0, min(100.0, score))
        angle_deg = 180.0 - (score_clamped / 100.0) * 180.0
        rad = math.radians(angle_deg)
        
        # Needle Tip
        nx = cx + (r - 10) * math.cos(rad)
        ny = cy - (r - 10) * math.sin(rad)
        
        # Needle base perpendicular points
        base_r = 8
        perp_rad = rad + math.pi / 2
        bx1 = cx + base_r * math.cos(perp_rad)
        by1 = cy - base_r * math.sin(perp_rad)
        bx2 = cx - base_r * math.cos(perp_rad)
        by2 = cy + base_r * math.sin(perp_rad)
        
        # Color based on score
        if score_clamped < 33.3:
            needle_color = "#2ecc71"
            status_str = "UNRIPE (ดิบ)"
        elif score_clamped < 66.6:
            needle_color = "#f39c12"
            status_str = "MID-RIPE (กึ่งสุก)"
        else:
            needle_color = "#e74c3c"
            status_str = "RIPE (สุก)"

        # Draw polygon needle
        self.create_polygon([bx1, by1, nx, ny, bx2, by2], fill=needle_color, outline="#ffffff", width=1, tags="needle")
        self.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill="#222222", outline="#ffffff", width=2, tags="needle")
        
        # Score Text below gauge center
        self.create_text(cx, cy + 30, text=f"{score_clamped:.1f}%", fill=needle_color, font=("Helvetica", 22, "bold"), tags="text_val")
        self.create_text(cx, cy + 54, text=status_str, fill="#ffffff", font=("Helvetica", 12, "bold"), tags="text_val")

    def set_score(self, target_score):
        """Smoothly update needle towards target score"""
        self.target_score = target_score
        # Smooth interpolation
        diff = self.target_score - self.current_score
        if abs(diff) > 0.5:
            self.current_score += diff * 0.25
        else:
            self.current_score = self.target_score
            
        self.draw_needle(self.current_score)
