#!/usr/bin/env bash
# Runner script for Resume Builder
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f ".venv/bin/python" ]; then
    exec .venv/bin/python main.py "$@"
else
    python3 main.py "$@"
fi

