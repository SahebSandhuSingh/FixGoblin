# FixGoblin - Autonomous Debugging System

## 🎯 Overview

FixGoblin is a complete autonomous debugging system that automatically detects, analyzes, and fixes bugs in Python code.

## 🏗️ Architecture

### 4-Step Pipeline

1. **Sandbox Execution** (`sandbox_runner.py`)
   - Safely executes code in isolated temporary directories
   - Supports: Python, C, C++, Java, JavaScript, HTML
   - Captures stdout, stderr, and return codes
   - 3-second timeout protection

2. **Error Analysis** (`error_parser.py`)
   - Parses error messages and stack traces
   - Extracts: error type, line number, message, faulty code snippet
   - Supports: SyntaxError, IndexError, NameError, ZeroDivisionError, etc.

3. **Patch Generation** (`patch_generator.py`)
   - Generates multiple fix candidates for detected errors
   - **Correctness Patches** (always generated):
     - IndexError: boundary checks, loop range fixes, offset removal
     - SyntaxError: operator fixes, missing colons, parentheses
     - NameError: typo correction, variable initialization
     - ZeroDivisionError: zero checks, try-except blocks
   - **Efficiency Patches** (optional, when `optimize_efficiency=True`):
     - Loop optimizations
     - Early exit conditions
     - Limited to max 2 patches

4. **Patch Optimization** (`patch_optimizer.py`)
   - Tests each patch in sandbox
   - Scores based on:
     - ✓ No errors: +50 points
     - ✓ Error reduction: +10 per error
     - ✗ New errors: -10 per error
     - ✓ Minimal changes: +5 points
   - Selects and applies best patch

## 🚀 Usage

### Basic Commands

```bash
# Analyze only (show patches but don't apply)
python3 fixgoblin.py user.py

# Analyze and automatically fix
python3 fixgoblin.py user.py --apply

# Include efficiency optimization patches
python3 fixgoblin.py user.py --optimize

# Fix with optimization
python3 fixgoblin.py user.py --apply --optimize
```

### Flags

- `--apply`, `-a` : Automatically apply the best patch
- `--optimize`, `-o` : Generate efficiency improvement patches (max 2)

## 📊 Example Output

```
🤖 AUTONOMOUS DEBUGGING SYSTEM - FixGoblin
======================================================================

STEP 1: SANDBOX EXECUTION
→ IndexError: list index out of range (Line 5)

STEP 2: ERROR ANALYSIS
→ Bug Type: IndexError
→ Faulty Code: if arr[j] > arr[j+1]:

STEP 3: PATCH GENERATION
→ Generated 5 patches:
  - 3 correctness patches
  - 2 efficiency patches (when --optimize used)

STEP 4: PATCH OPTIMIZATION
→ Testing patches...
→ Best: patch_2 (75 points)
→ Fix: Change range(0, n-i) to range(0, n-i-1)

✅ DEBUGGING COMPLETE - Bug Fixed!
```

## 🎓 Key Features

### Smart Patch Generation
- **Correctness First**: Always generates patches to fix the bug
- **Optional Optimization**: Only adds efficiency patches when user requests
- **Limited Scope**: Max 2 efficiency patches to avoid patch explosion

### Intelligent Scoring
- Prioritizes working solutions (return code 0)
- Penalizes new errors or changed error types
- Rewards minimal code changes
- Considers error reduction

### Safety Features
- All testing in temporary sandboxes
- Automatic backup creation (`.bak` files)
- Verification after applying patches
- No modification of original files during testing

---

**Built with ❤️ for autonomous debugging**