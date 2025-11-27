"""
Integrated Debugging Pipeline
==============================
Combines Step 1 (Sandbox Execution) and Step 2 (Error Parsing)
to analyze buggy code and extract structured error information.
"""

from sandbox_runner import run_in_sandbox
from error_parser import parse_error, format_error_report
import sys


def debug_code(file_path: str) -> dict:
    """
    Full debugging pipeline: run code in sandbox and parse any errors.
    
    Args:
        file_path: Path to the user's code file
        
    Returns:
        Dictionary containing:
            - sandbox_result: Full output from sandbox execution
            - error_analysis: Structured error information
            - has_error: Boolean indicating if errors were found
    """
    
    print("=" * 70)
    print("AUTONOMOUS DEBUGGING PIPELINE")
    print("=" * 70)
    print(f"\n🔍 Analyzing file: {file_path}\n")
    
    # STEP 1: Run code in sandbox
    print("Step 1: Executing code in sandbox...")
    print("-" * 70)
    sandbox_result = run_in_sandbox(file_path)
    
    print(f"Language: {sandbox_result['language']}")
    print(f"Return Code: {sandbox_result['returncode']}")
    
    if sandbox_result['stdout']:
        print(f"\n📤 STDOUT:\n{sandbox_result['stdout']}")
    
    if sandbox_result['stderr']:
        print(f"\n❌ STDERR:\n{sandbox_result['stderr']}")
    
    print("-" * 70)
    
    # STEP 2: Parse errors if any
    print("\nStep 2: Parsing error signals...")
    print("-" * 70)
    
    error_analysis = parse_error(sandbox_result, file_path)
    
    has_error = error_analysis['error_type'] is not None
    
    if has_error:
        print("\n🐛 BUG DETECTED!\n")
        print(format_error_report(error_analysis))
        
        # Additional analysis
        print("\n📊 Detailed Analysis:")
        print(f"   • Error Type: {error_analysis['error_type']}")
        print(f"   • Location: Line {error_analysis['line_number']}")
        print(f"   • Problem: {error_analysis['error_message']}")
        print(f"   • Faulty Code: {error_analysis['faulty_snippet']}")
    else:
        print("\n✅ No errors detected! Code executed successfully.\n")
    
    print("\n" + "=" * 70)
    
    return {
        "sandbox_result": sandbox_result,
        "error_analysis": error_analysis,
        "has_error": has_error
    }


def main():
    """Command-line interface for the debugging pipeline."""
    if len(sys.argv) < 2:
        print("Usage: python3 debug_pipeline.py <file_path>")
        print("Example: python3 debug_pipeline.py user.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = debug_code(file_path)
    
    # Exit with appropriate code
    sys.exit(1 if result['has_error'] else 0)


if __name__ == "__main__":
    main()
