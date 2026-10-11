# Spec: RGB Pipeline, Empty Box Detection, Non-Avocado Rejection & 85.42 mm × 55.60 mm Hardware UI Optimization

- **Date:** 2026-10-11
- **Type:** Python script, Computer Vision Engine, Touchscreen UI & Documentation
- **Status:** Approved

## 1. Goal
1. Standardize camera capture and CNN inference to native RGB color space.
2. Eliminate false 0% ripeness readings on empty scan boxes by detecting when the box is empty ("No avocado detected"), parking the gauge at `--%`.
3. Reject foreign non-avocado objects (hands, skin, cups, paper, other fruits) using morphological and RGB/HSV chromatic validation ("Not an avocado").
4. Adapt the UI for compact hardware touchscreen displays (active area: width 85.42 mm × height 55.60 mm, native ~480×320 landscape), providing a clean landscape touch-friendly layout with large buttons and switchable/stacked camera preview.
5. Rewrite project README to comprehensively document the new RGB pipeline, detection states, 85.42 mm × 55.60 mm hardware display setup, and run instructions.

## 2. Context
- Hardware Display: Active display area 85.42 mm (width) × 55.60 mm (height) — standard landscape LCD (e.g. 480×320 or 800×480 pixels, ~3.5" to 4.0" form factor).
- Relevant files:
  - [`src/avocado/camera/manager.py`](file:///c:/Users/tinna/Documents/antigravity/goofy-pascal/src/avocado/camera/manager.py): Camera capture pipeline.
  - [`src/avocado/core/classifier.py`](file:///c:/Users/tinna/Documents/antigravity/goofy-pascal/src/avocado/core/classifier.py): ROI extraction and classification.
  - [`src/avocado/core/trainer.py`](file:///c:/Users/tinna/Documents/antigravity/goofy-pascal/src/avocado/core/trainer.py): Preprocessing and tensor normalization.
  - [`src/avocado/ui/app.py`](file:///c:/Users/tinna/Documents/antigravity/goofy-pascal/src/avocado/ui/app.py): Desktop & Kiosk GUI dashboard.
  - [`src/avocado/ui/widgets/gauge.py`](file:///c:/Users/tinna/Documents/antigravity/goofy-pascal/src/avocado/ui/widgets/gauge.py): Speedometer gauge widget.
  - [`configs/default.yaml`](file:///c:/Users/tinna/Documents/antigravity/goofy-pascal/configs/default.yaml): System configuration.
  - [`README.md`](file:///c:/Users/tinna/Documents/antigravity/goofy-pascal/README.md): Documentation.

## 3. Scope
- **In scope:**
  - Camera & Model RGB888 color consistency across Picamera2, USB, and Simulation.
  - Empty scan box detection (`No Avocado Detected`, `--%` gauge).
  - Non-avocado object rejection filter (`Not an Avocado`, `--%` gauge).
  - Responsive / Adaptive UI layout mode for 85.42 mm × 55.60 mm screen (480×320 landscape):
    - Landscape layout (Left: Camera preview with CAM1/CAM2 switcher; Right: Results, compact gauge, and bottom touch trigger button).
    - Large touch target (>= 48px height) for finger navigation on an 85.42 mm wide screen.
  - Speedometer Gauge update: supports `--%` inactive state and responsive scaling.
  - Comprehensive `README.md` rewrite covering new detection behaviors, RGB pipeline, 85.42 mm × 55.60 mm hardware display guide, and installation.
  - Unit test additions in `tests/test_classifier.py`.
- **Out of scope:**
  - OS-level kernel display drivers.

## 4. Details
### Touchscreen UI (480×320 Landscape / 85.42 mm × 55.60 mm)
- Default window geometry: 480×320 in compact landscape mode, or adaptive when running on small screens.
- Left column: Camera preview box with 1-tap `[CAM 1 | CAM 2]` switcher.
- Right column: Result card, compact Gauge (width ~190, height ~110), and large touch button.

### Documentation (README.md Rewrite)
- Full documentation for:
  - New detection pipeline: Empty box detection & Foreign object rejection.
  - RGB camera & model standardization.
  - 85.42 mm × 55.60 mm (480×320 Landscape) LCD hardware setup guide.
  - Windows standalone & Raspberry Pi 5 touch kiosk setup.

## 5. Acceptance criteria (checkable)
- [ ] Empty frame returns `category="No Avocado"` and `score=None`.
- [ ] Non-avocado objects return `category="Not Avocado"` and `score=None`.
- [ ] Gauge widget displays `--%` and neutral message when empty/invalid.
- [ ] UI provides a dedicated landscape mode fitting 480×320 resolution without clipping or missing controls.
- [ ] Large touch button at bottom for easy fingertip operation on 85.42 mm × 55.60 mm screen.
- [ ] Camera frames natively output RGB.
- [ ] `README.md` rewritten with updated diagrams, detection guides, and hardware display section.
- [ ] Unit tests pass cleanly.

## 6. Assumptions
- A1: 85.42 mm × 55.60 mm screen maps to 480×320 pixels (3:2 landscape) or scales responsively.

## 7. Change log
- 2026-10-11: Updated to 85.42 mm × 55.60 mm landscape display and approved for implementation.
