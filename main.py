#!/usr/bin/env python3
"""
Entrypoint script for Resume Builder.
Run: python3 main.py
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Ensure local venv site-packages are loaded
venv_site = BASE_DIR / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
if venv_site.exists() and str(venv_site) not in sys.path:
    sys.path.insert(0, str(venv_site))

from resume_builder.cli import main

if __name__ == "__main__":
    main()

