# Multi-Language Sandbox & Compiler Engine

A secure, isolated execution environment for running code in 6 programming languages: **Python**, **JavaScript**, **C**, **C++**, **Java**, and **Go**.

## 🚀 Features

- **6 Language Support**: Python, JavaScript (Node.js), C, C++, Java, Go
- **Syntax Validation**: Pre-execution syntax checking where possible
- **Secure Sandbox**: Time limits, memory limits, process isolation
- **Comprehensive Error Parsing**: Structured error output with line numbers
- **No Docker Required**: Uses subprocess + OS-level restrictions
- **Production Ready**: Battle-tested with proper error handling

## 📦 Installation

### Prerequisites

Make sure you have the required compilers/interpreters installed:

```bash
# Python (usually pre-installed)
python3 --version

# JavaScript (Node.js)
node --version

# C Compiler
gcc --version

# C++ Compiler
g++ --version

# Java
javac --version
java --version

# Go
go version
```

### Install Missing Languages

**macOS:**
```bash
# Node.js
brew install node

# GCC/G++
xcode-select --install

# Java
brew install openjdk

# Go
brew install go
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install nodejs gcc g++ default-jdk golang
```

## 🎯 Quick Start

### Basic Usage

```python
from Backend.core.multi_language_sandbox import compile_and_run

# Execute Python code
result = compile_and_run("print('Hello World!')", "python")
print(result['output'])  # Hello World!

# Execute JavaScript
result = compile_and_run("console.log('Hello from JS');", "javascript")

# Execute C
c_code = """
#include <stdio.h>
int main() {
    printf("Hello from C!\\n");
    return 0;
}
"""
result = compile_and_run(c_code, "c")
```

### Return Value Structure

```python
{
    "success": bool,           # True if execution succeeded
    "output": str,             # Standard output (stdout)
    "error": str,              # Error message if any
    "error_type": str,         # SyntaxError, RuntimeError, etc.
    "line_number": int | None, # Line where error occurred
    "execution_time": float    # Execution time in seconds
}
```

## 🔒 Security Features

### Resource Limits

- **Time Limit**: 5 seconds per execution (configurable)
- **Memory Limit**: 512 MB (configurable)
- **CPU Priority**: Low (nice +10)
- **Core Dumps**: Disabled

### Isolation

- Temporary file execution only
- Automatic cleanup after execution
- No persistent file system access
- Process-level isolation

### Configuration

Edit these constants in `multi_language_sandbox.py`:

```python
TIMEOUT_SECONDS = 5      # Maximum execution time
MEMORY_LIMIT_MB = 512    # Maximum memory usage
```

## 📝 Language-Specific Details

### Python
- **Syntax Check**: `compile()` built-in
- **Execution**: subprocess with python3
- **Features**: Full Python 3.x support

### JavaScript (Node.js)
- **Syntax Check**: `node --check`
- **Execution**: `node` runtime
- **Features**: ES6+ support

### C
- **Compiler**: GCC with `-std=c11 -Wall`
- **Process**: Compile → Execute binary
- **Features**: C11 standard

### C++
- **Compiler**: G++ with `-std=c++17 -Wall`
- **Process**: Compile → Execute binary
- **Features**: C++17 standard

### Java
- **Compiler**: `javac`
- **Execution**: `java` with automatic class detection
- **Features**: Auto-extracts public class name

### Go
- **Compiler**: `go build`
- **Process**: Compile → Execute binary
- **Features**: Modern Go support

## 🔧 API Reference

### `compile_and_run(code: str, language: str) -> dict`

Main function to compile and execute code.

**Parameters:**
- `code` (str): Source code to execute
- `language` (str): One of: `python`, `javascript`, `c`, `cpp`, `java`, `go`

**Returns:** Dictionary with execution results

**Example:**
```python
result = compile_and_run("print(1 + 1)", "python")
if result['success']:
    print(f"Output: {result['output']}")
else:
    print(f"Error: {result['error_type']} at line {result['line_number']}")
```

### `map_error_type(stderr: str, language: str) -> tuple`

Parse error messages to extract structured information.

**Parameters:**
- `stderr` (str): Standard error output
- `language` (str): Programming language

**Returns:** Tuple of `(error_type: str, line_number: int | None)`

**Example:**
```python
error_type, line_num = map_error_type("SyntaxError: line 5", "python")
# Returns: ("SyntaxError", 5)
```

### `get_supported_languages() -> list`

Get list of all supported languages.

**Returns:** `['python', 'javascript', 'c', 'cpp', 'java', 'go']`

### `get_language_info() -> dict`

Get detailed information about language availability.

**Returns:**
```python
{
    'python': {
        'available': True,
        'extension': '.py',
        'compiler': 'python3'
    },
    # ... etc for all languages
}
```

## 📊 Usage Examples

### Example 1: Detect Syntax Errors

```python
from Backend.core.multi_language_sandbox import compile_and_run

code = """
if x = 5:
    print(x)
"""

result = compile_and_run(code, "python")

print(f"Success: {result['success']}")           # False
print(f"Error Type: {result['error_type']}")     # SyntaxError
print(f"Line: {result['line_number']}")          # 1
print(f"Message: {result['error']}")             # invalid syntax...
```

### Example 2: Multi-Language Testing

```python
languages = ['python', 'javascript', 'go']
code_samples = {
    'python': 'print("Hello")',
    'javascript': 'console.log("Hello");',
    'go': 'package main\nimport "fmt"\nfunc main() { fmt.Println("Hello") }'
}

for lang in languages:
    result = compile_and_run(code_samples[lang], lang)
    print(f"{lang}: {result['output'].strip()}")
```

### Example 3: Handle Timeouts

```python
# Infinite loop
code = "while True: pass"
result = compile_and_run(code, "python")

if result['error_type'] == 'TimeoutError':
    print(f"Execution timed out: {result['error']}")
```

### Example 4: Compile C with Error Detection

```python
c_code = """
#include <stdio.h>
int main() {
    printf("Hello"  // Missing closing paren and semicolon
    return 0;
}
"""

result = compile_and_run(c_code, "c")

if not result['success']:
    print(f"Compile Error at line {result['line_number']}")
    print(result['error'])
```

## 🧪 Testing

Run the built-in test suite:

```bash
python3 Backend/core/multi_language_sandbox.py
```

Run the comprehensive demo:

```bash
python3 demo_multi_language.py
```

## 🔍 Error Types by Language

### Python
- `SyntaxError`, `IndentationError`, `NameError`, `TypeError`, `IndexError`, `ValueError`, `KeyError`, `AttributeError`, `ZeroDivisionError`

### JavaScript
- `SyntaxError`, `ReferenceError`, `TypeError`, `RangeError`

### C/C++
- `SyntaxError`, `CompileError`, `LinkError`, `SegmentationFault`

### Java
- `CompileError`, `NullPointerException`, `ArrayIndexOutOfBoundsException`, `ClassNotFoundException`, `RuntimeException`

### Go
- `SyntaxError`, `UndefinedError`, `PanicError`, `CompileError`

## 🎨 Integration with FixGoblin

The multi-language sandbox is designed to integrate seamlessly with FixGoblin's repair system:

```python
from Backend.core.multi_language_sandbox import compile_and_run
from Backend.core.autonomous_repair import autonomous_repair

# 1. Run code and detect errors
result = compile_and_run(code, language)

# 2. If error detected, attempt repair
if not result['success']:
    # Use FixGoblin's repair system (Python only for now)
    if language == "python":
        repaired = autonomous_repair(file_path)
    else:
        # Future: implement repair for other languages
        print(f"Manual repair needed for {language}")
```

## 🛣️ Roadmap

- [ ] Add support for Rust, Ruby, PHP
- [ ] Implement auto-repair for C/C++/Java syntax errors
- [ ] Add static analysis integration
- [ ] Network isolation improvements
- [ ] Docker-based sandboxing option
- [ ] Real-time execution monitoring
- [ ] Resource usage analytics

## ⚠️ Limitations

1. **Platform Specific**: Resource limits work best on Unix/Linux systems
2. **Compiler Required**: Each language needs its compiler/interpreter installed
3. **No Network**: Sandbox blocks network access
4. **File System**: Limited to temp files only
5. **Single Threaded**: No parallel execution support yet

## 🤝 Contributing

To add support for a new language:

1. Add language config to `SUPPORTED_LANGUAGES`
2. Implement `_run_<language>(code: str) -> Dict` function
3. Add error patterns to `map_error_type()`
4. Add test cases
5. Update documentation

## 📄 License

MIT License - See LICENSE file for details

## 🙋 Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review test cases for examples

---

**Built with ❤️ by the FixGoblin Team**
