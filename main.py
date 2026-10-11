#!/usr/bin/env python3
"""
Entrypoint script for Resume Builder.
Run: python3 main.py
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
venv_python = BASE_DIR / ".venv" / "bin" / "python"

# If not running inside the project's .venv, re-exec with the .venv python
if venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
    os.execv(str(venv_python), [str(venv_python)] + sys.argv)

from resume_builder.cli import main

if __name__ == "__main__":
    main()


