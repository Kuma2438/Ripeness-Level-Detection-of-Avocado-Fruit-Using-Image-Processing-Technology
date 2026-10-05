#!/usr/bin/env python3
"""Headless CLI runner for Avocado Ripeness & Variety Detection on Raspberry Pi 5 / Servers."""

import argparse
import json
from pathlib import Path
import sys
import time
import cv2

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from avocado.camera.manager import DualCameraManager
from avocado.config import load_config
from avocado.core.classifier import AvocadoClassifier


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Avocado Ripeness & Variety CLI on Raspberry Pi 5")
    parser.add_argument("--image", type=str, help="Path to single image file for inference")
    parser.add_argument("--dir", type=str, help="Directory of images to batch process")
    parser.add_argument("--live", action="store_true", help="Run continuous live inference from USB webcams")
    parser.add_argument("--cam1", type=int, default=None, help="Primary USB camera index")
    parser.add_argument("--cam2", type=int, default=None, help="Secondary USB camera index")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--save-annotated", type=str, help="Save annotated image output path")
    return parser.parse_args()


def process_image(classifier: AvocadoClassifier, img_path: Path, output_json: bool, save_path: str | None) -> None:
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"Error: Unable to load image at {img_path}", file=sys.stderr)
        return

    res = classifier.predict_frame(img)

    if output_json:
        data = {
            "image": str(img_path),
            "ripeness": res.category,
            "ripeness_score": round(res.score, 2),
            "ripeness_confidence": round(res.confidence, 2),
            "variety": res.variety_name,
            "variety_confidence": round(res.variety_confidence, 2),
            "roi_box": res.roi_box,
        }
        print(json.dumps(data, indent=2))
    else:
        print(f"\n--- Results for: {img_path.name} ---")
        print(f"Ripeness Stage  : {res.category}")
        print(f"Ripeness Score  : {res.score:.1f}%")
        print(f"Ripeness Conf   : {res.confidence:.1f}%")
        print(f"Variety Name    : {res.variety_name}")
        print(f"Variety Conf    : {res.variety_confidence:.1f}%")

    if save_path:
        cv2.imwrite(save_path, res.annotated_frame)
        if not output_json:
            print(f"Annotated frame saved to: {save_path}")


def run_live(classifier: AvocadoClassifier, cam1_id: int | None, cam2_id: int | None, output_json: bool) -> None:
    config = load_config()
    cam_manager = DualCameraManager(config=config, cam1_id=cam1_id, cam2_id=cam2_id)
    print("Starting live USB webcam stream (Press Ctrl+C to stop)...")

    try:
        while True:
            t0 = time.time()
            f1, f2 = cam_manager.read_frames()
            res1 = classifier.predict_frame(f1)
            res2 = classifier.predict_frame(f2)
            latency = (time.time() - t0) * 1000.0

            avg_score = (res1.score + res2.score) / 2.0

            if output_json:
                data = {
                    "timestamp": time.time(),
                    "ripeness": res1.category,
                    "score": round(avg_score, 1),
                    "variety": res1.variety_name,
                    "latency_ms": round(latency, 1),
                }
                print(json.dumps(data))
            else:
                print(
                    f"\r[Live] Ripeness: {res1.category:<10} | Score: {avg_score:5.1f}% | "
                    f"Variety: {res1.variety_name:<12} | Latency: {latency:4.1f}ms",
                    end="",
                    flush=True,
                )
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopping camera stream.")
    finally:
        cam_manager.release()


def main() -> None:
    args = parse_args()
    config = load_config()
    classifier = AvocadoClassifier(config=config)

    if args.image:
        process_image(classifier, Path(args.image), args.json, args.save_annotated)
    elif args.dir:
        folder = Path(args.dir)
        valid_exts = {".jpg", ".jpeg", ".png", ".bmp"}
        for f in folder.iterdir():
            if f.suffix.lower() in valid_exts:
                process_image(classifier, f, args.json, None)
    elif args.live:
        run_live(classifier, args.cam1, args.cam2, args.json)
    else:
        print("Please provide --image, --dir, or --live. Use --help for details.")


if __name__ == "__main__":
    main()
