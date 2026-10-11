---
name: python-craft
description: >-
  Use this skill when authoring, refactoring, structuring, or debugging Python
  scripts and CLI utilities. Enforces production-grade scaffolding (pathlib,
  argparse, logging, typing, error boundaries) and a 5-step investigative
  root-cause debugging procedure.
---

# Python Craft: Production-Ready Engineering & Systematic Debugging

Guidelines for building maintainable Python automation scripts and systematically debugging issues without guesswork.

---

## Part 1: Production-Grade Script Scaffolding

When writing or refactoring Python scripts, enforce the following architecture:

### 1. Robust CLI & Arguments
- Use `argparse` with sensible defaults, `--help` descriptions, and type validation.
- Avoid hardcoded file paths or magic numbers inside functions.
- Support standard flags where applicable (e.g., `--input`, `--output`, `--verbose` / `--debug`, `--dry-run`).

### 2. Cross-Platform Path Handling
- Always use `pathlib.Path` instead of manual string concatenation or `os.path`.
- Ensure scripts run seamlessly on Windows, macOS, and Linux without path separator issues.

### 3. Structured Logging (No Random `print`)
- Use Python's built-in `logging` module:
  - `logging.info()` for lifecycle events (start, finish, record counts).
  - `logging.warning()` for non-fatal issues (skipped malformed records).
  - `logging.error()` for failure conditions.
- Keep `print()` reserved only for direct stdout streaming or user CLI tables.

### 4. Error Boundaries & Exit Codes
- Catch specific expected exceptions (`FileNotFoundError`, `ValueError`, `KeyError`) with clear error messages.
- Always exit with non-zero status codes on failure (`sys.exit(1)`).
- Never use bare `except:` or empty `except Exception: pass` that swallows failures silently.

### 5. Standard Entry Point Template
```python
import argparse
import logging
from pathlib import Path
import sys

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Script description here.")
    parser.add_argument("--input", "-i", type=Path, required=True, help="Path to input file")
    parser.add_argument("--output", "-o", type=Path, default=Path("output.csv"), help="Path to output file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logging.info("Starting processing...")
    # Core logic here

if __name__ == "__main__":
    main()
```

---

## Part 2: 5-Step Root-Cause Debugging (No Guesswork)

When investigating a bug, failure, or unexpected behavior:

1. **Step 1: Reproduce (Isolate)**
   - Formulate a single command or minimal test case that consistently reproduces the error.
2. **Step 2: Form Hypotheses**
   - Read the stack trace and state leading up to the error.
   - List 1–2 plausible root causes (focus on logic, types, missing data, or boundary conditions).
3. **Step 3: Pinpoint Root Cause**
   - Verify the hypothesis by inspecting the exact failing line and runtime values (via minimal logging or targeted script execution).
   - Never apply random fixes before understanding why it broke.
4. **Step 4: Surgical Fix**
   - Fix the root cause directly at its source.
   - Do not mask the symptom with catch-all wrappers or ad-hoc patches.
5. **Step 5: Regression Guard**
   - Verify that the reproduction command now succeeds.
   - Add a test or assertion so this specific issue cannot silently re-occur.
