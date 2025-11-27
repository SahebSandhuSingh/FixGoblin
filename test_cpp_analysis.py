import sys
import os

# Add Backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from core.multi_language_sandbox import compile_and_run

# Read the C++ file
with open('test_cpp_linkedlist.cpp', 'r') as f:
    cpp_code = f.read()

print("=" * 70)
print("C++ CODE ANALYSIS")
print("=" * 70)

# Run the code
result = compile_and_run(cpp_code, "cpp")

print(f"\n✅ Success: {result['success']}")
print(f"⏱️  Execution Time: {result['execution_time']:.4f}s")

if result['success']:
    print(f"\n📤 Output:")
    print(result['output'])
else:
    print(f"\n❌ Error Type: {result['error_type']}")
    if result['line_number']:
        print(f"📍 Line Number: {result['line_number']}")
    print(f"\n💬 Error Message:")
    print(result['error'])

print("\n" + "=" * 70)
print("NOTE: Auto-repair is only available for Python code.")
print("For C++, you'll see errors but must fix them manually.")
print("=" * 70)
