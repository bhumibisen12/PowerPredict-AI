"""
PowerPredict AI - Main Entry Launcher
Starts the FastAPI application and serves the complete AI Command Center.
"""

import sys
import io

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import uvicorn
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if __name__ == "__main__":
    print("=" * 70)
    print("[*] POWERPREDICT AI - NATIONAL POWER PROJECT PREDICTIVE PLATFORM")
    print("[*] Ministry of Power & CEA Calibrated Enterprise Decision Support")
    print("[*] Starting Server on http://localhost:8000")
    print("=" * 70)
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=False)
