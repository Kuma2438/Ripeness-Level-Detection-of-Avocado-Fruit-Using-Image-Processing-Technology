import os
import sys
import time
import subprocess
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print("=" * 65)
    print(" [+] AVOCADO RIPENESS & VARIETY DETECTION SYSTEM — CONTROL CENTER ")
    print("=" * 65)

def run_gui_app():
    print("\n[>] Launching Real-Time Dual-Camera GUI App...")
    subprocess.run([sys.executable, "app.py"])

def run_trainer_gui():
    print("\n[>] Launching Avocado Variety Trainer & Labeler Studio...")
    subprocess.run([sys.executable, "trainer_gui.py"])

def run_generate_dataset():
    print("\n[>] Generating / Refreshing Synthetic Sample Dataset...")
    subprocess.run([sys.executable, "generate_dataset.py"])

def run_ml_pipeline():
    print("\n[>] Running Feature Extraction & ML Model Evaluation...")
    import glob, numpy as np, cv2
    from avocado_classifier import AvocadoClassifier
    from avocado_variety_trainer import AvocadoVarietyTrainer

    classifier = AvocadoClassifier('dataset')
    print("\n--- Ripeness Model Status ---")
    print("Dataset Status:", "Trained" if classifier.trained else "Not Trained")
    if hasattr(classifier, 'X_train'):
        print(f"Total Samples: {len(classifier.y_train)}")
        counts = np.bincount(classifier.y_train)
        print(f"  - Unripe: {counts[0] if len(counts)>0 else 0}")
        print(f"  - Mid-ripe: {counts[1] if len(counts)>1 else 0}")
        print(f"  - Ripe: {counts[2] if len(counts)>2 else 0}")

    variety_trainer = AvocadoVarietyTrainer()
    print("\n--- Variety / Label Model Status ---")
    print(f"Classes ({len(variety_trainer.classes)}): {', '.join(variety_trainer.classes)}")
    if hasattr(variety_trainer, 'X_train_norm'):
        print(f"Total Variety Samples: {len(variety_trainer.y_train)}")

    print("\nRunning test inference speed on sample frames...")
    test_files = glob.glob('dataset/*/*.jpg')[:10]
    times = []
    for f in test_files:
        img = cv2.imread(f)
        start = time.time()
        annotated, cat, score, conf, var_name, var_conf = classifier.predict_frame(img)
        times.append((time.time() - start) * 1000)
        print(f"  Image {os.path.basename(f)} -> Class: {cat:8s} | Variety: {var_name:18s} ({var_conf:.0f}%) | Score: {score:5.1f}% | Latency: {times[-1]:.2f} ms")

    if times:
        print(f"\nAverage Inference Latency: {np.mean(times):.2f} ms / frame")

def run_git_push():
    print("\n[>] Syncing & Pushing to GitHub Repository...")
    commit_msg = input("Enter commit message (Press Enter for default): ").strip()
    if not commit_msg:
        commit_msg = "Update project code, variety trainer, and models"
    
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", commit_msg])
    subprocess.run(["git", "push", "origin", "main"])
    print("[+] Pushed successfully!")

def interactive_menu():
    while True:
        clear_screen()
        print_banner()
        print("""
 Select an option to execute:

  [1] 🥑 Launch Real-Time Dual-Camera GUI App (app.py)
  [2] 🎓 Open Variety Trainer & Labeler Studio (trainer_gui.py)
  [3] ⚡ Generate / Refresh Sample Dataset (generate_dataset.py)
  [4] 🧪 Run ML Model Pipeline & Performance Check
  [5] 🐙 Push Changes to GitHub Repository
  [0] ❌ Exit

""")
        choice = input("Enter your choice (0-5): ").strip()

        if choice == '1':
            run_gui_app()
            input("\nPress Enter to return to menu...")
        elif choice == '2':
            run_trainer_gui()
            input("\nPress Enter to return to menu...")
        elif choice == '3':
            run_generate_dataset()
            input("\nPress Enter to return to menu...")
        elif choice == '4':
            run_ml_pipeline()
            input("\nPress Enter to return to menu...")
        elif choice == '5':
            run_git_push()
            input("\nPress Enter to return to menu...")
        elif choice == '0':
            print("\nExiting system. Have a great day!")
            break
        else:
            print("\nInvalid choice. Please try again.")
            time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description="Avocado Ripeness & Variety System Unified CLI")
    parser.add_argument("--app", action="store_true", help="Launch GUI App directly")
    parser.add_argument("--trainer", action="store_true", help="Launch Trainer & Labeler Studio directly")
    parser.add_argument("--dataset", action="store_true", help="Generate dataset directly")
    parser.add_argument("--eval", action="store_true", help="Run ML evaluation directly")
    parser.add_argument("--push", action="store_true", help="Push to Git directly")

    args = parser.parse_args()

    if args.app:
        run_gui_app()
    elif args.trainer:
        run_trainer_gui()
    elif args.dataset:
        run_generate_dataset()
    elif args.eval:
        run_ml_pipeline()
    elif args.push:
        run_git_push()
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
