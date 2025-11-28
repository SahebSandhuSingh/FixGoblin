"""
QUICK REFERENCE: Multi-Language Sandbox
========================================

IMPORT
------
from Backend.core.multi_language_sandbox import compile_and_run, map_error_type, get_language_info

BASIC USAGE
-----------
result = compile_and_run(code, language)

SUPPORTED LANGUAGES
-------------------
• python
• javascript  
• c
• cpp
• java
• go

RETURN FORMAT
-------------
{
    "success": bool,
    "output": str,
    "error": str, 
    "error_type": str,
    "line_number": int|None,
    "execution_time": float
}

EXAMPLES
--------

# Python
compile_and_run("print('Hello')", "python")

# JavaScript
compile_and_run("console.log('Hello');", "javascript")

# C
compile_and_run('''
#include <stdio.h>
int main() { printf("Hello\\n"); return 0; }
''', "c")

# C++
compile_and_run('''
#include <iostream>
int main() { std::cout << "Hello" << std::endl; return 0; }
''', "cpp")

# Java
compile_and_run('''
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
''', "java")

# Go
compile_and_run('''
package main
import "fmt"
func main() { fmt.Println("Hello") }
''', "go")

ERROR HANDLING
--------------
result = compile_and_run(buggy_code, "python")
if not result['success']:
    print(f"{result['error_type']} at line {result['line_number']}")
    print(result['error'])

CONFIGURATION
-------------
Edit in multi_language_sandbox.py:
    TIMEOUT_SECONDS = 5      # Max execution time
    MEMORY_LIMIT_MB = 512    # Max memory

SECURITY FEATURES
-----------------
✓ Time limit (5s default)
✓ Memory limit (512MB)
✓ Process isolation
✓ Temp file execution only
✓ Auto cleanup

CHECK AVAILABILITY
------------------
info = get_language_info()
for lang, data in info.items():
    if data['available']:
        print(f"✓ {lang}")

TESTING
-------
# Run test suite
python3 Backend/core/multi_language_sandbox.py

# Run demos
python3 demo_multi_language.py

# Run integration tests
python3 test_multi_language_integration.py

COMMON ERROR TYPES
------------------
Python:      SyntaxError, NameError, IndexError, TypeError
JavaScript:  SyntaxError, ReferenceError, TypeError
C/C++:       SyntaxError, CompileError, SegmentationFault
Java:        CompileError, NullPointerException, RuntimeException
Go:          SyntaxError, PanicError, UndefinedError

INTEGRATION WITH FIXGOBLIN
--------------------------
from Backend.core.error_parser import parse_error

result = compile_and_run(code, "python")
signals = {
    "stdout": result['output'],
    "stderr": result['error'],
    "returncode": 0 if result['success'] else 1
}
error_data = parse_error(signals, code)

TIPS
----
• Always check result['success'] first
• Use get_language_info() to verify compiler availability
• Errors include line numbers when available
• Timeout errors have error_type='TimeoutError'
• Syntax errors caught before execution (when possible)

TROUBLESHOOTING
---------------
Missing compiler? Install:
  macOS:   brew install node gcc java go
  Linux:   sudo apt install nodejs gcc default-jdk golang

Import error? Check path:
  sys.path.insert(0, '/path/to/FixGoblin')

Timeout too short? Adjust:
  TIMEOUT_SECONDS = 10  # in multi_language_sandbox.py
"""
