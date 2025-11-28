# 🧠 Deterministic Logical Error Detection Engine

## Overview

FixGoblin now includes a **deterministic, non-LLM logical error detection engine** that identifies algorithmic and logical bugs using rule-based static analysis techniques.

## Key Features

✅ **No AI/LLM Required** - Pure deterministic algorithms  
✅ **Multi-Language Support** - Python, Java, C++, JavaScript, Go  
✅ **AST Analysis** - Deep code structure understanding  
✅ **Control Flow Graphs** - Detects unreachable code & infinite loops  
✅ **Data Flow Analysis** - Tracks variable usage & initialization  
✅ **Test Case Integration** - Compares expected vs actual outputs  
✅ **High Confidence Scoring** - Each detection includes confidence level  

## Architecture

### Core Components

```
Backend/core/logical_analyzer.py     - Main analysis engine
Backend/core/test_case_validator.py  - Test execution & validation
```

### Analysis Techniques

#### 1. Abstract Syntax Tree (AST) Analysis
Parses code into tree structure to understand:
- Function definitions and calls
- Variable assignments and usage
- Control flow statements
- Expression evaluation

#### 2. Control Flow Graph (CFG)
Builds execution path graph to detect:
- **Unreachable code** - Statements that can never execute
- **Infinite loops** - Loops with no exit condition
- **Missing return paths** - Functions without proper returns
- **Dead code** - Code after unconditional returns/breaks

#### 3. Data Flow Analysis (DFA)
Tracks variable states through execution to find:
- **Uninitialized variables** - Used before defined
- **Unused variables** - Defined but never used
- **Variable shadowing** - Local vars hiding outer scope

#### 4. Pattern-Based Rules
Detects common logical errors:
- **Off-by-one errors** - Array bounds and loop ranges
- **Wrong comparisons** - Assignment in conditionals (= vs ==)
- **Incorrect operators** - + instead of -, * instead of /
- **Always true/false** - Conditions that never change
- **Missing breaks** - Fall-through in switch statements
- **Boundary errors** - Edge cases in loops and arrays

## Error Types Detected

| Error Type | Description | Severity | Example |
|------------|-------------|----------|---------|
| `INFINITE_LOOP` | Loop condition never changes | High | `while True:` without break |
| `UNREACHABLE_CODE` | Code after return/break | Medium | Code after `return` statement |
| `OFF_BY_ONE` | Array index or loop bound error | Medium | `range(1, len(arr))` with `arr[i]` |
| `WRONG_COMPARISON` | Assignment in condition | High | `if x = 5:` instead of `if x == 5:` |
| `MISSING_RETURN` | Function missing return | Critical | Non-void function with no return |
| `INCORRECT_BASE_CASE` | Recursion without base case | High | Recursive function always recurses |
| `UNINITIALIZED_VARIABLE` | Variable used before set | High | `print(x)` before `x = 10` |
| `ALWAYS_TRUE_FALSE` | Constant condition | Medium | `if 5 == 5:` always true |
| `BOUNDARY_ERROR` | Index out of bounds | High | Accessing beyond array length |
| `WRONG_OPERATOR` | Incorrect arithmetic operator | Medium | Using + when should be - |

## Usage

### 1. Command Line

```bash
# Basic usage (logical analysis enabled by default)
python fixgoblin.py your_code.py

# Disable logical analysis for faster execution
python fixgoblin.py your_code.py --disable-logical-analysis

# With test cases embedded in comments
python fixgoblin.py test_logical_analyzer_demo.py
```

### 2. Programmatic API

```python
from Backend.core.logical_analyzer import analyze_logic

code = """
def factorial(n):
    return n * factorial(n - 1)  # Missing base case!
"""

result = analyze_logic(code, language="python")

print(f"Found {len(result['logical_errors'])} errors:")
for error in result['logical_errors']:
    print(f"  Line {error['line']}: {error['message']}")
    print(f"  Suggested fix: {error['suggested_fix']}")
```

### 3. With Test Cases

```python
from Backend.core.test_case_validator import TestCase, TestCaseValidator

# Define test cases
test_cases = [
    TestCase(
        test_id=1,
        description="Factorial of 5",
        input_data=5,
        expected_output=120
    ),
    TestCase(
        test_id=2,
        description="Factorial of 0",
        input_data=0,
        expected_output=1
    )
]

# Run tests
validator = TestCaseValidator("python")
results = validator.run_tests(code, test_cases)

# Analyze failures
from Backend.core.logical_analyzer import analyze_logic

test_data = [r.to_dict() for r in results]
analysis = analyze_logic(code, "python", test_cases=test_data)
```

### 4. Embedded Test Cases

Add test cases directly in code comments:

```python
# TEST: Calculate sum
# INPUT: [1, 2, 3, 4, 5]
# EXPECTED: 15

def sum_array(arr):
    total = 0
    for i in range(1, len(arr)):  # BUG: Off-by-one!
        total += arr[i]
    return total
```

The analyzer automatically parses these and runs tests!

## Output Format

```json
{
  "logical_errors": [
    {
      "type": "infinite_loop",
      "line": 5,
      "column": 4,
      "message": "Potential infinite loop: variable 'i' never modified",
      "severity": "high",
      "confidence": 0.95,
      "suggested_fix": "Add 'i += 1' inside the loop"
    }
  ],
  "confidence_score": 0.87,
  "control_flow_issues": ["Unreachable code after line 10"],
  "data_flow_issues": ["Variable 'x' used before initialization"],
  "ast_valid": true
}
```

## Integration with FixGoblin

The logical analyzer is fully integrated into the autonomous repair loop:

1. **Code Execution** - Run code in sandbox
2. **Test Validation** - Execute test cases (if provided)
3. **Logical Analysis** - Run deterministic error detection
   - AST parsing and validation
   - CFG construction and traversal
   - DFA variable tracking
   - Pattern-based rule matching
4. **Error Reporting** - Display all detected issues
5. **Patch Generation** - Create fixes based on analysis
6. **Iterative Repair** - Apply fixes and re-validate

## Confidence Scoring

Each detected error includes a confidence score (0.0 - 1.0):

- **0.9 - 1.0**: High confidence (definitely an error)
- **0.7 - 0.9**: Medium-high confidence (very likely an error)
- **0.5 - 0.7**: Medium confidence (probably an error)
- **< 0.5**: Low confidence (might be intentional)

Confidence is calculated based on:
- Pattern specificity
- Context analysis
- Severity of issue
- Historical accuracy

## Language-Specific Features

### Python
- Full AST analysis with `ast` module
- CFG construction
- DFA with scope tracking
- Comprehensive error detection

### Java
- Regex-based pattern matching
- Common error detection (missing semicolons, braces)
- Type-related issues
- Assignment in conditionals

### C++
- Pointer analysis patterns
- Memory leak detection patterns
- Assignment vs comparison
- Missing return statements

### JavaScript
- `undefined` and `null` handling
- Async/await patterns
- Scope hoisting issues
- Type coercion errors

### Go
- Goroutine leak detection
- Channel patterns
- Error handling validation
- Defer usage patterns

## Limitations

⚠️ **Current Limitations:**

1. **Semantic Understanding**: Cannot detect errors requiring domain knowledge
   - Example: "This should calculate distance, not velocity"
   
2. **Complex Logic**: May miss errors in intricate algorithmic patterns
   - Example: Subtle mathematical formula errors
   
3. **Context-Dependent**: Cannot validate business logic correctness
   - Example: "Price should never be negative" (needs specification)
   
4. **Test Coverage**: Requires test cases for input/output validation
   - Without tests, only static analysis is performed

5. **Language Features**: Some advanced language features not fully supported
   - Metaprogramming, macros, reflection

## Future Enhancements

🚀 **Planned Features:**

- [ ] Symbolic execution for path exploration
- [ ] Constraint solving for boundary conditions
- [ ] Taint analysis for security issues
- [ ] Memory safety analysis (buffer overflows)
- [ ] Concurrency bug detection (race conditions)
- [ ] Performance anti-pattern detection
- [ ] Enhanced multi-language AST support
- [ ] Integration with external theorem provers

## Examples

### Example 1: Infinite Loop Detection

```python
# Before
def count_up():
    i = 0
    while i < 10:
        print(i)
        # Forgot to increment i

# Analysis Result
# ❌ Line 3: Infinite loop - variable 'i' never modified
# 💡 Suggested fix: Add 'i += 1' inside loop

# After (auto-fixed)
def count_up():
    i = 0
    while i < 10:
        print(i)
        i += 1
```

### Example 2: Off-By-One Error

```python
# Before
def sum_array(arr):
    total = 0
    for i in range(1, len(arr)):  # Starting at 1!
        total += arr[i]
    return total

# Analysis Result
# ❌ Line 3: Off-by-one error - range starts at 1
# 💡 Suggested fix: Use range(0, len(arr)) for 0-indexed arrays

# After (auto-fixed)
def sum_array(arr):
    total = 0
    for i in range(0, len(arr)):
        total += arr[i]
    return total
```

### Example 3: Missing Base Case

```python
# Before
def factorial(n):
    return n * factorial(n - 1)

# Analysis Result
# ❌ Line 2: Missing recursion base case
# 💡 Suggested fix: Add 'if n <= 1: return 1' at start

# After (auto-fixed)
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

## Comparison with Other Approaches

| Approach | Pros | Cons |
|----------|------|------|
| **FixGoblin Logical Analyzer** | ✅ Deterministic<br>✅ Fast<br>✅ No training needed<br>✅ Explainable | ❌ Limited to known patterns<br>❌ Can't understand intent |
| **LLM-based** | ✅ Understands context<br>✅ Flexible | ❌ Non-deterministic<br>❌ Expensive<br>❌ Requires API |
| **Static Analyzers (pylint, etc.)** | ✅ Fast<br>✅ Well-tested | ❌ Style-focused<br>❌ Limited logic detection |
| **Symbolic Execution** | ✅ Thorough path coverage | ❌ Very slow<br>❌ Path explosion |
| **Manual Code Review** | ✅ Understands intent | ❌ Time-consuming<br>❌ Not scalable |

## Best Practices

1. **Write Test Cases** - Embed expected inputs/outputs in comments
2. **Enable by Default** - Logical analysis adds minimal overhead
3. **Review Suggestions** - Not all detections are bugs (check confidence)
4. **Iterative Development** - Fix high-severity issues first
5. **Combine with Tests** - Use both unit tests and logical analysis

## Troubleshooting

**Q: Why aren't errors detected?**
A: Check that:
- Code is syntactically valid (parser must succeed)
- Language is correctly detected
- Logical analysis is enabled (default: yes)

**Q: Too many false positives?**
A: Adjust confidence threshold or disable specific rule types

**Q: Slow analysis?**
A: Use `--disable-logical-analysis` for quick runs, enable for final validation

## References

- AST Analysis: Python `ast` module documentation
- Control Flow Graphs: Compiler design textbooks
- Data Flow Analysis: Static analysis literature
- Pattern Detection: Software bug taxonomies

---

**Built by**: FixGoblin Team  
**Version**: 2.0  
**License**: MIT  
**Contributions**: Welcome! See GitHub issues
