"""
app.py - Maneki-AI Web Frontend (Render Deployment Entry Point)

This is the main entry point for the Render web service at
https://maneki-ai.onrender.com/.

It delegates to the modular web/ui.py which provides:
  - Task Submission Form
  - Task Status Dashboard
  - Execution Report Viewer

Usage:
    streamlit run app.py
    (or via Render: configured in Render Dashboard)
"""

import os
import sys

# Ensure the project root is on sys.path for module imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Delegate to the modular web UI
from web.ui import main

if __name__ == "__main__":
    main()
