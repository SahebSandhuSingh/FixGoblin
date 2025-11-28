#!/bin/bash
# FixGoblin Web UI Launcher
# Launches the Streamlit web interface

cd "$(dirname "$0")"
streamlit run Backend/ui/streamlit_app.py
