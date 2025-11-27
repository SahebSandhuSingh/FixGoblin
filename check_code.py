#!/usr/bin/env python3
"""
Quick C++/Java/JS Error Checker
Just detects errors - you fix them manually
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from core.multi_language_sandbox import compile_and_run

def check_code(file_path):
    """Check code for errors (works for C++, Java, JS, Go, C)"""
    
    # Detect language from extension
    ext_to_lang = {
        '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
        '.c': 'c',
        '.java': 'java',
        '.js': 'javascript',
        '.go': 'go',
        '.py': 'python'
    }
    
    ext = os.path.splitext(file_path)[1]
    language = ext_to_lang.get(ext)
    
    if not language:
        print(f"❌ Unsupported file type: {ext}")
        return
    
    # Read the code
    with open(file_path, 'r') as f:
        code = f.read()
    
    print("=" * 70)
    print(f"🔍 ANALYZING {language.upper()} CODE: {file_path}")
    print("=" * 70)
    
    # Run it
    result = compile_and_run(code, language)
    
    if result['success']:
        print("\n✅ SUCCESS - No errors found!")
        print(f"⏱️  Execution time: {result['execution_time']:.4f}s")
        print(f"\n📤 Output:\n{result['output']}")
    else:
        print("\n❌ ERRORS DETECTED")
        print(f"🐛 Error Type: {result['error_type']}")
        if result['line_number']:
            print(f"📍 Line: {result['line_number']}")
        print(f"\n💬 Error Details:\n{result['error']}")
        print("\n⚠️  Fix the errors manually - auto-repair only works for Python!")
    
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 check_code.py <file.cpp|.java|.js|.c|.go|.py>")
        print("\nExample:")
        print("  python3 check_code.py test.cpp")
        print("  python3 check_code.py MyClass.java")
        print("  python3 check_code.py app.js")
        sys.exit(1)
    
    check_code(sys.argv[1])
