#!/usr/bin/env python3
"""Automated PyInstaller Standalone Binary Builder for Avocado Inspector."""

from pathlib import Path
import platform
import subprocess
import sys


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"

    print("=========================================================================")
    print("  AVOCADO INSPECTOR - STANDALONE EXECUTABLE BUILDER (PyInstaller)")
    print("=========================================================================")
    print(f"System: {platform.system()} ({platform.machine()})")
    print(f"Project Root: {project_root}")
    print("")

    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("⚠️ PyInstaller not found. Installing pyinstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Locate customtkinter asset directory
    try:
        import customtkinter
        ctk_dir = Path(customtkinter.__file__).parent
        ctk_data_arg = f"{ctk_dir}{';' if platform.system() == 'Windows' else ':'}customtkinter"
    except ImportError:
        ctk_data_arg = None

    entrypoint = project_root / "scripts" / "run_app.py"
    models_src = project_root / "models"
    configs_src = project_root / "configs"

    sep = ";" if platform.system() == "Windows" else ":"
    data_args = [
        f"--add-data={models_src}{sep}models",
        f"--add-data={configs_src}{sep}configs",
    ]
    if ctk_data_arg:
        data_args.append(f"--add-data={ctk_data_arg}")

    hidden_imports = [
        "--hidden-import=torch",
        "--hidden-import=torchvision",
        "--hidden-import=PIL",
        "--hidden-import=cv2",
        "--hidden-import=customtkinter",
        "--hidden-import=yaml",
        "--hidden-import=avocado",
    ]

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=avocado-inspector",
        f"--paths={project_root / 'src'}",
        *data_args,
        *hidden_imports,
        str(entrypoint),
    ]

    print("🔨 Running PyInstaller command:")
    print(" ".join(cmd))
    print("")

    ret = subprocess.call(cmd, cwd=str(project_root))
    if ret == 0:
        print("\n=========================================================================")
        print("✅ Standalone Executable Build Successful!")
        print(f"📁 Output Location: {dist_dir / 'avocado-inspector'}")
        print("=========================================================================")
    else:
        print(f"\n❌ Build failed with return code {ret}", file=sys.stderr)
        sys.exit(ret)


if __name__ == "__main__":
    main()
