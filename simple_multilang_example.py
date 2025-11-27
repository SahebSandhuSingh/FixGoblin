#!/usr/bin/env python3
"""
Simple Multi-Language Example
==============================
The easiest way to get started with FixGoblin's multi-language sandbox.
"""

from Backend.core.multi_language_sandbox import compile_and_run

# Example 1: Python
print("=" * 60)
print("Example 1: Python")
print("=" * 60)
result = compile_and_run("print('Hello from Python!')", "python")
print(f"Success: {result['success']}")
print(f"Output: {result['output']}")

# Example 2: JavaScript
print("\n" + "=" * 60)
print("Example 2: JavaScript")
print("=" * 60)
result = compile_and_run("console.log('Hello from JS!');", "javascript")
print(f"Success: {result['success']}")
print(f"Output: {result['output']}")

# Example 3: Error Detection
print("\n" + "=" * 60)
print("Example 3: Error Detection (Python)")
print("=" * 60)
buggy_code = """
def divide(a, b):
    return a / b

result = divide(10, 0)  # ZeroDivisionError!
print(result)
"""
result = compile_and_run(buggy_code, "python")
print(f"Success: {result['success']}")
print(f"Error Type: {result['error_type']}")
print(f"Line Number: {result['line_number']}")
print(f"Error: {result['error'][:80]}...")

# Example 4: Syntax Error
print("\n" + "=" * 60)
print("Example 4: Syntax Error Detection")
print("=" * 60)
result = compile_and_run("if x = 5:\n    print(x)", "python")
print(f"Success: {result['success']}")
print(f"Error Type: {result['error_type']}")
print(f"Line Number: {result['line_number']}")

print("\n✅ Done! That's how easy it is to use the multi-language sandbox!")
