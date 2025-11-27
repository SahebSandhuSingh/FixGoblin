#!/usr/bin/env python3
"""
Multi-Language FixGoblin Integration Demo
==========================================
Demonstrates how to use the multi-language sandbox with FixGoblin's
error detection and repair capabilities.

This shows how FixGoblin can be extended to support multiple languages
beyond Python.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from Backend.core.multi_language_sandbox import compile_and_run, get_language_info
import json


def demo_multi_language_execution():
    """Demonstrate multi-language code execution."""
    
    print("=" * 80)
    print("Multi-Language FixGoblin Demo")
    print("=" * 80)
    print()
    
    # Test cases for each language
    test_cases = {
        "python": {
            "correct": "print('Python works!')",
            "buggy": "if x = 5:\n    print(x)"
        },
        "javascript": {
            "correct": "console.log('JavaScript works!');",
            "buggy": "consol.log('Bug');"  # Typo in console
        },
        "c": {
            "correct": """
#include <stdio.h>
int main() {
    printf("C works!\\n");
    return 0;
}
""",
            "buggy": """
#include <stdio.h>
int main() {
    printf("Bug"  // Missing semicolon and closing paren
    return 0;
}
"""
        },
        "cpp": {
            "correct": """
#include <iostream>
int main() {
    std::cout << "C++ works!" << std::endl;
    return 0;
}
""",
            "buggy": """
#include <iostream>
int main() {
    std::cout << "Bug" << std::endl  // Missing semicolon
    return 0;
}
"""
        },
        "java": {
            "correct": """
public class Main {
    public static void main(String[] args) {
        System.out.println("Java works!");
    }
}
""",
            "buggy": """
public class Main {
    public static void main(String[] args) {
        System.out.println("Bug")  // Missing semicolon
    }
}
"""
        },
        "go": {
            "correct": """
package main
import "fmt"
func main() {
    fmt.Println("Go works!")
}
""",
            "buggy": """
package main
import "fmt"
func main() {
    fmt.Println("Bug"  // Missing closing paren
}
"""
        }
    }
    
    # Check available languages
    lang_info = get_language_info()
    available_langs = [lang for lang, info in lang_info.items() if info["available"]]
    
    print(f"Testing {len(available_langs)} available languages:")
    print(f"  {', '.join(available_langs)}")
    print()
    
    # Run tests
    for language in available_langs:
        print(f"\n{'=' * 80}")
        print(f"LANGUAGE: {language.upper()}")
        print(f"{'=' * 80}")
        
        # Test 1: Correct code
        print(f"\n✅ Test 1: Correct {language} code")
        print("-" * 80)
        result = compile_and_run(test_cases[language]["correct"], language)
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Output: {result['output'].strip()}")
        print(f"Execution time: {result['execution_time']:.3f}s")
        
        # Test 2: Buggy code
        print(f"\n❌ Test 2: Buggy {language} code")
        print("-" * 80)
        result = compile_and_run(test_cases[language]["buggy"], language)
        print(f"Success: {result['success']}")
        print(f"Error Type: {result['error_type']}")
        print(f"Line Number: {result['line_number']}")
        print(f"Error Preview: {result['error'][:150]}...")
        print(f"Execution time: {result['execution_time']:.3f}s")
    
    print("\n" + "=" * 80)
    print("✅ Multi-language demo completed!")
    print("=" * 80)


def demo_json_output():
    """Demonstrate JSON output format for API integration."""
    
    print("\n" + "=" * 80)
    print("JSON Output Format Demo (for API integration)")
    print("=" * 80)
    print()
    
    # Test Python code with error
    code = """
def calculate_sum(n):
    total = 0
    for i in range(n)
        total += i
    return total

result = calculate_sum(10)
print(result)
"""
    
    result = compile_and_run(code, "python")
    
    print("Request:")
    print(json.dumps({
        "code": code,
        "language": "python"
    }, indent=2))
    
    print("\nResponse:")
    print(json.dumps(result, indent=2))


def demo_timeout_and_limits():
    """Demonstrate timeout and resource limit handling."""
    
    print("\n" + "=" * 80)
    print("Timeout & Resource Limits Demo")
    print("=" * 80)
    print()
    
    # Infinite loop test
    print("Test 1: Infinite Loop (should timeout)")
    print("-" * 80)
    infinite_loop = """
while True:
    pass
"""
    result = compile_and_run(infinite_loop, "python")
    print(f"Success: {result['success']}")
    print(f"Error Type: {result['error_type']}")
    print(f"Error: {result['error']}")
    print(f"Execution time: {result['execution_time']:.3f}s")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Run all demos
    demo_multi_language_execution()
    demo_json_output()
    demo_timeout_and_limits()
    
    print("\n🎉 All demos completed successfully!")
