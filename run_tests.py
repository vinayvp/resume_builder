#!/usr/bin/env python3
"""
Test runner script.
Run: python3 run_tests.py
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
venv_site = BASE_DIR / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
if venv_site.exists() and str(venv_site) not in sys.path:
    sys.path.insert(0, str(venv_site))

import pytest

if __name__ == "__main__":
    args = ["tests/", "-v"] + sys.argv[1:]
    exit_code = pytest.main(args)
    sys.exit(exit_code)

