#!/bin/bash

# ===================================================================
# 🚀 LAUNCH FIXGOBLIN STREAMLIT APP
# ===================================================================
# 
# This script launches the fully integrated Streamlit web interface
# for the FixGoblin autonomous code debugger.
#
# ===================================================================

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   🤖 FIXGOBLIN v2.0 - Streamlit Web Interface              ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit is not installed!"
    echo ""
    echo "Installing Streamlit..."
    pip3 install streamlit
    echo ""
fi

# Check if we're in the right directory
if [ ! -f "streamlit_app.py" ]; then
    echo "❌ Error: streamlit_app.py not found!"
    echo "   Please run this script from the FixGoblin root directory."
    exit 1
fi

# Check if Backend directory exists
if [ ! -d "Backend" ]; then
    echo "❌ Error: Backend directory not found!"
    echo "   The app requires the Backend/ directory to function."
    exit 1
fi

echo "✅ All checks passed!"
echo ""
echo "📋 Starting Streamlit app..."
echo ""
echo "┌──────────────────────────────────────────────────────────────┐"
echo "│  The app will open automatically in your default browser.   │"
echo "│                                                              │"
echo "│  If it doesn't, navigate to:                                │"
echo "│  → http://localhost:8501                                     │"
echo "│                                                              │"
echo "│  To stop the server:                                        │"
echo "│  → Press Ctrl+C in this terminal                            │"
echo "└──────────────────────────────────────────────────────────────┘"
echo ""

# Launch Streamlit
streamlit run streamlit_app.py

echo ""
echo "👋 Streamlit app stopped."
echo ""
