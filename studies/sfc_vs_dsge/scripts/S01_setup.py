#!/usr/bin/env python3
"""S01 — Environment Setup

Validates Python version, checks required packages, verifies API keys.
"""
import os
import sys
from pathlib import Path


REQUIRED_PACKAGES = ["pandas", "numpy", "statsmodels", "matplotlib", "requests"]
REQUIRED_API_KEYS = ["FRED_API_KEY"]


def main():
    print("S01: Environment setup")

    # Python version
    if sys.version_info < (3, 9):
        raise RuntimeError(f"Python 3.9+ required, got {sys.version}")
    print(f"  Python: {sys.version.split()[0]}")

    # Required packages
    missing_packages = []
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except ImportError:
            missing_packages.append(pkg)
    if missing_packages:
        print(f"  WARNING: Missing packages: {missing_packages}")
        print(f"  Install with: pip install {' '.join(missing_packages)}")
    else:
        print(f"  Packages: all {len(REQUIRED_PACKAGES)} required packages installed")

    # API keys
    missing_keys = [k for k in REQUIRED_API_KEYS if not os.environ.get(k)]
    if missing_keys:
        print(f"  WARNING: Missing API keys: {missing_keys}")
        print(f"  Affected L## scripts will skip API fetches and use cached data if available")
    else:
        print(f"  API keys: all {len(REQUIRED_API_KEYS)} configured")

    # Ensure output directories exist
    project_root = Path(__file__).parent.parent
    for folder in ["data/raw-data", "data/int-data", "data/final-data",
                   "logs/setup", "logs/validation",
                   "outputs/analysis", "outputs/deliverables"]:
        (project_root / folder).mkdir(parents=True, exist_ok=True)

    print("S01: Setup complete")
    return {"status": "SUCCESS", "phase": "S", "script": "S01"}


if __name__ == "__main__":
    main()
