"""
Error Signal Extraction Module
================================
Parses stderr output from sandbox execution to extract structured error information.
Supports syntax errors, runtime errors, and multi-line tracebacks.
"""

import re
from typing import Dict, Optional, Any


def parse_error(signals: Dict[str, Any], user_code: str) -> Dict[str, Any]:
    """
    Extract structured error information from sandbox execution signals.
    
    Args:
        signals: Dictionary containing stdout, stderr, and returncode from sandbox
        user_code: The original user code (as string or file path)
        
    Returns:
        Dictionary containing:
            - error_type: Type of error (e.g., "SyntaxError", "IndexError")
            - line_number: Line number where error occurred (or None)
            - error_message: The error message text
            - faulty_snippet: The actual line of code that caused the error (or None)
    """
    
    stderr = signals.get("stderr", "")
    returncode = signals.get("returncode", 0)
    
    # If no error occurred, return empty error info
    if returncode == 0 or not stderr.strip():
        return {
            "error_type": None,
            "line_number": None,
            "error_message": None,
            "faulty_snippet": None
        }
    
    # Load user code lines for snippet extraction
    code_lines = _load_code_lines(user_code)
    
    # Try to parse as syntax error first (different format)
    syntax_error = _parse_syntax_error(stderr, code_lines)
    if syntax_error:
        return syntax_error
    
    # Otherwise parse as runtime error
    runtime_error = _parse_runtime_error(stderr, code_lines)
    return runtime_error


def _load_code_lines(user_code: str) -> list:
    """
    Load code lines from string or file path.
    
    Args:
        user_code: Either code as string or path to file
        
    Returns:
        List of code lines
    """
    # Check if it's a file path
    try:
        with open(user_code, 'r', encoding='utf-8') as f:
            return f.readlines()
    except (FileNotFoundError, OSError):
        # Treat as code string
        return user_code.splitlines(keepends=True)


def _parse_syntax_error(stderr: str, code_lines: list) -> Optional[Dict[str, Any]]:
    """
    Parse Python syntax errors which have a special format.
    
    Example format:
      File "main.py", line 3
        if x = 5:
           ^
    SyntaxError: invalid syntax
    
    Also handles:
    - IndentationError
    - TabError
    """
    
    # Check if it's a syntax/indentation error
    if not any(err in stderr for err in ["SyntaxError", "IndentationError", "TabError"]):
        return None
    
    error_info = {
        "error_type": None,
        "line_number": None,
        "error_message": None,
        "faulty_snippet": None
    }
    
    # Extract error type (SyntaxError, IndentationError, TabError, etc.)
    error_type_match = re.search(r'(SyntaxError|IndentationError|TabError):', stderr)
    if error_type_match:
        error_info["error_type"] = error_type_match.group(1)
    
    # Extract line number: File "...", line N
    line_match = re.search(r'File\s+"[^"]+",\s+line\s+(\d+)', stderr)
    if line_match:
        error_info["line_number"] = int(line_match.group(1))
    
    # Extract error message (last line after error type)
    lines = stderr.strip().split('\n')
    for line in reversed(lines):
        if error_info["error_type"] and error_info["error_type"] in line:
            # Get the message after "ErrorType: "
            parts = line.split(':', 1)
            if len(parts) > 1:
                error_info["error_message"] = parts[1].strip()
            else:
                error_info["error_message"] = line.strip()
            break
    
    # Extract faulty code snippet from user code
    if error_info["line_number"] and code_lines:
        line_idx = error_info["line_number"] - 1
        if 0 <= line_idx < len(code_lines):
            error_info["faulty_snippet"] = code_lines[line_idx].rstrip()
    
    return error_info


def _parse_runtime_error(stderr: str, code_lines: list) -> Dict[str, Any]:
    """
    Parse Python runtime errors (IndexError, NameError, ZeroDivisionError, etc.).
    
    Example format:
    Traceback (most recent call last):
      File "main.py", line 5, in <module>
        print(my_list[10])
    IndexError: list index out of range
    """
    
    error_info = {
        "error_type": None,
        "line_number": None,
        "error_message": None,
        "faulty_snippet": None
    }
    
    lines = stderr.strip().split('\n')
    
    # Extract error type and message from last line
    # Format: "ErrorType: message"
    if lines:
        last_line = lines[-1]
        error_match = re.match(r'^(\w+(?:Error|Exception|Warning)):\s*(.*)$', last_line)
        if error_match:
            error_info["error_type"] = error_match.group(1)
            error_info["error_message"] = error_match.group(2).strip()
        else:
            # Sometimes there's just an error type without colon
            if last_line.strip():
                error_info["error_type"] = last_line.strip()
                error_info["error_message"] = last_line.strip()
    
    # Extract line number from traceback
    # Look for: File "...", line N, in ...
    for line in reversed(lines):
        line_match = re.search(r'File\s+"([^"]+)",\s+line\s+(\d+)', line)
        if line_match:
            filename = line_match.group(1)
            # Only capture line number from main.py (user code), not library files
            if "main." in filename or filename.endswith(('.py', '.c', '.cpp', '.java', '.js')):
                error_info["line_number"] = int(line_match.group(2))
                
                # The faulty code snippet is usually on the next line in the traceback
                line_idx = lines.index(line)
                if line_idx + 1 < len(lines):
                    # Extract the code snippet from traceback (it's indented)
                    snippet_line = lines[line_idx + 1].strip()
                    if snippet_line and not snippet_line.startswith('File'):
                        error_info["faulty_snippet"] = snippet_line
                
                break
    
    # If we couldn't find snippet in traceback, extract from user code
    if not error_info["faulty_snippet"] and error_info["line_number"] and code_lines:
        line_idx = error_info["line_number"] - 1
        if 0 <= line_idx < len(code_lines):
            error_info["faulty_snippet"] = code_lines[line_idx].rstrip()
    
    return error_info


def format_error_report(error_info: Dict[str, Any]) -> str:
    """
    Format error information into a human-readable report.
    
    Args:
        error_info: Dictionary from parse_error()
        
    Returns:
        Formatted string report
    """
    if not error_info["error_type"]:
        return "No error detected."
    
    report = []
    report.append("=" * 60)
    report.append("ERROR ANALYSIS")
    report.append("=" * 60)
    
    if error_info["error_type"]:
        report.append(f"Error Type: {error_info['error_type']}")
    
    if error_info["line_number"]:
        report.append(f"Line Number: {error_info['line_number']}")
    
    if error_info["error_message"]:
        report.append(f"Message: {error_info['error_message']}")
    
    if error_info["faulty_snippet"]:
        report.append(f"\nFaulty Code:")
        report.append(f"  {error_info['faulty_snippet']}")
    
    report.append("=" * 60)
    
    return "\n".join(report)


# ---------------------------------------------
#  Test/Demo Section
# ---------------------------------------------
if __name__ == "__main__":
    # Test Case 1: Runtime Error (IndexError)
    test_signals_1 = {
        "stdout": "",
        "stderr": """Traceback (most recent call last):
  File "main.py", line 3, in <module>
    print(my_list[10])
IndexError: list index out of range""",
        "returncode": 1
    }
    
    test_code_1 = """my_list = [1, 2, 3]
x = 5
print(my_list[10])
"""
    
    print("TEST 1: Runtime Error (IndexError)")
    print("-" * 60)
    result_1 = parse_error(test_signals_1, test_code_1)
    print(format_error_report(result_1))
    print("\nParsed Data:", result_1)
    print("\n\n")
    
    # Test Case 2: Syntax Error
    test_signals_2 = {
        "stdout": "",
        "stderr": """  File "main.py", line 2
    if x = 5:
       ^
SyntaxError: invalid syntax""",
        "returncode": 1
    }
    
    test_code_2 = """x = 10
if x = 5:
    print("test")
"""
    
    print("TEST 2: Syntax Error")
    print("-" * 60)
    result_2 = parse_error(test_signals_2, test_code_2)
    print(format_error_report(result_2))
    print("\nParsed Data:", result_2)
    print("\n\n")
    
    # Test Case 3: NameError
    test_signals_3 = {
        "stdout": "",
        "stderr": """Traceback (most recent call last):
  File "main.py", line 2, in <module>
    result = undefined_var + 10
NameError: name 'undefined_var' is not defined""",
        "returncode": 1
    }
    
    test_code_3 = """x = 5
result = undefined_var + 10
print(result)
"""
    
    print("TEST 3: NameError")
    print("-" * 60)
    result_3 = parse_error(test_signals_3, test_code_3)
    print(format_error_report(result_3))
    print("\nParsed Data:", result_3)
    print("\n\n")
    
    # Test Case 4: No Error
    test_signals_4 = {
        "stdout": "Success!",
        "stderr": "",
        "returncode": 0
    }
    
    test_code_4 = """print("Success!")"""
    
    print("TEST 4: No Error")
    print("-" * 60)
    result_4 = parse_error(test_signals_4, test_code_4)
    print(format_error_report(result_4))
    print("\nParsed Data:", result_4)
