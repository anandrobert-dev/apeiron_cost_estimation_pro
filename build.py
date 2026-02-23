#!/usr/bin/env python3
"""
Apeiron CostEstimation Pro – PyInstaller Build Script
=====================================================
Build a standalone executable for Ubuntu 24.04.
"""

import subprocess
import sys


def build():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "ApeironCostEstimationPro",
        "--add-data", "assets:assets",
        "--hidden-import", "sqlalchemy.dialects.sqlite",
        "run.py",
    ]
    print("Building Apeiron CostEstimation Pro...")
    print(f"Command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("\n✅ Build complete! Executable is in dist/ApeironCostEstimationPro")


if __name__ == "__main__":
    build()
