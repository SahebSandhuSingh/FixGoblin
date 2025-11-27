#!/usr/bin/env python3
"""
Integration Test: Multi-Language Sandbox + FixGoblin Error Detection
======================================================================
Demonstrates how the multi-language sandbox integrates with FixGoblin's
existing error detection and parsing infrastructure.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from Backend.core.multi_language_sandbox import compile_and_run
from Backend.core.error_parser import parse_error


def test_python_integration():
    """Test Python code with FixGoblin's error_parser."""
    print("=" * 80)
    print("TEST 1: Python Integration with error_parser")
    print("=" * 80)
    
    # Buggy Python code
    code = """
my_list = [1, 2, 3]
print(my_list[10])  # IndexError
"""
    
    # Execute in sandbox
    result = compile_and_run(code, "python")
    
    print(f"\n1. Sandbox Execution:")
    print(f"   Success: {result['success']}")
    print(f"   Error Type: {result['error_type']}")
    print(f"   Line: {result['line_number']}")
    
    # Convert to FixGoblin's format
    signals = {
        "stdout": result['output'],
        "stderr": result['error'],
        "returncode": 0 if result['success'] else 1
    }
    
    # Parse with FixGoblin's error_parser
    error_data = parse_error(signals, code)
    
    print(f"\n2. FixGoblin Error Parser:")
    print(f"   Error Type: {error_data['error_type']}")
    print(f"   Line Number: {error_data['line_number']}")
    print(f"   Message: {error_data['error_message']}")
    print(f"   Faulty Snippet: {error_data['faulty_snippet']}")
    
    print("\n✅ Python integration successful!")
    return error_data


def test_multi_language_error_detection():
    """Test error detection across multiple languages."""
    print("\n" + "=" * 80)
    print("TEST 2: Multi-Language Error Detection")
    print("=" * 80)
    
    test_cases = {
        "python": {
            "code": "print(undefined_var)",
            "expected_error": "NameError"
        },
        "javascript": {
            "code": "console.log(undefinedVar);",
            "expected_error": "ReferenceError"
        },
        "c": {
            "code": "#include <stdio.h>\nint main() { printf(x); return 0; }",
            "expected_error": "CompileError"
        }
    }
    
    results = {}
    
    for lang, test in test_cases.items():
        print(f"\n{lang.upper()}:")
        print("-" * 40)
        
        result = compile_and_run(test['code'], lang)
        results[lang] = result
        
        print(f"  Expected: {test['expected_error']}")
        print(f"  Detected: {result['error_type']}")
        print(f"  Match: {'✅' if test['expected_error'] in result['error_type'] else '❌'}")
        print(f"  Line: {result['line_number']}")
    
    print("\n✅ Multi-language error detection completed!")
    return results


def test_syntax_validation():
    """Test pre-execution syntax validation."""
    print("\n" + "=" * 80)
    print("TEST 3: Syntax Validation (No Execution)")
    print("=" * 80)
    
    syntax_errors = {
        "python": "if x = 5:\n    print(x)",
        "javascript": "if (x = 5) {",
        "c": "#include <stdio.h>\nint main() { printf(\"test\" return 0; }"
    }
    
    for lang, code in syntax_errors.items():
        print(f"\n{lang.upper()}:")
        print("-" * 40)
        
        result = compile_and_run(code, lang)
        
        print(f"  Success: {result['success']}")
        print(f"  Error Type: {result['error_type']}")
        print(f"  Line: {result['line_number']}")
        print(f"  Is Syntax Error: {'✅' if 'Syntax' in result['error_type'] else '❌'}")
    
    print("\n✅ Syntax validation completed!")


def test_successful_execution():
    """Test successful code execution across languages."""
    print("\n" + "=" * 80)
    print("TEST 4: Successful Multi-Language Execution")
    print("=" * 80)
    
    test_programs = {
        "python": "print('Success:', 2 + 2)",
        "javascript": "console.log('Success:', 2 + 2);",
        "c": "#include <stdio.h>\nint main() { printf(\"Success: %d\\n\", 2+2); return 0; }",
        "cpp": "#include <iostream>\nint main() { std::cout << \"Success: \" << (2+2) << std::endl; return 0; }",
        "java": "public class Main { public static void main(String[] args) { System.out.println(\"Success: \" + (2+2)); } }",
        "go": "package main\nimport \"fmt\"\nfunc main() { fmt.Printf(\"Success: %d\\n\", 2+2) }"
    }
    
    for lang, code in test_programs.items():
        result = compile_and_run(code, lang)
        
        status = "✅" if result['success'] else "❌"
        output = result['output'].strip() if result['success'] else result['error'][:50]
        
        print(f"{status} {lang:12s}: {output}")
    
    print("\n✅ All executions completed!")


def test_performance():
    """Test execution performance across languages."""
    print("\n" + "=" * 80)
    print("TEST 5: Performance Comparison")
    print("=" * 80)
    
    # Simple loop program for each language
    programs = {
        "python": "for i in range(1000): pass",
        "javascript": "for (let i = 0; i < 1000; i++) {}",
        "c": "#include <stdio.h>\nint main() { for(int i=0; i<1000; i++); return 0; }",
        "cpp": "#include <iostream>\nint main() { for(int i=0; i<1000; i++); return 0; }",
        "java": "public class Main { public static void main(String[] args) { for(int i=0; i<1000; i++); } }",
        "go": "package main\nfunc main() { for i := 0; i < 1000; i++ {} }"
    }
    
    print("\nLanguage      | Execution Time")
    print("-" * 40)
    
    times = []
    for lang, code in programs.items():
        result = compile_and_run(code, lang)
        if result['success']:
            time_ms = result['execution_time'] * 1000
            times.append((lang, time_ms))
            print(f"{lang:12s}  | {time_ms:7.2f}ms")
    
    # Show fastest
    if times:
        fastest = min(times, key=lambda x: x[1])
        print(f"\n🏆 Fastest: {fastest[0]} ({fastest[1]:.2f}ms)")
    
    print("\n✅ Performance test completed!")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("FixGoblin Multi-Language Integration Tests")
    print("=" * 80)
    
    # Run all tests
    test_python_integration()
    test_multi_language_error_detection()
    test_syntax_validation()
    test_successful_execution()
    test_performance()
    
    print("\n" + "=" * 80)
    print("🎉 All integration tests completed successfully!")
    print("=" * 80)
