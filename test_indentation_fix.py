"""
Test script to verify indentation error detection and fixing
"""

# Test Case 1: Missing indentation after colon
test_code_1 = """
def calculate_sum(a, b):
result = a + b
return result
"""

# Test Case 2: Unexpected indent
test_code_2 = """
def greet(name):
    print("Hello")
        print(name)
"""

# Test Case 3: Mixed tabs and spaces
test_code_3 = """
def process_data(data):
    for item in data:
\t\tif item > 0:
            print(item)
"""

# Test Case 4: Unindent does not match
test_code_4 = """
def check_value(x):
    if x > 0:
        print("positive")
      print("done")
"""

# Test Case 5: Expected an indented block
test_code_5 = """
def do_nothing():
print("This should be indented")
"""

import sys
import os

# Add Backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from core.autonomous_repair import autonomous_repair
import tempfile

def test_indentation_fix(test_name, code):
    """Test indentation fix on given code"""
    print("=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)
    print("\nOriginal Code:")
    print(code)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # Run autonomous repair
        result = autonomous_repair(temp_file, max_iterations=3)
        
        print(f"\nResult: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        print(f"Iterations: {result['total_iterations']}")
        print(f"Reason: {result['reason']}")
        
        if result['iterations']:
            print("\nFixed Code:")
            with open(temp_file, 'r', encoding='utf-8') as f:
                print(f.read())
        
        return result['success']
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("INDENTATION ERROR DETECTION AND FIXING TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Missing indentation after colon", test_code_1),
        ("Unexpected indent", test_code_2),
        ("Mixed tabs and spaces", test_code_3),
        ("Unindent does not match", test_code_4),
        ("Expected an indented block", test_code_5),
    ]
    
    results = []
    for test_name, code in tests:
        success = test_indentation_fix(test_name, code)
        results.append((test_name, success))
        print("\n")
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 70)
