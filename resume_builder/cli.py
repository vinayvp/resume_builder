"""
CLI launcher for resume_builder application.
"""

import argparse
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Ensure local venv site-packages are loaded
BASE_DIR = Path(__file__).resolve().parent.parent
venv_site = BASE_DIR / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
if venv_site.exists() and str(venv_site) not in sys.path:
    sys.path.insert(0, str(venv_site))

import uvicorn


def open_browser_delayed(url: str, delay_seconds: float = 1.2):
    def _open():
        time.sleep(delay_seconds)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    t = threading.Thread(target=_open, daemon=True)
    t.start()


def main():
    parser = argparse.ArgumentParser(description="Launch Resume Builder Web UI")
    parser.add_argument("--host", default="127.0.0.1", help="Host IP to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open web browser automatically")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    args = parser.parse_args()

    app_url = f"http://{args.host}:{args.port}"
    print("=" * 65)
    print("  🚀 Resume Builder: RenderCV Modern Web UI")
    print(f"  👉 Serving on: {app_url}")
    print("=" * 65)

    if not args.no_browser:
        open_browser_delayed(app_url)

    uvicorn.run(
        "resume_builder.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()

