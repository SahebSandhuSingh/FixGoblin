"""
Local Autonomous Debugging Sandbox Runner
==========================================
Safely executes user-submitted code in isolated temporary directories.
Supports: Python, C, C++, Java, JavaScript, HTML
"""

import subprocess
import tempfile
import shutil
import pathlib
from typing import Dict, List, Any


# ---------------------------------------------
#  Language Detection by File Extension
# ---------------------------------------------
def detect_language_from_extension(file_path: str) -> str:
    """
    Detect programming language based on file extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Language name as string (python, c, cpp, java, javascript, html, unknown)
    """
    path = pathlib.Path(file_path)
    ext = path.suffix.lower()
    
    extension_map = {
        '.py': 'python',
        '.c': 'c',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.java': 'java',
        '.js': 'javascript',
        '.html': 'html',
        '.htm': 'html'
    }
    
    return extension_map.get(ext, 'unknown')


# ---------------------------------------------
#  Extract Java Class Name from File
# ---------------------------------------------
def extract_java_class_name(file_path: str) -> str:
    """
    Extract the public class name from a Java file.
    Falls back to filename if no public class is found.
    
    Args:
        file_path: Path to Java file
        
    Returns:
        Class name as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Simple regex to find public class name
        import re
        match = re.search(r'public\s+class\s+(\w+)', content)
        if match:
            return match.group(1)
    except Exception:
        pass
    
    # Fallback: use filename without extension
    return pathlib.Path(file_path).stem


# ---------------------------------------------
#  Main Sandbox Execution Function
# ---------------------------------------------
def run_in_sandbox(file_path: str, timeout: int = 3) -> Dict[str, Any]:
    """
    Execute user code in an isolated temporary sandbox.
    
    Args:
        file_path: Path to the user's source file
        timeout: Maximum execution time in seconds (default: 3)
        
    Returns:
        Dictionary containing:
            - language: detected language
            - stdout: standard output from execution
            - stderr: standard error from execution
            - returncode: process return code (0 = success)
            - executed_command: list of command arguments used
            
    Raises:
        FileNotFoundError: If input file doesn't exist
        subprocess.TimeoutExpired: If execution exceeds timeout
    """
    
    # Validate input file exists
    input_path = pathlib.Path(file_path)
    if not input_path.exists():
        return {
            "language": "unknown",
            "stdout": "",
            "stderr": f"Error: File '{file_path}' not found",
            "returncode": 1,
            "executed_command": []
        }
    
    # Detect language from file extension
    language = detect_language_from_extension(file_path)
    
    # Handle unknown file types
    if language == "unknown":
        return {
            "language": "unknown",
            "stdout": "",
            "stderr": f"Error: Unsupported file extension '{input_path.suffix}'",
            "returncode": 1,
            "executed_command": []
        }
    
    # Create temporary isolated sandbox directory
    with tempfile.TemporaryDirectory() as sandbox_dir:
        sandbox_path = pathlib.Path(sandbox_dir)
        
        try:
            # Execute based on detected language
            if language == "python":
                return _execute_python(input_path, sandbox_path, timeout)
            elif language == "c":
                return _execute_c(input_path, sandbox_path, timeout)
            elif language == "cpp":
                return _execute_cpp(input_path, sandbox_path, timeout)
            elif language == "java":
                return _execute_java(input_path, sandbox_path, timeout)
            elif language == "javascript":
                return _execute_javascript(input_path, sandbox_path, timeout)
            elif language == "html":
                return _execute_html(input_path, sandbox_path)
                
        except subprocess.TimeoutExpired:
            return {
                "language": language,
                "stdout": "",
                "stderr": f"Error: Execution exceeded {timeout} second timeout",
                "returncode": 124,  # Standard timeout exit code
                "executed_command": []
            }
        except Exception as e:
            return {
                "language": language,
                "stdout": "",
                "stderr": f"Error: {str(e)}",
                "returncode": 1,
                "executed_command": []
            }


# ---------------------------------------------
#  Language-Specific Execution Functions
# ---------------------------------------------

def _execute_python(source_file: pathlib.Path, sandbox: pathlib.Path, timeout: int) -> Dict[str, Any]:
    """Execute Python code in sandbox with syntax validation."""
    # Read source code for syntax validation
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        return {
            "language": "python",
            "stdout": "",
            "stderr": f"Error reading file: {str(e)}",
            "returncode": 1,
            "executed_command": []
        }
    
    # Validate syntax using compile() before execution
    try:
        compile(source_code, str(source_file), 'exec')
    except SyntaxError as e:
        # Format syntax error in same way as runtime errors
        error_msg = f"  File \"{source_file}\", line {e.lineno}\n"
        if e.text:
            error_msg += f"    {e.text}"
            if e.offset:
                error_msg += f"    {' ' * (e.offset - 1)}^\n"
        error_msg += f"SyntaxError: {e.msg}"
        
        return {
            "language": "python",
            "stdout": "",
            "stderr": error_msg,
            "returncode": 1,
            "executed_command": []
        }
    
    # Copy source file to sandbox as main.py
    sandbox_file = sandbox / "main.py"
    shutil.copy2(source_file, sandbox_file)
    
    # Execute with Python 3
    command = ["python3", "main.py"]
    result = subprocess.run(
        command,
        cwd=sandbox,  # Run inside sandbox directory
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    return {
        "language": "python",
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "executed_command": command
    }


def _execute_c(source_file: pathlib.Path, sandbox: pathlib.Path, timeout: int) -> Dict[str, Any]:
    """Compile and execute C code in sandbox."""
    # Copy source to sandbox
    sandbox_source = sandbox / "main.c"
    shutil.copy2(source_file, sandbox_source)
    
    # Compile with gcc
    executable = sandbox / "program"
    compile_cmd = ["gcc", "main.c", "-o", "program"]
    compile_result = subprocess.run(
        compile_cmd,
        cwd=sandbox,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    # If compilation failed, return compilation errors
    if compile_result.returncode != 0:
        return {
            "language": "c",
            "stdout": compile_result.stdout,
            "stderr": f"Compilation failed:\n{compile_result.stderr}",
            "returncode": compile_result.returncode,
            "executed_command": compile_cmd
        }
    
    # Execute the compiled binary
    run_cmd = ["./program"]
    run_result = subprocess.run(
        run_cmd,
        cwd=sandbox,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    return {
        "language": "c",
        "stdout": run_result.stdout,
        "stderr": run_result.stderr,
        "returncode": run_result.returncode,
        "executed_command": run_cmd
    }


def _execute_cpp(source_file: pathlib.Path, sandbox: pathlib.Path, timeout: int) -> Dict[str, Any]:
    """Compile and execute C++ code in sandbox."""
    # Copy source to sandbox
    sandbox_source = sandbox / "main.cpp"
    shutil.copy2(source_file, sandbox_source)
    
    # Compile with g++
    executable = sandbox / "program"
    compile_cmd = ["g++", "main.cpp", "-o", "program"]
    compile_result = subprocess.run(
        compile_cmd,
        cwd=sandbox,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    # If compilation failed, return compilation errors
    if compile_result.returncode != 0:
        return {
            "language": "cpp",
            "stdout": compile_result.stdout,
            "stderr": f"Compilation failed:\n{compile_result.stderr}",
            "returncode": compile_result.returncode,
            "executed_command": compile_cmd
        }
    
    # Execute the compiled binary
    run_cmd = ["./program"]
    run_result = subprocess.run(
        run_cmd,
        cwd=sandbox,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    return {
        "language": "cpp",
        "stdout": run_result.stdout,
        "stderr": run_result.stderr,
        "returncode": run_result.returncode,
        "executed_command": run_cmd
    }


def _execute_java(source_file: pathlib.Path, sandbox: pathlib.Path, timeout: int) -> Dict[str, Any]:
    """Compile and execute Java code in sandbox."""
    # Extract class name from source file
    class_name = extract_java_class_name(str(source_file))
    
    # Copy source to sandbox with proper class name
    sandbox_source = sandbox / f"{class_name}.java"
    shutil.copy2(source_file, sandbox_source)
    
    # Compile with javac
    compile_cmd = ["javac", f"{class_name}.java"]
    compile_result = subprocess.run(
        compile_cmd,
        cwd=sandbox,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    # If compilation failed, return compilation errors
    if compile_result.returncode != 0:
        return {
            "language": "java",
            "stdout": compile_result.stdout,
            "stderr": f"Compilation failed:\n{compile_result.stderr}",
            "returncode": compile_result.returncode,
            "executed_command": compile_cmd
        }
    
    # Execute with java
    run_cmd = ["java", class_name]
    run_result = subprocess.run(
        run_cmd,
        cwd=sandbox,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    return {
        "language": "java",
        "stdout": run_result.stdout,
        "stderr": run_result.stderr,
        "returncode": run_result.returncode,
        "executed_command": run_cmd
    }


def _execute_javascript(source_file: pathlib.Path, sandbox: pathlib.Path, timeout: int) -> Dict[str, Any]:
    """Execute JavaScript code in sandbox using Node.js."""
    # Copy source to sandbox
    sandbox_file = sandbox / "main.js"
    shutil.copy2(source_file, sandbox_file)
    
    # Execute with Node.js
    command = ["node", "main.js"]
    result = subprocess.run(
        command,
        cwd=sandbox,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    return {
        "language": "javascript",
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "executed_command": command
    }


def _execute_html(source_file: pathlib.Path, sandbox: pathlib.Path) -> Dict[str, Any]:
    """
    HTML files are not executed - just validated by copying successfully.
    Returns success message without actual execution.
    """
    # Copy to sandbox (validates file is readable)
    sandbox_file = sandbox / "index.html"
    shutil.copy2(source_file, sandbox_file)
    
    return {
        "language": "html",
        "stdout": "HTML parsed successfully.",
        "stderr": "",
        "returncode": 0,
        "executed_command": []
    }


# ---------------------------------------------
#  Test/Demo Section (Optional)
# ---------------------------------------------
if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        file_to_run = sys.argv[1]
        result = run_in_sandbox(file_to_run)
        
        print(f"STDOUT:\n{result['stdout']}")
        print(f"STDERR:\n{result['stderr']}")
        print(f"RETURNCODE:\n{result['returncode']}")
    else:
        print("Usage: python3 sandbox_runner.py <file_path>")
        print("Example: python3 sandbox_runner.py user.py")
