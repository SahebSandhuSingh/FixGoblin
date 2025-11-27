#!/usr/bin/env python3
"""
FixGoblin - Universal Autonomous Debugging System
Main Entry Point - Now supports ALL major languages!

Supported Languages:
    ✅ Python    - Full auto-repair with logical error detection
    ✅ C++       - Full auto-repair with syntax & semantic fixes
    ✅ Java      - Full auto-repair with type & compilation fixes
    ✅ JavaScript- Full auto-repair with runtime error fixes
    ✅ C         - Full auto-repair (uses C++ engine)
    ✅ Go        - Error detection (auto-repair coming soon)

Usage:
    python fixgoblin.py <file_path> [options]
    
Options:
    --log <path>           Save repair log to JSON file
    --max-iterations <n>   Maximum repair iterations (default: 5)
    --efficiency           Enable efficiency mode (only correctness patches)
    --language <lang>      Force language (auto-detected from extension)
    --help                 Show this help message

Examples:
    # Python (existing system)
    python fixgoblin.py backend/tests/user.py
    
    # C++ auto-repair (NEW!)
    python fixgoblin.py buggy_code.cpp
    
    # Java auto-repair (NEW!)
    python fixgoblin.py MyClass.java --max-iterations 10
    
    # JavaScript auto-repair (NEW!)
    python fixgoblin.py app.js
    
    # With logging
    python fixgoblin.py code.cpp --log repair_log.json
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from universal_repair import universal_repair

def main():
    """Main entry point with universal language support"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='FixGoblin - Universal Auto-Repair for All Languages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported Languages:
  Python, C++, Java, JavaScript, C, Go
  
Examples:
  python fixgoblin.py buggy.py
  python fixgoblin.py buggy.cpp --max-iterations 10
  python fixgoblin.py MyClass.java --log repair.json
        """
    )
    
    parser.add_argument('file', help='Source code file to repair')
    parser.add_argument('--max-iterations', type=int, default=5, 
                       help='Maximum repair iterations (default: 5)')
    parser.add_argument('--language', help='Programming language (auto-detected if omitted)')
    parser.add_argument('--log', help='Save repair log to JSON file')
    parser.add_argument('--efficiency', action='store_true',
                       help='Enable efficiency mode (Python only)')
    
    args = parser.parse_args()
    
    # Detect language from file extension
    ext = os.path.splitext(args.file)[1].lower()
    lang_map = {
        '.py': 'python',
        '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', '.c++': 'cpp',
        '.c': 'c',
        '.java': 'java',
        '.js': 'javascript', '.mjs': 'javascript',
        '.go': 'go'
    }
    
    detected_lang = args.language or lang_map.get(ext, 'python')
    
    # Display language support banner
    print("\n" + "=" * 70)
    print("🦎 FixGoblin - Universal Auto-Repair System")
    print("=" * 70)
    print(f"📄 File: {args.file}")
    print(f"🌍 Language: {detected_lang.upper()}")
    print(f"🔄 Max Iterations: {args.max_iterations}")
    if detected_lang != 'python':
        print("✨ Using NEW multi-language repair engine!")
    print("=" * 70 + "\n")
    
    # Use universal repair system
    result = universal_repair(
        file_path=args.file,
        max_iterations=args.max_iterations,
        language=detected_lang
    )
    
    # Save log if requested
    if args.log:
        import json
        with open(args.log, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Log saved to: {args.log}")
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main()
