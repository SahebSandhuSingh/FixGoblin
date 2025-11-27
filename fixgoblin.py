#!/usr/bin/env python3
"""
FixGoblin - Autonomous Debugging System
Main Entry Point

Usage:
    python fixgoblin.py <file_path> [options]
    
Options:
    --log <path>           Save repair log to JSON file
    --max-iterations <n>   Maximum repair iterations (default: 5)
    --efficiency           Enable efficiency mode (only correctness patches)
    --help                 Show this help message

Examples:
    python fixgoblin.py backend/tests/user.py
    python fixgoblin.py backend/tests/new_test_code.py --log backend/logs/repair.json
    python fixgoblin.py backend/tests/buggy.py --max-iterations 3
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.autonomous_repair import main as repair_main

if __name__ == "__main__":
    repair_main()
