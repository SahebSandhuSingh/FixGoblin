# FixGoblin - Autonomous Debugging System

## 🎯 Overview

FixGoblin is a complete autonomous debugging system that automatically detects, analyzes, and fixes bugs in code through iterative self-repair. Detects both **runtime crashes** and **logical errors** (off-by-one bugs, missing returns, etc.).

**NEW:** Comprehensive final report generation with colored terminal output and JSON export!

## 📁 Project Structure

```
FixGoblin/
├── fixgoblin.py              # Main entry point
├── README.md                 # This file
│
└── backend/
    ├── core/                 # Core debugging modules
    │   ├── sandbox_runner.py
    │   ├── error_parser.py
    │   ├── patch_generator.py
    │   ├── patch_optimizer.py
    │   ├── autonomous_repair.py
    │   ├── logical_validator.py
    │   └── final_report.py   # ⭐ NEW: Report generation
    │
    ├── backups/              # Backup files (*.backup)
    ├── logs/                 # Repair logs (*.json)
    ├── docs/                 # Documentation
    ├── demos/                # Example scripts
    └── tests/                # Sample buggy code
```

## 🚀 Quick Start

```bash
# Run FixGoblin on any Python file
python fixgoblin.py backend/tests/your_code.py

# Save detailed repair log + final report
python fixgoblin.py backend/tests/your_code.py --log backend/logs/repair.json --final-report

# Limit repair iterations
python fixgoblin.py backend/tests/your_code.py --max-iterations 3

# Enable efficiency mode (faster, only correctness patches)
python fixgoblin.py backend/tests/your_code.py --efficiency
```

## 🏗️ Architecture

### 5-Step Pipeline

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
   - Enhanced Scoring System:
     - ✓ No errors: **+100 points** (working patches strongly favored)
     - ✓ Error reduction: **+20 per error** reduced
     - ✗ New errors: **-50 per error** introduced
     - ✓ Minimal changes: **+10 points** for small diffs
   - Selects and applies best patch with backup creation

5. **Autonomous Repair Loop** (`autonomous_repair.py`) ⭐ **NEW**
   - Iteratively fixes bugs until code works
   - Automatically applies best patches
   - Tracks repair progress across iterations
   - Stops when code executes successfully or max iterations reached
   - Generates detailed JSON logs of repair process

## 🚀 Usage

### Quick Start - Autonomous Repair (Recommended)

The autonomous repair loop automatically fixes multiple bugs iteratively:

```bash
# Automatic multi-bug repair (default: 5 iterations)
python3 autonomous_repair.py user.py

# With efficiency optimization
python3 autonomous_repair.py user.py --optimize

# Custom iteration limit
python3 autonomous_repair.py user.py --max-iterations 10

# Save repair log to JSON
python3 autonomous_repair.py user.py --log repair_log.json

# Quiet mode (summary only)
python3 autonomous_repair.py user.py --quiet
```

### Single-Pass Debugging (Legacy)

For single-bug analysis without iteration:

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

**Autonomous Repair (`fixgoblin.py`):**
- `--max-iterations N` : Maximum repair attempts (default: 5)
- `--optimize` : Generate efficiency improvement patches
- `--log FILE` : Save repair history to JSON file
- `--quiet` : Suppress detailed output
- `--final-report` : Generate comprehensive debugging report ⭐ NEW

**Legacy Single-Pass:**
- `--apply`, `-a` : Automatically apply the best patch
- `--optimize`, `-o` : Generate efficiency improvement patches (max 2)

## 📊 Example Output

### Final Report (NEW!) ⭐

```
================================================================================
🔍 FINAL DEBUGGING REPORT
================================================================================

📁 File: backend/tests/user.py
⏱️  Execution Time: 2.5s
🔄 Total Iterations: 3
📅 Generated: 2025-11-27T19:48:25

✅ Status: Fixed
   Success: True
   Final Status: success

🐛 Detected Error Types (2):
   - IndexError: list index out of range (Line 45)
   - TypeError: unsupported operand type(s)

🔧 Applied Patches (2):
   - Patch #1: Fixed IndexError (Score: 120)
   - Patch #2: Fixed TypeError (Score: 100)

📄 Code Changes:
   Original Lines: 50
   Final Lines: 52
   Lines Changed: 5

📊 Code Diff (Preview):
   --- original
   +++ patched
   @@ -42,7 +42,7 @@
    def process_list(items):
   -    return items[len(items)]  # BUG: IndexError
   +    return items[len(items)-1]  # FIXED

📄 Full report saved to: backend/logs/user_final_report.json
```

### Autonomous Repair Loop

```
🤖 AUTONOMOUS REPAIR LOOP - FixGoblin v2.0
================================================================================
📁 Target: multi_bug_test.py
🔄 Max Iterations: 5
⚡ Efficiency Mode: ENABLED

▶▶▶▶ ITERATION 1/5 ▶▶▶▶
🔬 Running code in sandbox...
❌ Execution failed with errors
🐛 Parsing error...
   Type: SyntaxError (Line 5)
   Message: expected ':'
🔧 Generating patches...
   Generated 1 patch candidate(s)
🏆 Selecting best patch...
   Selected: patch_2 (Score: -90)
💾 Applying patch to file...
   ✅ Applied: multi_bug_test.py.backup
📊 Status: RETRYING

▶▶▶▶ ITERATION 2/5 ▶▶▶▶
🔬 Running code in sandbox...
❌ Execution failed with errors
🐛 Parsing error...
   Type: IndexError (Line 11)
🏆 Selecting best patch...
   Selected: patch_1 (Score: -35)
💾 Applying patch to file...
📊 Status: RETRYING

▶▶▶▶ ITERATION 3/5 ▶▶▶▶
🔬 Running code in sandbox...
❌ Execution failed with errors
🐛 Parsing error...
   Type: NameError (Line 20)
🏆 Selecting best patch...
   Selected: patch_1 (Score: 150)
💾 Applying patch to file...
📊 Status: FIXED

▶▶▶▶ ITERATION 4/5 ▶▶▶▶
🔬 Running code in sandbox...
✅ CODE RUNS SUCCESSFULLY!

📋 REPAIR SUMMARY
================================================================================
🎯 Final Status: SUCCESS
✅ Success: True
🔄 Total Iterations: 4
📝 Reason: Code successfully repaired and executes without errors

📊 ITERATION HISTORY:
🔄 Iteration 1: SyntaxError → patch_2 (-90 pts) → RETRYING
🔄 Iteration 2: IndexError → patch_1 (-35 pts) → RETRYING
✅ Iteration 3: NameError → patch_1 (150 pts) → FIXED
✅ Iteration 4: Verification passed
```

## 🎓 Key Features

### Final Report Generation ⭐ NEW
- **Terminal Output**: Colored, human-readable report with emojis
- **JSON Export**: Machine-readable logs for CI/CD integration
- **Code Diff**: Unified diff showing all changes (colored +/-)
- **Comprehensive Data**: Status, errors, patches, execution time
- **See**: [FINAL_REPORT.md](backend/docs/FINAL_REPORT.md) for detailed guide

### Iterative Self-Repair ⭐
- **Automatic Iteration**: Fixes bugs one-by-one until code works
- **Progress Tracking**: Detailed logs for each repair iteration
- **Max Iterations**: Safety limit prevents infinite loops (default: 5)
- **JSON Export**: Complete repair history saved to file
- **Multi-Bug Support**: Handles files with sequential bugs

### Smart Patch Generation
- **Correctness First**: Always generates patches to fix the bug
- **Optional Optimization**: Only adds efficiency patches when user requests
- **Limited Scope**: Max 2 efficiency patches to avoid patch explosion

### Enhanced Scoring System
- **Strong Success Reward**: +100 for working patches (vs +50 before)
- **Error Reduction Bonus**: +20 per error reduced (vs +10 before)
- **Harsh Failure Penalty**: -50 per new error (vs -10 before)
- **Minimal Changes**: Rewards small, targeted fixes

### Safety Features
- All testing in temporary sandboxes
- Automatic backup creation (`.backup` files)
- Verification after applying patches
- No modification of original files during testing
- Max iteration limit prevents infinite loops

## 📁 Project Structure

```
FixGoblin/
├── sandbox_runner.py         # Step 1: Isolated code execution
├── error_parser.py            # Step 2: Error extraction & analysis
├── patch_generator.py         # Step 3: Fix candidate generation
├── patch_optimizer.py         # Step 4: Patch testing & selection
├── autonomous_repair.py       # Step 5: Iterative repair loop ⭐ NEW
├── fixgoblin.py              # Legacy single-pass interface
├── user.py                    # Test file (buggy bubble sort)
├── multi_bug_test.py         # Multi-bug test case
└── README.md                  # Documentation
```

## 🧪 Test Examples

### Single Bug Fix
```bash
python3 autonomous_repair.py user.py
# Fixes IndexError in bubble sort (1-2 iterations)
```

### Multiple Bug Fix
```bash
python3 autonomous_repair.py multi_bug_test.py --log repair.json
# Fixes SyntaxError → IndexError → NameError (3-4 iterations)
```

### With Optimization
```bash
python3 autonomous_repair.py user.py --optimize
# Generates correctness + efficiency patches
```

---

**Built with ❤️ for autonomous debugging**