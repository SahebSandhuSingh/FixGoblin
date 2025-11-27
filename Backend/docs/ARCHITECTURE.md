# FixGoblin - System Architecture Summary

## 🎯 Complete 5-Step Autonomous Repair System

### Overview
FixGoblin is a fully autonomous debugging system that iteratively repairs buggy code until it executes successfully. It combines sandbox execution, error parsing, patch generation, intelligent optimization, and iterative repair loops.

---

## 📋 Core Components

### Step 1: Sandbox Runner (`sandbox_runner.py`)
**Purpose**: Safe code execution in isolated environments

**Key Function**: `run_in_sandbox(file_path, timeout=3)`

**Features**:
- Multi-language support (Python, C, C++, Java, JavaScript, HTML)
- Automatic language detection by file extension
- Isolated temporary directory execution
- Timeout protection (3 seconds)
- Captures: stdout, stderr, returncode, language, command

**Return Format**:
```python
{
    "stdout": "...",
    "stderr": "...",
    "returncode": 0/1,
    "language": "python",
    "executed_command": "python3 main.py"
}
```

---

### Step 2: Error Parser (`error_parser.py`)
**Purpose**: Extract structured information from error messages

**Key Function**: `parse_error(sandbox_result, user_code)`

**Features**:
- Parses SyntaxError, RuntimeError, IndexError, NameError, etc.
- Extracts line numbers from tracebacks
- Identifies faulty code snippets
- Provides context for patch generation

**Return Format**:
```python
{
    "error_type": "IndexError",
    "line_number": 5,
    "error_message": "list index out of range",
    "faulty_snippet": "if arr[j] > arr[j+1]:",
    "defined_variables": ["arr", "n", "i", "j"]
}
```

---

### Step 3: Patch Generator (`patch_generator.py`)
**Purpose**: Generate multiple fix candidates

**Key Function**: `generate_patch_candidates(error_data, user_code, optimize_efficiency=False)`

**Patch Types**:

**Correctness Patches** (always generated):
- **IndexError**: 
  - Boundary checks: `if i < len(arr):`
  - Loop range fixes: `range(0, n-i-1)` instead of `range(0, n-i)`
  - Offset removal: `arr[j]` instead of `arr[j+1]`
  
- **SyntaxError**:
  - Missing colons: `if condition:` instead of `if condition`
  - Operator fixes: `==` instead of `=`
  - Missing parentheses
  
- **NameError**:
  - Variable initialization: `count = None`
  - Typo correction (Levenshtein distance)
  
- **ZeroDivisionError**:
  - Zero checks: `if denominator != 0:`
  - Try-except blocks

**Efficiency Patches** (optional, max 2):
- Loop optimizations
- Early exit conditions
- Only generated when `optimize_efficiency=True`

**Return Format**:
```python
[
    {
        "id": "patch_1",
        "description": "Add boundary check before array access",
        "patched_code": "...",
        "diff": "...",
        "patch_type": "correctness"
    },
    ...
]
```

---

### Step 4: Patch Optimizer (`patch_optimizer.py`)
**Purpose**: Test patches and select the best one

**Key Functions**: 
- `select_best_patch(patches, original_code, run_in_sandbox)`
- `apply_patch_to_file(best_patch, file_path, auto_apply=True)`

**Enhanced Scoring System**:
- ✅ **No errors** (returncode 0): **+100 points**
- ✅ **Error reduction**: **+20 points per error** reduced
- ❌ **New errors**: **-50 points per error** introduced
- ✅ **Minimal changes**: **+10 points** for small diffs
- ❌ **Large diffs**: **-10 points per extra line**

**Scoring Example**:
```
Patch 1: SyntaxError → IndexError
   - Reduced 1 error: +20
   - Changed error type: -50
   - Score: -30 ❌

Patch 2: All errors fixed
   - No errors: +100
   - Reduced 2 errors: +40
   - Minimal change: +10
   - Score: 150 ✅ WINNER
```

**File Application**:
- `auto_apply=False`: Returns patched code only, **never modifies files**
- `auto_apply=True`: Writes patch and creates `.backup` file
- Safety: Never runs during optimization loop

---

### Step 5: Autonomous Repair Loop (`autonomous_repair.py`) ⭐
**Purpose**: Iteratively fix bugs until code works

**Key Function**: `autonomous_repair(file_path, max_iterations=5, optimize_efficiency=False)`

**Algorithm**:
```
1. Load code from file
2. Run in sandbox
3. If returncode == 0:
      → SUCCESS - Stop loop
4. If error:
      → Parse error
      → Generate patches
      → Select best patch
      → Apply patch to file
      → Log iteration
5. Repeat until fixed or max_iterations reached
```

**Iteration Logging**:
```python
{
    "iteration": 1,
    "error_type": "IndexError",
    "line_number": 5,
    "error_message": "list index out of range",
    "selected_patch_id": "patch_2",
    "description": "Adjust loop range",
    "patch_score": 150,
    "status": "fixed",  # or "retrying" or "failed"
    "returncode": 1,
    "backup_path": "user.py.backup"
}
```

**Return Format**:
```python
{
    "success": True,
    "final_code": "...",
    "iterations": [...],
    "total_iterations": 2,
    "final_status": "success",  # or "failed" or "max_iterations_reached"
    "reason": "Code successfully repaired and executes without errors"
}
```

---

## 🚀 Usage Examples

### Basic Repair
```bash
# Fix single or multiple bugs automatically
python3 autonomous_repair.py user.py

# Output:
# Iteration 1: SyntaxError → Fixed
# Iteration 2: IndexError → Fixed
# Iteration 3: Code runs successfully ✅
```

### With Optimization
```bash
python3 autonomous_repair.py user.py --optimize
# Generates correctness + efficiency patches
```

### Custom Iterations
```bash
python3 autonomous_repair.py user.py --max-iterations 10
# Allow up to 10 repair attempts
```

### JSON Export
```bash
python3 autonomous_repair.py user.py --log repair.json
# Save complete repair history
```

---

## 🎓 Real-World Example

**Input**: `multi_bug_test.py` with 3 bugs
```python
def calculate_average(numbers):
    if len(numbers) == 0  # Bug 1: Missing colon
        return 0
    total = 0
    for i in range(len(numbers) + 1):  # Bug 2: Off-by-one error
        total += numbers[i]
    return total / len(numbers)

result = calculate_average([10, 20, 30])
print(f"Count: {count}")  # Bug 3: Undefined variable
```

**Repair Process**:
```
Iteration 1: SyntaxError (missing colon)
   → Applied patch_2: Add colon
   → Status: RETRYING (score: -90)

Iteration 2: IndexError (array out of bounds)
   → Applied patch_1: Boundary check
   → Status: RETRYING (score: -35)

Iteration 3: NameError (undefined variable)
   → Applied patch_1: Initialize count = None
   → Status: FIXED (score: 150)

Iteration 4: Verification
   → Code runs successfully ✅
```

**Output**: `multi_bug_test.py` (fixed)
```python
def calculate_average(numbers):
    if len(numbers) == 0:  # ✅ Fixed
        return 0
    total = 0
    for i in range(len(numbers) + 1):
        if i < len(numbers):  # ✅ Fixed
            total += numbers[i]
    return total / len(numbers)

result = calculate_average([10, 20, 30])
count = None  # ✅ Fixed
print(f"Count: {count}")
```

---

## 🛡️ Safety Features

1. **Sandbox Isolation**: All code execution in temporary directories
2. **Automatic Backups**: `.backup` files created before any modification
3. **Max Iterations**: Prevents infinite loops (default: 5)
4. **No-Modify Testing**: Patches evaluated in-memory during optimization
5. **Timeout Protection**: 3-second execution limit
6. **Verification**: Code re-run after patching to confirm fix

---

## 📊 Performance Characteristics

- **Single bugs**: Typically fixed in **1-2 iterations**
- **Multiple bugs**: Fixed sequentially, **1 bug per iteration**
- **Success rate**: High for common error types (IndexError, SyntaxError, NameError)
- **Speed**: Fast - each iteration takes ~1-3 seconds
- **Scalability**: Handles files with multiple sequential bugs

---

## 🔮 Future Enhancements

- [ ] Machine learning for patch ranking
- [ ] Support for more languages (Ruby, Go, Rust)
- [ ] Semantic equivalence checking
- [ ] Test suite integration
- [ ] IDE plugin support
- [ ] Cloud-based repair service

---

**Built with ❤️ for autonomous debugging**
