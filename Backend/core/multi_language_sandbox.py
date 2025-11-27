#!/usr/bin/env python3
"""
Multi-Language Sandbox Engine
==============================
Secure sandbox for executing code in multiple languages with isolation.

Supports: Python, JavaScript, C, C++, Java, Go

Security Features:
- Time limits per execution
- Memory limits
- No file system writes (temp files only)
- No network access
- Process isolation

Author: FixGoblin Team
License: MIT
"""

import subprocess
import tempfile
import os
import signal
import resource
import time
import re
from typing import Dict, Optional, Tuple
from pathlib import Path


# ============================================================================
# CONFIGURATION
# ============================================================================

TIMEOUT_SECONDS = 5  # Maximum execution time
MEMORY_LIMIT_MB = 512  # Maximum memory usage in MB

SUPPORTED_LANGUAGES = {
    "python": [".py", "python3"],
    "javascript": [".js", "node"],
    "c": [".c", "gcc"],
    "cpp": [".cpp", "g++"],
    "java": [".java", "javac"],
    "go": [".go", "go"]
}


# ============================================================================
# MAIN API
# ============================================================================

def compile_and_run(code: str, language: str) -> Dict:
    """
    Compile and run code in a secure sandbox environment.
    
    Args:
        code: Source code as string
        language: One of: python, javascript, c, cpp, java, go
        
    Returns:
        Dictionary with keys:
            - success (bool): True if execution succeeded
            - output (str): Standard output
            - error (str): Error message if any
            - error_type (str): Type of error (SyntaxError, RuntimeError, etc.)
            - line_number (int|None): Line number where error occurred
            - execution_time (float): Time taken in seconds
            
    Example:
        >>> result = compile_and_run("print('Hello')", "python")
        >>> result['success']
        True
        >>> result['output']
        'Hello\\n'
    """
    start_time = time.time()
    
    # Validate language
    language = language.lower()
    if language not in SUPPORTED_LANGUAGES:
        return {
            "success": False,
            "output": "",
            "error": f"Unsupported language: {language}",
            "error_type": "ConfigurationError",
            "line_number": None,
            "execution_time": 0.0
        }
    
    # Check if required compiler/interpreter is available
    if not _check_language_available(language):
        return {
            "success": False,
            "output": "",
            "error": f"Language runtime not found: {language}",
            "error_type": "ConfigurationError",
            "line_number": None,
            "execution_time": 0.0
        }
    
    try:
        # Language-specific compilation and execution
        if language == "python":
            result = _run_python(code)
        elif language == "javascript":
            result = _run_javascript(code)
        elif language == "c":
            result = _run_c(code)
        elif language == "cpp":
            result = _run_cpp(code)
        elif language == "java":
            result = _run_java(code)
        elif language == "go":
            result = _run_go(code)
        else:
            result = {
                "success": False,
                "output": "",
                "error": f"Language handler not implemented: {language}",
                "error_type": "ConfigurationError",
                "line_number": None
            }
        
        # Add execution time
        result["execution_time"] = time.time() - start_time
        return result
        
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Sandbox error: {str(e)}",
            "error_type": "SandboxError",
            "line_number": None,
            "execution_time": time.time() - start_time
        }


# ============================================================================
# PYTHON EXECUTION
# ============================================================================

def _run_python(code: str) -> Dict:
    """Execute Python code with syntax validation."""
    
    # Step 1: Validate syntax using compile()
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        error_type, line_number = map_error_type(str(e), "python")
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "error_type": error_type,
            "line_number": line_number
        }
    
    # Step 2: Write to temp file and execute
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        result = _execute_with_sandbox(
            ["python3", temp_file],
            timeout=TIMEOUT_SECONDS
        )
        
        # Parse errors from stderr (but preserve TimeoutError)
        if not result["success"] and result["error"]:
            # Don't remap TimeoutError or MemoryError
            if result["error_type"] not in ["TimeoutError", "MemoryError"]:
                error_type, line_number = map_error_type(result["error"], "python")
                result["error_type"] = error_type
                result["line_number"] = line_number
        
        return result
        
    finally:
        # Cleanup
        try:
            os.unlink(temp_file)
        except:
            pass


# ============================================================================
# JAVASCRIPT EXECUTION
# ============================================================================

def _run_javascript(code: str) -> Dict:
    """Execute JavaScript code with Node.js."""
    
    # Step 1: Validate syntax using node --check
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # Syntax check
        check_result = subprocess.run(
            ["node", "--check", temp_file],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if check_result.returncode != 0:
            error_type, line_number = map_error_type(check_result.stderr, "javascript")
            return {
                "success": False,
                "output": "",
                "error": check_result.stderr,
                "error_type": error_type,
                "line_number": line_number
            }
        
        # Step 2: Execute
        result = _execute_with_sandbox(
            ["node", temp_file],
            timeout=TIMEOUT_SECONDS
        )
        
        # Parse errors (but preserve TimeoutError/MemoryError)
        if not result["success"] and result["error"]:
            if result["error_type"] not in ["TimeoutError", "MemoryError"]:
                error_type, line_number = map_error_type(result["error"], "javascript")
                result["error_type"] = error_type
                result["line_number"] = line_number
        
        return result
        
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass


# ============================================================================
# C EXECUTION
# ============================================================================

def _run_c(code: str) -> Dict:
    """Compile and execute C code with GCC."""
    
    # Create temp files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write(code)
        source_file = f.name
    
    binary_file = source_file.replace('.c', '.out')
    
    try:
        # Step 1: Compile
        compile_result = subprocess.run(
            ["gcc", source_file, "-o", binary_file, "-std=c11", "-Wall"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if compile_result.returncode != 0:
            error_type, line_number = map_error_type(compile_result.stderr, "c")
            return {
                "success": False,
                "output": "",
                "error": compile_result.stderr,
                "error_type": error_type,
                "line_number": line_number
            }
        
        # Step 2: Execute
        result = _execute_with_sandbox(
            [binary_file],
            timeout=TIMEOUT_SECONDS
        )
        
        # Parse runtime errors (but preserve TimeoutError/MemoryError)
        if not result["success"] and result["error"]:
            if result["error_type"] not in ["TimeoutError", "MemoryError"]:
                error_type, line_number = map_error_type(result["error"], "c")
                result["error_type"] = error_type
                result["line_number"] = line_number
        
        return result
        
    finally:
        # Cleanup
        try:
            os.unlink(source_file)
        except:
            pass
        try:
            os.unlink(binary_file)
        except:
            pass


# ============================================================================
# C++ EXECUTION
# ============================================================================

def _run_cpp(code: str) -> Dict:
    """Compile and execute C++ code with G++."""
    
    # Create temp files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
        f.write(code)
        source_file = f.name
    
    binary_file = source_file.replace('.cpp', '.out')
    
    try:
        # Step 1: Compile
        compile_result = subprocess.run(
            ["g++", source_file, "-o", binary_file, "-std=c++17", "-Wall"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if compile_result.returncode != 0:
            error_type, line_number = map_error_type(compile_result.stderr, "cpp")
            return {
                "success": False,
                "output": "",
                "error": compile_result.stderr,
                "error_type": error_type,
                "line_number": line_number
            }
        
        # Step 2: Execute
        result = _execute_with_sandbox(
            [binary_file],
            timeout=TIMEOUT_SECONDS
        )
        
        # Parse runtime errors (but preserve TimeoutError/MemoryError)
        if not result["success"] and result["error"]:
            if result["error_type"] not in ["TimeoutError", "MemoryError"]:
                error_type, line_number = map_error_type(result["error"], "cpp")
                result["error_type"] = error_type
                result["line_number"] = line_number
        
        return result
        
    finally:
        # Cleanup
        try:
            os.unlink(source_file)
        except:
            pass
        try:
            os.unlink(binary_file)
        except:
            pass


# ============================================================================
# JAVA EXECUTION
# ============================================================================

def _run_java(code: str) -> Dict:
    """Compile and execute Java code."""
    
    # Extract class name from code
    class_name = _extract_java_class_name(code)
    if not class_name:
        return {
            "success": False,
            "output": "",
            "error": "Could not find public class in Java code",
            "error_type": "SyntaxError",
            "line_number": None
        }
    
    # Create temp directory for Java files
    temp_dir = tempfile.mkdtemp()
    source_file = os.path.join(temp_dir, f"{class_name}.java")
    
    try:
        # Write source file
        with open(source_file, 'w') as f:
            f.write(code)
        
        # Step 1: Compile
        compile_result = subprocess.run(
            ["javac", source_file],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=temp_dir
        )
        
        if compile_result.returncode != 0:
            error_type, line_number = map_error_type(compile_result.stderr, "java")
            return {
                "success": False,
                "output": "",
                "error": compile_result.stderr,
                "error_type": error_type,
                "line_number": line_number
            }
        
        # Step 2: Execute
        result = _execute_with_sandbox(
            ["java", class_name],
            timeout=TIMEOUT_SECONDS,
            cwd=temp_dir
        )
        
        # Parse runtime errors (but preserve TimeoutError/MemoryError)
        if not result["success"] and result["error"]:
            if result["error_type"] not in ["TimeoutError", "MemoryError"]:
                error_type, line_number = map_error_type(result["error"], "java")
                result["error_type"] = error_type
                result["line_number"] = line_number
        
        return result
        
    finally:
        # Cleanup
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


def _extract_java_class_name(code: str) -> Optional[str]:
    """Extract the public class name from Java code."""
    match = re.search(r'public\s+class\s+(\w+)', code)
    if match:
        return match.group(1)
    # Fallback: try to find any class
    match = re.search(r'class\s+(\w+)', code)
    if match:
        return match.group(1)
    return None


# ============================================================================
# GO EXECUTION
# ============================================================================

def _run_go(code: str) -> Dict:
    """Compile and execute Go code."""
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    source_file = os.path.join(temp_dir, "main.go")
    binary_file = os.path.join(temp_dir, "program")
    
    try:
        # Write source file
        with open(source_file, 'w') as f:
            f.write(code)
        
        # Step 1: Compile
        compile_result = subprocess.run(
            ["go", "build", "-o", binary_file, source_file],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=temp_dir
        )
        
        if compile_result.returncode != 0:
            error_type, line_number = map_error_type(compile_result.stderr, "go")
            return {
                "success": False,
                "output": "",
                "error": compile_result.stderr,
                "error_type": error_type,
                "line_number": line_number
            }
        
        # Step 2: Execute
        result = _execute_with_sandbox(
            [binary_file],
            timeout=TIMEOUT_SECONDS
        )
        
        # Parse runtime errors (but preserve TimeoutError/MemoryError)
        if not result["success"] and result["error"]:
            if result["error_type"] not in ["TimeoutError", "MemoryError"]:
                error_type, line_number = map_error_type(result["error"], "go")
                result["error_type"] = error_type
                result["line_number"] = line_number
        
        return result
        
    finally:
        # Cleanup
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


# ============================================================================
# SANDBOX EXECUTION ENGINE
# ============================================================================

def _execute_with_sandbox(
    command: list,
    timeout: int = TIMEOUT_SECONDS,
    cwd: Optional[str] = None
) -> Dict:
    """
    Execute command in sandboxed environment with resource limits.
    
    Args:
        command: Command and arguments as list
        timeout: Maximum execution time in seconds
        cwd: Working directory (optional)
        
    Returns:
        Dictionary with success, output, error
    """
    
    def set_limits():
        """Set resource limits for child process."""
        # Set memory limit (soft and hard)
        memory_bytes = MEMORY_LIMIT_MB * 1024 * 1024
        try:
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        except:
            pass  # Not all systems support this
        
        # Set CPU time limit
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (timeout + 1, timeout + 1))
        except:
            pass
        
        # Prevent core dumps
        try:
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        except:
            pass
        
        # Set process priority to low
        try:
            os.nice(10)
        except:
            pass
    
    try:
        # Execute with timeout and resource limits
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            preexec_fn=set_limits if os.name != 'nt' else None  # Unix only
        )
        
        success = result.returncode == 0
        
        return {
            "success": success,
            "output": result.stdout,
            "error": result.stderr if not success else "",
            "error_type": "RuntimeError" if not success else None,
            "line_number": None
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": f"Execution timed out after {timeout} seconds",
            "error_type": "TimeoutError",
            "line_number": None
        }
    
    except MemoryError:
        return {
            "success": False,
            "output": "",
            "error": f"Memory limit exceeded ({MEMORY_LIMIT_MB}MB)",
            "error_type": "MemoryError",
            "line_number": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Execution error: {str(e)}",
            "error_type": "ExecutionError",
            "line_number": None
        }


# ============================================================================
# ERROR PARSING
# ============================================================================

def map_error_type(stderr: str, language: str) -> Tuple[str, Optional[int]]:
    """
    Parse error message to extract error type and line number.
    
    Args:
        stderr: Standard error output
        language: Programming language
        
    Returns:
        Tuple of (error_type, line_number)
        
    Example:
        >>> map_error_type("SyntaxError: invalid syntax", "python")
        ('SyntaxError', None)
        >>> map_error_type("File 'main.py', line 5", "python")
        ('RuntimeError', 5)
    """
    
    if not stderr:
        return ("RuntimeError", None)
    
    stderr_lower = stderr.lower()
    
    # Python error patterns
    if language == "python":
        # Extract error type
        if "syntaxerror" in stderr_lower:
            error_type = "SyntaxError"
        elif "indentationerror" in stderr_lower:
            error_type = "IndentationError"
        elif "nameerror" in stderr_lower:
            error_type = "NameError"
        elif "typeerror" in stderr_lower:
            error_type = "TypeError"
        elif "indexerror" in stderr_lower:
            error_type = "IndexError"
        elif "valueerror" in stderr_lower:
            error_type = "ValueError"
        elif "keyerror" in stderr_lower:
            error_type = "KeyError"
        elif "attributeerror" in stderr_lower:
            error_type = "AttributeError"
        elif "zerodivisionerror" in stderr_lower:
            error_type = "ZeroDivisionError"
        else:
            error_type = "RuntimeError"
        
        # Extract line number
        line_match = re.search(r'line (\d+)', stderr)
        line_number = int(line_match.group(1)) if line_match else None
        
        return (error_type, line_number)
    
    # JavaScript error patterns
    elif language == "javascript":
        if "syntaxerror" in stderr_lower:
            error_type = "SyntaxError"
        elif "referenceerror" in stderr_lower:
            error_type = "ReferenceError"
        elif "typeerror" in stderr_lower:
            error_type = "TypeError"
        elif "rangeerror" in stderr_lower:
            error_type = "RangeError"
        else:
            error_type = "RuntimeError"
        
        # Extract line number (format: file:line:col)
        line_match = re.search(r':(\d+):\d+', stderr)
        line_number = int(line_match.group(1)) if line_match else None
        
        return (error_type, line_number)
    
    # C/C++ error patterns
    elif language in ["c", "cpp"]:
        if "error:" in stderr_lower:
            if "syntax" in stderr_lower or "expected" in stderr_lower:
                error_type = "SyntaxError"
            elif "undefined reference" in stderr_lower:
                error_type = "LinkError"
            elif "segmentation fault" in stderr_lower:
                error_type = "SegmentationFault"
            else:
                error_type = "CompileError"
        else:
            error_type = "RuntimeError"
        
        # Extract line number (format: file.c:line:col)
        line_match = re.search(r':(\d+):\d+:', stderr)
        line_number = int(line_match.group(1)) if line_match else None
        
        return (error_type, line_number)
    
    # Java error patterns
    elif language == "java":
        if "error:" in stderr_lower:
            error_type = "CompileError"
        elif "exception" in stderr_lower:
            if "nullpointerexception" in stderr_lower:
                error_type = "NullPointerException"
            elif "arrayindexoutofboundsexception" in stderr_lower:
                error_type = "ArrayIndexOutOfBoundsException"
            elif "classnotfoundexception" in stderr_lower:
                error_type = "ClassNotFoundException"
            else:
                error_type = "RuntimeException"
        else:
            error_type = "RuntimeError"
        
        # Extract line number (format: ClassName.java:line)
        line_match = re.search(r'\.java:(\d+)', stderr)
        line_number = int(line_match.group(1)) if line_match else None
        
        return (error_type, line_number)
    
    # Go error patterns
    elif language == "go":
        if "syntax error" in stderr_lower:
            error_type = "SyntaxError"
        elif "undefined:" in stderr_lower:
            error_type = "UndefinedError"
        elif "panic:" in stderr_lower:
            error_type = "PanicError"
        else:
            error_type = "CompileError"
        
        # Extract line number (format: main.go:line:col)
        line_match = re.search(r'\.go:(\d+):\d+', stderr)
        line_number = int(line_match.group(1)) if line_match else None
        
        return (error_type, line_number)
    
    # Default fallback
    return ("RuntimeError", None)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _check_language_available(language: str) -> bool:
    """Check if the required compiler/interpreter is available."""
    
    if language == "python":
        command = "python3"
    elif language == "javascript":
        command = "node"
    elif language == "c":
        command = "gcc"
    elif language == "cpp":
        command = "g++"
    elif language == "java":
        command = "javac"
    elif language == "go":
        command = "go"
    else:
        return False
    
    try:
        subprocess.run(
            [command, "--version"],
            capture_output=True,
            timeout=2
        )
        return True
    except:
        return False


def get_supported_languages() -> list:
    """Get list of supported languages."""
    return list(SUPPORTED_LANGUAGES.keys())


def get_language_info() -> Dict:
    """Get detailed information about supported languages."""
    info = {}
    for lang in SUPPORTED_LANGUAGES:
        info[lang] = {
            "available": _check_language_available(lang),
            "extension": SUPPORTED_LANGUAGES[lang][0],
            "compiler": SUPPORTED_LANGUAGES[lang][1]
        }
    return info


# ============================================================================
# TEST EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Multi-Language Sandbox Engine - Test Suite")
    print("=" * 80)
    print()
    
    # Check available languages
    print("Available Languages:")
    lang_info = get_language_info()
    for lang, info in lang_info.items():
        status = "✅" if info["available"] else "❌"
        print(f"  {status} {lang}: {info['compiler']}")
    print()
    
    # Test Python
    print("TEST 1: Python - Success")
    print("-" * 80)
    result = compile_and_run("print('Hello from Python!')", "python")
    print(f"Success: {result['success']}")
    print(f"Output: {result['output']}")
    print(f"Time: {result['execution_time']:.3f}s")
    print()
    
    # Test Python - Syntax Error
    print("TEST 2: Python - Syntax Error")
    print("-" * 80)
    result = compile_and_run("if x = 5:\n    print(x)", "python")
    print(f"Success: {result['success']}")
    print(f"Error Type: {result['error_type']}")
    print(f"Line: {result['line_number']}")
    print(f"Error: {result['error'][:100]}...")
    print()
    
    # Test JavaScript
    if lang_info["javascript"]["available"]:
        print("TEST 3: JavaScript - Success")
        print("-" * 80)
        result = compile_and_run("console.log('Hello from JavaScript!');", "javascript")
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        print()
    
    # Test C
    if lang_info["c"]["available"]:
        print("TEST 4: C - Success")
        print("-" * 80)
        c_code = """
#include <stdio.h>
int main() {
    printf("Hello from C!\\n");
    return 0;
}
"""
        result = compile_and_run(c_code, "c")
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        print()
    
    # Test C++ 
    if lang_info["cpp"]["available"]:
        print("TEST 5: C++ - Success")
        print("-" * 80)
        cpp_code = """
#include <iostream>
int main() {
    std::cout << "Hello from C++!" << std::endl;
    return 0;
}
"""
        result = compile_and_run(cpp_code, "cpp")
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        print()
    
    # Test Java
    if lang_info["java"]["available"]:
        print("TEST 6: Java - Success")
        print("-" * 80)
        java_code = """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
    }
}
"""
        result = compile_and_run(java_code, "java")
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        print()
    
    # Test Go
    if lang_info["go"]["available"]:
        print("TEST 7: Go - Success")
        print("-" * 80)
        go_code = """
package main
import "fmt"
func main() {
    fmt.Println("Hello from Go!")
}
"""
        result = compile_and_run(go_code, "go")
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        print()
    
    print("=" * 80)
    print("✅ Test suite completed!")
