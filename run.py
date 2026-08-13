"""Launch the complete local NEXUS demo without Docker.

Starts FastAPI and the Vite dashboard, then opens the dashboard in a browser.
Press Ctrl+C once in this terminal to stop both services.
"""

from __future__ import annotations

import shutil
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(command: str, install_hint: str) -> None:
    """Fail early with an actionable prerequisite message."""

    if shutil.which(command) is None:
        raise SystemExit(f"Missing '{command}'. {install_hint}")


def main() -> None:
    """Start API and dashboard as child processes."""

    require("npm", "Install Node.js 20+ and reopen PowerShell.")
    api = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--reload"], cwd=ROOT / "backend")
    dashboard = subprocess.Popen(["npm", "run", "dev"], cwd=ROOT / "frontend", shell=True)
    print("NEXUS is starting. Dashboard: http://localhost:5174")
    print("Press Ctrl+C to stop NEXUS.")
    try:
        time.sleep(3)
        webbrowser.open("http://localhost:5174")
        api.wait()
    except KeyboardInterrupt:
        pass
    finally:
        for process in (api, dashboard):
            if process.poll() is None:
                process.send_signal(signal.SIGTERM)
        for process in (api, dashboard):
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    main()
