import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from core.multi_language_sandbox import compile_and_run

with open('buggy_cpp.cpp', 'r') as f:
    cpp_code = f.read()

print("=" * 70)
print("ANALYZING BUGGY C++ CODE")
print("=" * 70)

result = compile_and_run(cpp_code, "cpp")

print(f"\n✅ Success: {result['success']}")

if not result['success']:
    print(f"\n❌ Error Type: {result['error_type']}")
    if result['line_number']:
        print(f"📍 Line Number: {result['line_number']}")
    print(f"\n💬 Error Message:")
    print(result['error'])
    
    print("\n" + "=" * 70)
    print("⚠️  FixGoblin detected errors but CANNOT auto-repair C++ code.")
    print("Auto-repair is ONLY available for Python.")
    print("=" * 70)
else:
    print(f"\n📤 Output:")
    print(result['output'])
